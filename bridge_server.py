#!/usr/bin/env python3
"""LIBERO Direct-EEF bridge for Codex / GPT-6 Astra.

Keeps one OffScreenRenderEnv alive and exposes a small HTTP API:
  GET  /status
  POST /move   JSON {x,y,z,gripper,note}  (unnamed dims hold current)
  POST /give_up JSON {reason}

Observations written to obs/ for the agent to read as files.
Every control step is archived as 7-D OSC action + RGB in run_dir/ctrl/ and steps.jsonl.
No object poses, names, or reward internals are returned to the planner.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

os.environ.setdefault("MUJOCO_GL", "egl")
os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
OBS_DIR = ROOT / "obs"
RUN_DIR = Path(os.environ.get("LIBERO_RUN_DIR", str(ROOT / "runs" / "current")))
HOST = os.environ.get("LIBERO_BRIDGE_HOST", "127.0.0.1")
PORT = int(os.environ.get("LIBERO_BRIDGE_PORT", "8765"))

SUITE = os.environ.get("LIBERO_SUITE", "libero_spatial")
TASK_ID = int(os.environ.get("LIBERO_TASK_ID", "0"))
INIT_ID = int(os.environ.get("LIBERO_INIT_ID", "0"))
MAX_ENV_STEPS = int(os.environ.get("LIBERO_MAX_ENV_STEPS", "600"))
MAX_MOVES = int(os.environ.get("LIBERO_MAX_MOVES", "30"))
CAMERA_SIZE = int(os.environ.get("LIBERO_CAMERA_SIZE", "256"))
REPLAY_STEPS = os.environ.get("LIBERO_REPLAY_STEPS", "").strip()


def _env_flag(name: str, default: bool = False) -> bool:
    v = os.environ.get(name, "").strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off"):
        return False
    return default


# Translucent world XYZ triad on agentview and wrist. Off by default; set at episode start.
WORLD_AXES = _env_flag("LIBERO_WORLD_AXES")
WORLD_AXES_CAMERAS = {
    "agentview": "agentview",
    "wrist": "robot0_eye_in_hand",
}
# Always save PNG as img[::-1, ::-1]. Agentview: arm at top, table at bottom.
# Wrist: pads at bottom. Matches OpenVLA / π0 LIBERO eval.

# OSC_POSE: action in [-1,1] maps to 0.05 m / 0.5 rad per control step.
POS_SCALE = 0.05
ORI_SCALE = 0.5
# robosuite Panda: +1 closes, -1 opens (verified on this machine).
GRIP_OPEN = -1.0
GRIP_CLOSE = 1.0

import robosuite.utils.transform_utils as T
from viz_world_axes import camera_pose_from_sim, overlay_world_axes_bgr


class Episode:
    def __init__(self):
        self.lock = threading.Lock()
        self.env = None
        self.instruction = None
        self.task_name = None
        self.obs = None
        self.env_steps = 0
        self.moves = 0
        self.success = False
        self.terminated = False
        self.termination_reason = None
        self.transcript = []
        self.started_at = time.time()
        self.q_home = None
        self.last_feedback = "reset"
        self.last_g_cmd = 1.0  # analog open-fraction is not a holdable command

    def start(self):
        from libero.libero import benchmark, get_libero_path
        from libero.libero.envs import OffScreenRenderEnv

        suite = benchmark.get_benchmark_dict()[SUITE]()
        task = suite.get_task(TASK_ID)
        bddl = os.path.join(
            get_libero_path("bddl_files"), task.problem_folder, task.bddl_file
        )
        self.instruction = task.language
        self.task_name = task.name
        self.env = OffScreenRenderEnv(
            bddl_file_name=bddl,
            camera_heights=CAMERA_SIZE,
            camera_widths=CAMERA_SIZE,
            has_offscreen_renderer=True,
            use_camera_obs=True,
        )
        self.env.seed(0)
        self.env.reset()
        inits = suite.get_task_init_states(TASK_ID)
        init_id = min(INIT_ID, len(inits) - 1)
        self.obs = self.env.set_init_state(inits[init_id])
        dummy = np.zeros(7, dtype=np.float32)
        for i in range(5):
            self._apply_action(dummy, kind="dummy", move_id=0, interp_i=i)
        self.q_home = self.obs["robot0_eef_quat"].astype(np.float64).copy()
        n_replay = 0
        if REPLAY_STEPS:
            rpath = Path(REPLAY_STEPS)
            recs = [
                json.loads(l)
                for l in rpath.read_text().splitlines()
                if l.strip()
            ]
            for rec in recs:
                if int(rec.get("env_step") or 0) <= 5:
                    continue
                act = np.asarray(rec["action"], dtype=np.float32)
                self.last_g_cmd = 0.0 if float(act[6]) > 0 else 1.0
                self._apply_action(
                    act,
                    kind="replay",
                    move_id=int(rec.get("move_id") or 0),
                    interp_i=int(rec.get("interp_i") or 0),
                    save_images=False,
                )
                n_replay += 1
            self.last_feedback = (
                f"resume: replayed {n_replay} ctrl steps from {rpath.name}; "
                "same physics pose as the source run, remaining_moves is a fresh budget"
            )
        else:
            self.last_feedback = (
                "reset: cameras live, jaws at home (pitch=roll=yaw=0)"
            )
        self._dump_obs()
        self._log(
            {
                "event": "reset" if not n_replay else "resume",
                "suite": SUITE,
                "task_id": TASK_ID,
                "init_id": init_id,
                "n_init": int(len(inits)),
                "instruction": self.instruction,
                "task_name": self.task_name,
                "replay_steps": n_replay,
                "replay_from": REPLAY_STEPS or None,
                "world_axes_overlay": WORLD_AXES,
                "state": self._state(),
            }
        )

    def _rpy_deg(self, quat=None):
        """Roll/pitch/yaw in degrees relative to the reset downward pose."""
        q = self.obs["robot0_eef_quat"] if quat is None else quat
        R_cur = T.quat2mat(q)
        R_home = T.quat2mat(self.q_home if self.q_home is not None else q)
        R_rel = R_home.T.dot(R_cur)
        rpy = T.mat2euler(R_rel)
        return [round(float(np.degrees(a)), 1) for a in rpy]

    def _quat_from_rpy_deg(self, roll_deg, pitch_deg, yaw_deg):
        rpy = np.radians([roll_deg, pitch_deg, yaw_deg], dtype=np.float64)
        R_rel = T.euler2mat(rpy)
        R_home = T.quat2mat(self.q_home)
        return T.mat2quat(R_home.dot(R_rel))

    def _state(self):
        o = self.obs
        grip = o["robot0_gripper_qpos"]
        # Panda: ~0.04 span open, ~0 closed. Map to [0,1] open.
        width = float(abs(grip[0]) + abs(grip[1]))
        open_frac = float(np.clip(width / 0.08, 0.0, 1.0))
        roll, pitch, yaw = self._rpy_deg()
        return {
            "eef_x": round(float(o["robot0_eef_pos"][0]), 4),
            "eef_y": round(float(o["robot0_eef_pos"][1]), 4),
            "eef_z": round(float(o["robot0_eef_pos"][2]), 4),
            "roll_deg": roll,
            "pitch_deg": pitch,
            "yaw_deg": yaw,
            "eef_quat": [round(float(q), 4) for q in o["robot0_eef_quat"]],
            "gripper_open": round(open_frac, 3),
            "feedback": self.last_feedback,
            "env_steps": self.env_steps,
            "moves": self.moves,
            "remaining_env_steps": MAX_ENV_STEPS - self.env_steps,
            "remaining_moves": MAX_MOVES - self.moves,
            "success": bool(self.success),
            "terminated": bool(self.terminated),
            "world_axes_overlay": bool(WORLD_AXES),
        }

    def _bgr_cams(self):
        out = {}
        for key, name in (
            ("agentview_image", "agentview"),
            ("robot0_eye_in_hand_image", "wrist"),
        ):
            img = self.obs[key]
            if img.dtype != np.uint8:
                img = np.clip(img, 0, 255).astype(np.uint8)
            img = img[::-1, ::-1]
            bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            if WORLD_AXES and name in WORLD_AXES_CAMERAS:
                bgr = self._overlay_world_axes(bgr, name)
            out[name] = bgr
        return out

    def _overlay_world_axes(self, bgr, view_name):
        """PNG-only overlay. Does not add geoms to the MuJoCo scene.

        Wrist pose is re-read every frame; the camera moves with the gripper.
        """
        cam_name = WORLD_AXES_CAMERAS[view_name]
        pose, fovy = camera_pose_from_sim(self.env.sim, cam_name)
        return overlay_world_axes_bgr(
            bgr,
            pose,
            fovy,
            alpha=0.5,
            legend=False,
        )

    def _write_named_pngs(self, directory, prefix, cams=None):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        cams = self._bgr_cams() if cams is None else cams
        paths = {}
        for name, bgr in cams.items():
            path = directory / f"{prefix}_{name}.png"
            cv2.imwrite(str(path), bgr)
            paths[name] = path
        return paths

    def _apply_action(self, action, *, kind, move_id, interp_i, target=None, save_images=True):
        """One OSC control step: env.step, then archive action + RGB."""
        action = np.asarray(action, dtype=np.float32).reshape(7)
        self.obs, _, _, _ = self.env.step(action)
        self.env_steps += 1
        prefix = f"{self.env_steps:04d}"
        if save_images:
            self._write_named_pngs(RUN_DIR / "ctrl", prefix)
        st = self._state()
        pos = self.obs["robot0_eef_pos"].astype(np.float64)
        dist = None if target is None else float(np.linalg.norm(target - pos))
        rec = {
            "event": "ctrl",
            "env_step": self.env_steps,
            "move_id": move_id,
            "interp_i": interp_i,
            "kind": kind,
            "action": [round(float(x), 5) for x in action],
            "eef": [st["eef_x"], st["eef_y"], st["eef_z"]],
            "rpy_deg": [st["roll_deg"], st["pitch_deg"], st["yaw_deg"]],
            "gripper_open": st["gripper_open"],
            "dist_m": None if dist is None else round(dist, 4),
            "success": bool(self.env.check_success()),
            "agentview": f"ctrl/{prefix}_agentview.png",
            "wrist": f"ctrl/{prefix}_wrist.png",
        }
        RUN_DIR.mkdir(parents=True, exist_ok=True)
        with open(RUN_DIR / "steps.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")
        return rec

    def _dump_obs(self):
        OBS_DIR.mkdir(parents=True, exist_ok=True)
        RUN_DIR.mkdir(parents=True, exist_ok=True)
        cams = self._bgr_cams()
        for name, bgr in cams.items():
            cv2.imwrite(str(OBS_DIR / f"{name}.png"), bgr)
        self._write_named_pngs(RUN_DIR / "frames", f"{self.env_steps:04d}", cams)
        payload = {
            "instruction": self.instruction,
            "task_name": self.task_name,
            "suite": SUITE,
            "task_id": TASK_ID,
            "init_id": INIT_ID,
            "cameras": {
                "agentview": str(OBS_DIR / "agentview.png"),
                "wrist": str(OBS_DIR / "wrist.png"),
            },
            **self._state(),
        }
        (OBS_DIR / "state.json").write_text(json.dumps(payload, indent=2))
        (RUN_DIR / "status.json").write_text(json.dumps(payload, indent=2))
        return payload

    def _log(self, rec):
        rec = dict(rec)
        rec["t"] = time.time()
        self.transcript.append(rec)
        RUN_DIR.mkdir(parents=True, exist_ok=True)
        with open(RUN_DIR / "transcript.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")

    def _finish(self, reason):
        self.terminated = True
        self.termination_reason = reason
        self.success = bool(self.env.check_success()) if self.env is not None else False
        result = {
            "success": self.success,
            "reason": reason,
            "instruction": self.instruction,
            "task_name": self.task_name,
            "suite": SUITE,
            "task_id": TASK_ID,
            "init_id": INIT_ID,
            "env_steps": self.env_steps,
            "moves": self.moves,
            "elapsed_s": round(time.time() - self.started_at, 2),
            "final_state": self._state(),
        }
        (RUN_DIR / "result.json").write_text(json.dumps(result, indent=2))
        (OBS_DIR / "result.json").write_text(json.dumps(result, indent=2))
        self._log({"event": "done", **result})
        return result

    def move(self, body):
        if self.terminated:
            return {"error": "episode already terminated", **self._dump_obs()}
        if self.moves >= MAX_MOVES:
            return self._finish("max_moves")
        if self.env_steps >= MAX_ENV_STEPS:
            return self._finish("max_env_steps")

        cur = self.obs["robot0_eef_pos"].astype(np.float64).copy()
        target = cur.copy()
        named = {}
        for i, axis in enumerate(("x", "y", "z")):
            if axis in body and body[axis] is not None:
                target[i] = float(body[axis])
                named[axis] = float(body[axis])
            elif f"d{axis}" in body and body[f"d{axis}"] is not None:
                target[i] = cur[i] + float(body[f"d{axis}"])
                named[f"d{axis}"] = float(body[f"d{axis}"])

        cur_rpy = self._rpy_deg()
        tgt_rpy = list(cur_rpy)
        ori_requested = False
        for i, key in enumerate(("roll_deg", "pitch_deg", "yaw_deg")):
            dkey = "d" + key
            if key in body and body[key] is not None:
                tgt_rpy[i] = float(body[key])
                named[key] = float(body[key])
                ori_requested = True
            elif dkey in body and body[dkey] is not None:
                tgt_rpy[i] = cur_rpy[i] + float(body[dkey])
                named[dkey] = float(body[dkey])
                ori_requested = True
        q_tgt = self._quat_from_rpy_deg(*tgt_rpy)

        if "gripper" in body and body["gripper"] is not None:
            g_cmd = float(np.clip(body["gripper"], 0.0, 1.0))
            named["gripper"] = g_cmd
            self.last_g_cmd = g_cmd
        else:
            # Hold last commanded open/close. Do NOT use analog gripper_open
            # (0.71 looks "open" and would drop a pinch).
            g_cmd = self.last_g_cmd
        note = body.get("note") or ""
        grip_act = GRIP_OPEN if g_cmd >= 0.5 else GRIP_CLOSE

        planned = 0
        last_dist = float(np.linalg.norm(target - cur))
        stall = 0
        stopped = "reached"
        while planned < 50 and self.env_steps < MAX_ENV_STEPS:
            cur = self.obs["robot0_eef_pos"].astype(np.float64)
            q_cur = self.obs["robot0_eef_quat"].astype(np.float64)
            delta = target - cur
            dist = float(np.linalg.norm(delta))
            if ori_requested:
                q_err = T.quat_multiply(q_tgt, T.quat_inverse(q_cur))
                if q_err[3] < 0:
                    q_err = -q_err
                aa = np.array(T.quat2axisangle(q_err), dtype=np.float64)
                ang = float(np.linalg.norm(aa))
                ori_act = np.clip(aa / ORI_SCALE, -1.0, 1.0)
                ori_done = ang < 0.05
            else:
                ori_act = np.zeros(3)
                ori_done = True
            pos_done = dist < 0.012
            move_id = self.moves + 1
            if pos_done and ori_done:
                action = np.array(
                    [0, 0, 0, 0, 0, 0, grip_act], dtype=np.float32
                )
                self._apply_action(
                    action,
                    kind="dwell",
                    move_id=move_id,
                    interp_i=planned,
                    target=target,
                )
                planned += 1
                if self.env.check_success():
                    self.success = True
                    break
                dwell = 12 if g_cmd < 0.5 else 8
                if planned >= dwell:
                    stopped = "reached"
                    break
                continue
            pos_act = np.clip(delta / POS_SCALE, -1.0, 1.0)
            if g_cmd < 0.5:
                # slower vertical when closed so a pinch is not snatched off the rim
                pos_act[2] = float(np.clip(pos_act[2], -0.35, 0.35))
            action = np.concatenate([pos_act, ori_act, [grip_act]]).astype(
                np.float32
            )
            self._apply_action(
                action,
                kind="interp",
                move_id=move_id,
                interp_i=planned,
                target=target,
            )
            planned += 1
            new_dist = float(
                np.linalg.norm(
                    target - self.obs["robot0_eef_pos"].astype(np.float64)
                )
            )
            if new_dist > last_dist - 0.002 and dist > 0.02:
                stall += 1
            else:
                stall = 0
            last_dist = new_dist
            # Only call a large remaining error "blocked" after the arm has
            # actually tried; small free-space moves must be allowed to finish.
            if stall >= 10 and planned >= 20:
                stopped = "blocked"
                break
            if self.env.check_success():
                self.success = True
                break

        self.moves += 1
        self.success = bool(self.env.check_success())
        remaining = [
            round(float(target[i] - self.obs["robot0_eef_pos"][i]), 4)
            for i in range(3)
        ]
        if stopped == "blocked":
            self.last_feedback = (
                "blocked/contact: target not reached after stall. "
                "remaining_xyz_m={} remaining_z_cm={:.1f}. "
                "Do not repeat the same z; change height, xy, or pitch.".format(
                    remaining, remaining[2] * 100.0
                )
            )
        else:
            self.last_feedback = (
                "ok: {} dist_m={:.3f} remaining_xyz={}".format(
                    stopped, last_dist, remaining
                )
            )
        reached = self._state()
        rec = {
            "event": "move",
            "move_id": self.moves,
            "named": named,
            "note": note,
            "target": [round(float(v), 4) for v in target],
            "target_rpy_deg": [round(float(v), 1) for v in tgt_rpy],
            "planned_env_steps": planned,
            "final_dist_m": round(last_dist, 4),
            "stopped": stopped,
            "feedback": self.last_feedback,
            "state": reached,
        }
        self._log(rec)
        payload = self._dump_obs()
        payload["last_move"] = rec
        if self.success:
            payload["result"] = self._finish("success")
        elif self.env_steps >= MAX_ENV_STEPS:
            payload["result"] = self._finish("max_env_steps")
        elif self.moves >= MAX_MOVES:
            payload["result"] = self._finish("max_moves")
        return payload

    def give_up(self, reason):
        if self.terminated:
            return json.loads((RUN_DIR / "result.json").read_text())
        return self._finish("give_up:" + (reason or "unspecified"))


EP = Episode()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("[bridge] " + (fmt % args) + "\n")

    def _send(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n == 0:
            return {}
        return json.loads(self.rfile.read(n).decode() or "{}")

    def do_GET(self):
        if self.path in ("/status", "/obs", "/"):
            with EP.lock:
                self._send(200, EP._dump_obs())
            return
        self._send(404, {"error": "not found"})

    def do_POST(self):
        try:
            body = self._read_json()
            with EP.lock:
                if self.path == "/move":
                    self._send(200, EP.move(body))
                    return
                if self.path == "/give_up":
                    self._send(200, EP.give_up(body.get("reason")))
                    return
            self._send(404, {"error": "not found"})
        except Exception as e:
            traceback.print_exc()
            self._send(500, {"error": str(e)})


def main():
    import shutil

    OBS_DIR.mkdir(parents=True, exist_ok=True)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "transcript.jsonl").write_text("")
    (RUN_DIR / "steps.jsonl").write_text("")
    (RUN_DIR / "ctrl").mkdir(parents=True, exist_ok=True)
    prompt = ROOT / "PROMPT.txt"
    if prompt.exists():
        shutil.copy(prompt, RUN_DIR / "PROMPT.txt")
    print(f"[bridge] starting env suite={SUITE} task={TASK_ID} init={INIT_ID}")
    print(f"[bridge] run dir {RUN_DIR}")
    print(f"[bridge] world_axes_overlay={int(WORLD_AXES)}")
    EP.start()
    # Single-thread only: MuJoCo/EGL rendering is not safe across HTTP worker threads.
    httpd = HTTPServer((HOST, PORT), Handler)
    print(f"[bridge] http://{HOST}:{PORT}  instruction={EP.instruction!r}")
    print("[bridge] obs ->", OBS_DIR)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
