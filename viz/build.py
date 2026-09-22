#!/usr/bin/env python3
"""Pack every LIBERO×Astra episode into viz/data.js + viz/frames/<id>/."""
from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/chener/LIBERO/astra_eval")
RUNS = ROOT / "runs"
OUT = ROOT / "viz"
FRAMES_OUT = OUT / "frames"
CTRL_OUT = OUT / "ctrl"
DATA_JS = OUT / "data.js"
WIN_SYNC = Path("/mnt/c/Users/c00670587/Documents/LIBERO-astra-viz")
STALE_SOURCES = ("transcript.jsonl", "steps.jsonl", "result.json", "NOTES.md", "AGENT_SUMMARY.md")

CATALOG = [
    {
        "id": "a1",
        "dir": "spatial0_init0_attempt1",
        "n": 1,
        "title": "第 1 集 · harness 崩溃",
        "kind": "harness",
        "planner": "gpt-6-astra",
        "task_id": 0,
        "headline": "第一步之后两路相机变黑，夹爪极性反了。这不是策略分。",
        "analysis": [
            "ThreadingHTTPServer 在工作线程里调 MuJoCo/EGL，第一步后 RGB 掉到约 1 KB 黑帧。",
            "gripper=1 被映射成合上（Panda 实际是 +1 闭合）。",
            "Astra 看见坏图后原地停住，随即 give_up。只走了 2 次 move / 27 步。",
        ],
    },
    {
        "id": "a2",
        "dir": "spatial0_init0_attempt2",
        "n": 2,
        "title": "第 2 集 · 四次空抓",
        "kind": "policy",
        "planner": "gpt-6-astra",
        "task_id": 0,
        "headline": "相机和夹爪修好后的第一集真实策略：碗找对了，但四次都在同一高度捏碗沿。",
        "analysis": [
            "语义正确：始终抓盘子和 ramekin 中间那只黑碗，没有去搬另一只碗。",
            "程序记忆完整：接近 → 下降 → 合爪 → 垂直抬升验抓 → 空了再张开重对准。从未空抓着去放盘子。",
            "合爪高度锁在 z≈0.94–0.96，手指贴在碗口上沿，gripper_open 合到 0.28–0.40 后一抬变成 0.02。",
            "没有姿态工具，夹爪几乎一直朝下。第 11、17 步各烧 80 环境步。",
        ],
    },
    {
        "id": "a3",
        "dir": "attempt_003_libero_spatial_t0_i0",
        "n": 3,
        "title": "第 3 集 · 姿态回归拧腕",
        "kind": "harness",
        "planner": "gpt-6-astra",
        "task_id": 0,
        "headline": "新桥误把未点名的 roll/pitch/yaw 往 0 拉，腕被拧到 −51°，Astra 走一步就退出。",
        "default_reason": "Codex 在第一次 blocked 之后退出，没有 /give_up，也没有 result.json。",
        "analysis": [
            "目标 (0.03, −0.16, 1.08) 方向还反了（世界 −y 不是碗所在的 +y）。",
            "桥在智能体没点名姿态时仍调节姿态，四元数/欧拉换算出 roll=−51°、yaw=37°。",
            "stall 在 dist=0.26 m 就触发。Codex 写了“下一步抬起来”然后直接结束，没有 /give_up。",
            "随后修复：未点名的姿态维保持当前值；stall 至少 20 步才判；prompt 禁止一步 blocked 就停。",
        ],
    },
    {
        "id": "a4",
        "dir": "attempt_004_libero_spatial_t0_i0",
        "n": 4,
        "title": "第 4 集 · 侧抓 + 反馈",
        "kind": "policy",
        "planner": "gpt-6-astra",
        "task_id": 0,
        "headline": "用上了 pitch 和 harness 反馈，三次侧壁抓仍全空；yaw=90° 再次拧腕。",
        "analysis": [
            "Prompt 写入了第 2 集的教训：空抓后必须降 2–4 cm 或加 10–20° pitch，不要在同一 z 再合。",
            "Astra 确实改了策略：第 1 次 15° pitch，第 2 次 −15° 且更低，第 3 次 10° 侧向偏移。",
            "每次合爪后反馈都能正确报 empty_grasp_suspected。它听了反馈，但碗始终没被带走。",
            "第 12 步 yaw=90° 想换方向，被接触卡住，腕拧到 roll 23° / yaw 73°，后面花了好几步复位。",
            "接触时 z 目标经常到不了（blocked remaining_z≈2 cm），侧壁抓在 OSC 无姿态规划时仍然很难。",
        ],
    },
    {
        "id": "a5",
        "dir": "attempt_005_libero_spatial_t0_i0",
        "n": 5,
        "title": "第 5 集 · 首次成功",
        "kind": "policy",
        "planner": "gpt-6-astra",
        "task_id": 0,
        "headline": "同一任务第一次官方成功：15° 侧壁抓住，先抬 2 cm 确认碗起来，再放到盘子上。",
        "analysis": [
            "相对第 4 集：浅捏后只先抬 2 cm；单步姿态不超过约 20°；碗没起来绝不去盘子。",
            "第一次 pinch 短抬就滑了，重对准后第二次开合保持约 0.16，2 cm 再 5.5 cm 碗都跟着走。",
            "放到盘子时第一次偏了，又抓一次，第 29 步下放时 check_success() 变 true。",
            "29 moves / 466 步 / 352 s。这是目前唯一的官方成功。",
        ],
    },
    {
        "id": "a6",
        "dir": "attempt_006_libero_spatial_t1_i0",
        "n": 6,
        "title": "第 6 集 · 任务 1 失败",
        "kind": "policy",
        "planner": "gpt-6-astra",
        "task_id": 1,
        "headline": "换了「ramekin 旁边的黑碗」，物体认对了，但反复捏沿把碗推走。",
        "analysis": [
            "15° pitch、z≈0.92，第一次 2 cm 试抬开合掉到 0.02，是空抓；桥没报 empty_grasp（抬升不到 4 cm）。",
            "第二次合爪开合 0.71，腕部画面被碗填满，其实是近沿顶在指垫上，不是壁在两爪之间。",
            "未点名 gripper 把 analog 开合 ≥0.5 当成张开，一次 pinch 被松开。",
            "28 moves / 377 步，give_up。任务 1 没有成功记录。",
        ],
    },
    {
        "id": "a7",
        "dir": "attempt_007_libero_spatial_t2_i0",
        "n": 7,
        "title": "第 7 集 · 额度中止",
        "kind": "quota",
        "planner": "gpt-6-astra",
        "task_id": 2,
        "headline": "任务 2（桌面中央的碗）跑到第 7 步，Codex 用量上限，不是策略 give_up。",
        "default_reason": "Codex CLI 用量上限，7 moves 后退出。提示 2026-09-21 00:31 再试。",
        "analysis": [
            "目标应是炉子和银碗之间桌面中央的小碗。接近时碗一度被夹爪挡住。",
            "智能体把「碗从腕部画面消失」理解成要沿 −x 后退 8–12 cm，结果停在炉子上方。",
            "最后 holding_or_pinching g≈0.69、z≈0.929，夹的是炉子不是碗。没做抬升。",
            "7 moves / 125 步。不能当任务 2 的策略分。",
        ],
    },
    {
        "id": "a8",
        "dir": "attempt_008_grok_libero_spatial_t0_i0",
        "n": 8,
        "title": "第 8 集 · Grok 抓到但没放进",
        "kind": "policy",
        "planner": "grok",
        "task_id": 0,
        "headline": "Grok 在任务 0 上把碗抓住并带到盘子边缘，但 30 步用尽，官方成功仍是 false。",
        "analysis": [
            "Planner 换成 Grok，不是 Astra。同一任务 0 init 0。",
            "前三次合爪开合约 0.14，2 cm 试抬掉到 0.07，碗没起来（还是捏沿）。",
            "改成 −x 约 3 cm、pitch 20°、z≈0.915 后开合 0.25，2 cm 和 5.5 cm 抬升都保住，碗跟着走。",
            "侧壁抓让碗相对末端偏了，照抄第 5 集放盘 xy 落在盘子右沿。一直合着爪去挤，没张开，撞上 30 move 上限。",
        ],
    },
    {
        "id": "a9",
        "dir": "attempt_009_grok_libero_spatial_t1_i0",
        "n": 9,
        "title": "第 9 集 · Grok 任务 1 空抓",
        "kind": "policy",
        "planner": "grok",
        "task_id": 1,
        "headline": "Grok 认对了 ramekin 旁的花纹碗，八次合爪全是空的（开合 0.05），从未 holding。",
        "analysis": [
            "物体正确：右前方花纹碗，不是炉子平底锅或后面银碗。簇大约在 xy≈(−0.24, 0.34)。",
            "腕部常被碗填满（相机对着碗心），agentview 里夹爪身体在碗旁边。八次合爪 pitch 15–20°、z 0.91–0.94，每次 gripper_open=0.05。",
            "主误差在 y：y≈0.34 合在碗左侧（ramekin 侧），y≈0.367 合在碗上/右侧空腔。没有 g≳0.14 的沿、也没有 g≳0.25 的壁。",
            "没有像第 6 集那样沿 +x 把碗推走。26 moves 后 give_up，还剩 4 步不够再做一次完整抓放。",
        ],
    },
    {
        "id": "a10",
        "dir": "attempt_010_grok_libero_spatial_t2_i0",
        "n": 10,
        "title": "第 10 集 · Grok 任务 2 九次空关",
        "kind": "policy",
        "planner": "grok",
        "task_id": 2,
        "headline": "中央灰碗找对了、没退到炉子上，但九次合爪八次空，一次擦沿（g=0.11），从未抬升。",
        "analysis": [
            "避开了第 7 集的失败：悬停在中央碗 x≈0.03，没有沿 −x 退到炉子。",
            "20° pitch 在抓取高度会挡住腕部里的碗。agentview「碗在爪下」张开时被当成对准，合上却打空。",
            "张开约 8 cm，左指垫可以盖住碗，闭合轴线却在碗右侧。在 z=0.912 上细调 y，agentview 侧瞥会把碗从极左翻到极右。",
            "30 moves 用尽。唯一接触是 m16 的 g=0.11。没有 2 cm 试抬，没有去盘子。",
        ],
    },
    {
        "id": "a11",
        "dir": "attempt_011_grok_libero_spatial_t3_i0",
        "n": 11,
        "title": "第 11 集 · Grok 任务 3 未写完",
        "kind": "policy",
        "planner": "grok",
        "task_id": 3,
        "headline": "饼干盒上的黑碗：高处对准了十几步，尚未合爪就被切到下一任务。",
        "default_reason": "没有 result.json，评测切到 attempt_012 时停在 move 17。",
        "analysis": [
            "指令：pick up the black bowl on the cookie box and place it on the plate。",
            "前十几步都在高处（z≈1.10–1.18）找饼干盒，避开桌上灰碗和炉子。",
            "若干次 −y / +x 被 stove 挡住。最后 pitch 20°、z≈0.98，爪仍张开。",
            "不是策略 give_up，只是没跑完。不能当 spatial/3 的分数。",
        ],
    },
    {
        "id": "a12",
        "dir": "attempt_012_grok_libero_object_t7_i0",
        "n": 12,
        "title": "第 12 集 · Grok object/7 进行中",
        "kind": "policy",
        "planner": "grok",
        "task_id": 7,
        "suite": "libero_object",
        "headline": "新套件 libero_object：把牛奶放进篮子。刚 reset，轨迹会随评测更新。",
        "default_reason": "进行中，尚无 result.json。",
        "analysis": [
            "指令：pick up the milk and place it in the basket。",
            "这是第一集 object 套件，不再是 spatial 碗→盘。",
            "打包时若只有 reset，回放会很短；结束后重新 build 即可看到完整轨迹。",
        ],
    },
]


ATTEMPT_RE = re.compile(r"attempt_(\d+)")
TAIL_RE = re.compile(r"attempt(\d+)$")
SUITE_RE = re.compile(r"libero_([a-z]+)_t(\d+)_i(\d+)")


def run_number(name: str):
    m = ATTEMPT_RE.search(name)
    if m:
        return int(m.group(1))
    m = TAIL_RE.search(name)
    if m:
        return int(m.group(1))
    return None


def latest_run_mtime() -> float:
    newest = 0.0
    if not RUNS.exists():
        return 0.0
    for d in RUNS.iterdir():
        if not d.is_dir() or d.name == "current":
            continue
        for name in STALE_SOURCES:
            p = d / name
            if p.exists():
                newest = max(newest, p.stat().st_mtime)
    return newest


def is_stale() -> bool:
    stamp = DATA_JS.stat().st_mtime if DATA_JS.exists() else 0.0
    return latest_run_mtime() > stamp + 0.5


def discover_catalog() -> list[dict]:
    """Every run dir with a transcript, overlay optional hand notes from CATALOG."""
    overlay = {c["dir"]: c for c in CATALOG}
    found = []
    for d in RUNS.iterdir():
        if not d.is_dir() or d.name in {"current"}:
            continue
        if not (d / "transcript.jsonl").exists():
            continue
        n = run_number(d.name)
        found.append((n if n is not None else 10_000, d.stat().st_mtime, d))
    found.sort()
    cats = []
    used = set()
    for n, _, d in found:
        ov = overlay.get(d.name) or {}
        if n is None or n == 10_000 or n in used:
            n = ov.get("n") or ((max(used) + 1) if used else 1)
        used.add(n)
        cat = dict(ov)
        cat["dir"] = d.name
        cat["n"] = n
        cat["id"] = ov.get("id") or f"a{n}"
        if not cat.get("planner"):
            cat["planner"] = "grok" if "_grok_" in d.name else "gpt-6-astra"
        m = SUITE_RE.search(d.name)
        if m:
            cat.setdefault("suite", "libero_" + m.group(1))
            cat.setdefault("task_id", int(m.group(2)))
        cat.setdefault("kind", "policy")
        cat.setdefault("title", f"第 {n} 集 · {cat['planner']} · {d.name}")
        cat.setdefault("headline", "")
        cat.setdefault("analysis", [])
        cats.append(cat)
    return cats


def enrich_from_files(cat: dict, run_dir: Path, result: dict) -> None:
    notes_p = run_dir / "NOTES.md"
    if notes_p.exists():
        lines = [ln.strip() for ln in notes_p.read_text().splitlines() if ln.strip()]
        if lines and not cat.get("headline"):
            cat["headline"] = lines[0].lstrip("# ").strip()
        if lines and not cat.get("analysis"):
            cat["analysis"] = lines[1:7]
    if not cat.get("headline"):
        cat["headline"] = (result.get("reason") or result.get("instruction") or run_dir.name)[:140]
    if not cat.get("analysis"):
        cat["analysis"] = []
    if not cat.get("suite"):
        cat["suite"] = result.get("suite") or "libero_spatial"
    if cat.get("task_id") is None:
        cat["task_id"] = result.get("task_id")


def copy_if_newer(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        ss, ds = src.stat(), dest.stat()
        if ds.st_size == ss.st_size and ds.st_mtime >= ss.st_mtime:
            return
    shutil.copy2(src, dest)


def nearest_frame(frame_dir: Path, steps: int, kind: str) -> str:
    name = f"{steps:04d}_{kind}.png"
    if (frame_dir / name).exists():
        return name
    nums = sorted({int(p.name[:4]) for p in frame_dir.glob(f"*_{kind}.png")})
    if not nums:
        return name
    best = min(nums, key=lambda n: abs(n - steps))
    return f"{best:04d}_{kind}.png"


def classify(rec: dict) -> tuple[str, str, str]:
    ev = rec.get("event")
    if ev == "reset":
        return "reset", "复位", "环境就绪"
    if ev == "done":
        if rec.get("success"):
            return "success", "成功", rec.get("reason") or ""
        return "give_up", "放弃", (rec.get("reason") or "")[:120]
    named = rec.get("named") or {}
    st = rec.get("state") or {}
    fb = rec.get("feedback") or st.get("feedback") or ""
    planned = rec.get("planned_env_steps") or 0
    stopped = rec.get("stopped")
    g = named.get("gripper")
    ori_keys = ("roll_deg", "pitch_deg", "yaw_deg", "droll_deg", "dpitch_deg", "dyaw_deg")
    has_ori = any(k in named for k in ori_keys)
    named_abs_ori = [k for k in ("roll_deg", "pitch_deg", "yaw_deg") if k in named]
    ori_reset = bool(named_abs_ori) and all(float(named[k]) == 0.0 for k in named_abs_ori)

    if "empty_grasp" in fb:
        return "lift", "空抓抬升", "夹爪合死但碗没起来"
    if g == 0.0 and (float(named.get("dz") or 0) > 0.03 or float(named.get("z") or 0) > 1.0):
        return "lift", "抬升验抓", "垂直抬，看碗是否跟随"
    if g == 0.0 and "z" not in named and "dz" not in named:
        return "close", "合爪", "尝试抓住"
    if stopped == "blocked" or "blocked" in fb:
        return "stall", "接触卡住", (fb.split(".")[0] if fb else "目标没到")
    if planned >= 70:
        return "stall", "插值打满", "80 步仍到不了 1.2 cm"
    if ori_reset:
        return "reacquire", "复位姿态", "roll/pitch/yaw 回 0"
    if has_ori:
        return "approach", "倾斜接近", "侧向 / 侧壁"
    if g == 1.0:
        return "reacquire", "张开重对准", "打开夹爪再找碗"
    return "approach", "接近", ""


def load_records(run_dir: Path) -> list[dict]:
    p = run_dir / "transcript.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def pack_ctrl(run_dir: Path, eid: str, move_meta: dict) -> list[dict]:
    """20 Hz control-step archive: steps.jsonl + ctrl/*.png."""
    steps_p = run_dir / "steps.jsonl"
    src = run_dir / "ctrl"
    if not steps_p.exists() or not src.is_dir():
        return []
    dest = CTRL_OUT / eid
    dest.mkdir(parents=True, exist_ok=True)
    out = []
    for line in steps_p.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        env_step = int(rec.get("env_step") or 0)
        prefix = f"{env_step:04d}"
        for cam in ("agentview", "wrist"):
            srcp = src / f"{prefix}_{cam}.png"
            if srcp.exists():
                copy_if_newer(srcp, dest / srcp.name)
        kind = rec.get("kind") or "interp"
        act = rec.get("action") or []
        phase = {"dummy": "reset", "dwell": "close", "interp": "approach"}.get(kind, "approach")
        if len(act) >= 7 and float(act[6]) >= 0.5:
            phase = "close"
        mid = rec.get("move_id")
        meta = move_meta.get(mid) or {}
        out.append(
            {
                "i": len(out),
                "event": "ctrl",
                "move_id": mid,
                "env_steps": env_step,
                "interp_i": rec.get("interp_i"),
                "kind": kind,
                "action": act,
                "eef": rec.get("eef") or [0, 0, 0],
                "rpy": rec.get("rpy_deg") or [None, None, None],
                "gripper_open": rec.get("gripper_open"),
                "dist_m": rec.get("dist_m"),
                "success": rec.get("success"),
                "phase": phase,
                "phaseLabel": kind,
                "phaseHint": f"move {mid} · interp {rec.get('interp_i')}",
                "note": meta.get("note") or "",
                "feedback": meta.get("feedback") or "",
                "named": meta.get("named") or {},
                "target": meta.get("target"),
                "target_rpy": meta.get("target_rpy"),
                "t_rel": None,
                "agentview": f"ctrl/{eid}/{prefix}_agentview.png",
                "wrist": f"ctrl/{eid}/{prefix}_wrist.png",
            }
        )
    return out


def pack_episode(cat: dict) -> dict:
    run_dir = RUNS / cat["dir"]
    recs = load_records(run_dir)
    src_frames = run_dir / "frames"
    dest = FRAMES_OUT / cat["id"]
    dest.mkdir(parents=True, exist_ok=True)
    if src_frames.exists():
        for p in src_frames.glob("*.png"):
            copy_if_newer(p, dest / p.name)

    result = {}
    rp = run_dir / "result.json"
    if rp.exists():
        result = json.loads(rp.read_text())
    enrich_from_files(cat, run_dir, result)
    summary = ""
    sp = run_dir / "AGENT_SUMMARY.md"
    if sp.exists():
        summary = sp.read_text()

    t0 = recs[0]["t"] if recs else 0
    steps = []
    n_close = n_empty = n_blocked = 0
    min_z = 9.0
    max_abs_pitch = 0.0
    used_ori = False

    for rec in recs:
        ev = rec.get("event")
        if ev == "reset":
            st = rec["state"]
            named, target, planned, dist, note, stopped = {}, None, 5, None, rec.get("state", {}).get("feedback") or "reset", None
            target_rpy = None
            move_id = 0
            fb = st.get("feedback") or ""
        elif ev == "move":
            st = rec["state"]
            named = rec.get("named") or {}
            target = rec.get("target")
            planned = rec.get("planned_env_steps")
            dist = rec.get("final_dist_m")
            note = rec.get("note") or ""
            stopped = rec.get("stopped")
            move_id = rec["move_id"]
            fb = rec.get("feedback") or st.get("feedback") or ""
            target_rpy = rec.get("target_rpy_deg")
        elif ev == "done":
            st = rec.get("final_state") or rec.get("state") or {}
            named, target, planned, dist = {}, None, None, None
            target_rpy = None
            note = rec.get("reason") or ""
            stopped = None
            move_id = 10_000
            fb = note
        else:
            continue

        phase, plabel, phint = classify(rec)
        if phase == "close":
            n_close += 1
        if phase == "lift":
            n_empty += 1
        if phase == "stall":
            n_blocked += 1
        z = float(st.get("eef_z") or 0)
        min_z = min(min_z, z)
        pitch = st.get("pitch_deg")
        if pitch is not None:
            max_abs_pitch = max(max_abs_pitch, abs(float(pitch)))
        if any(k in named for k in ("roll_deg", "pitch_deg", "yaw_deg")):
            used_ori = True

        env_steps = int(st.get("env_steps") or 0)
        av = nearest_frame(src_frames, env_steps, "agentview")
        wr = nearest_frame(src_frames, env_steps, "wrist")
        steps.append(
            {
                "i": len(steps),
                "event": ev,
                "move_id": 0 if ev == "reset" else (None if ev == "done" else move_id),
                "t_rel": round(rec["t"] - t0, 2),
                "phase": phase,
                "phaseLabel": plabel,
                "phaseHint": phint,
                "note": note,
                "feedback": fb,
                "named": named,
                "target": target,
                "target_rpy": target_rpy,
                "planned_env_steps": planned,
                "final_dist_m": dist,
                "stopped": stopped,
                "eef": [
                    round(float(st.get("eef_x") or 0), 4),
                    round(float(st.get("eef_y") or 0), 4),
                    round(float(st.get("eef_z") or 0), 4),
                ],
                "rpy": [
                    st.get("roll_deg"),
                    st.get("pitch_deg"),
                    st.get("yaw_deg"),
                ],
                "gripper_open": st.get("gripper_open"),
                "env_steps": env_steps,
                "remaining_moves": st.get("remaining_moves"),
                "remaining_env_steps": st.get("remaining_env_steps"),
                "agentview": f"frames/{cat['id']}/{av}",
                "wrist": f"frames/{cat['id']}/{wr}",
            }
        )

    current_name = ""
    cur = RUNS / "current"
    if cur.is_symlink():
        current_name = Path(os.readlink(cur)).name
    elif cur.exists():
        current_name = cur.resolve().name
    running = (
        run_dir.name == current_name
        and not rp.exists()
        and (not recs or recs[-1].get("event") != "done")
    )

    last = recs[-1] if recs else {}
    success = result.get("success")
    if success is None and last.get("event") == "done":
        success = last.get("success")
    reason = result.get("reason") or (last.get("reason") if last.get("event") == "done" else None)
    if running:
        reason = reason or "进行中（尚无 result.json）"
    elif success is None and last.get("event") != "done":
        reason = reason or cat.get("default_reason") or "Codex 中途退出，没有 /give_up"

    moves = result.get("moves")
    env_steps = result.get("env_steps")
    elapsed = result.get("elapsed_s")
    if moves is None and recs:
        mv = [r for r in recs if r.get("event") == "move"]
        moves = mv[-1]["move_id"] if mv else 0
        st = (last.get("final_state") or last.get("state") or {})
        env_steps = st.get("env_steps")
        elapsed = round(last["t"] - t0, 2) if t0 else None

    story = []
    for i, s in enumerate(steps):
        if i == 0 or s["phase"] in ("close", "lift", "give_up", "success") or (
            s["phase"] == "stall" and (s.get("planned_env_steps") or 0) >= 20
        ):
            story.append(i)
    if steps and (len(steps) - 1) not in story:
        story.append(len(steps) - 1)
    # unique, cap
    seen = set()
    story_u = []
    for i in story:
        if i not in seen:
            seen.add(i)
            story_u.append(i)
    if len(story_u) > 12:
        story_u = [story_u[0]] + story_u[1:-1][:: max(1, (len(story_u) - 2) // 10)] + [story_u[-1]]
        story_u = sorted(set(story_u))

    if running:
        status = "running"
    elif cat["kind"] == "quota":
        status = "aborted"
    elif cat["kind"] == "harness":
        status = "harness" if cat["id"] == "a1" else "aborted"
    elif success:
        status = "success"
    elif not rp.exists() and (not recs or recs[-1].get("event") != "done"):
        status = "aborted"
    else:
        status = "fail"

    packed = {
        "id": cat["id"],
        "n": cat["n"],
        "dir": cat["dir"],
        "title": cat["title"],
        "kind": cat["kind"],
        "planner": cat.get("planner") or "gpt-6-astra",
        "suite": cat.get("suite") or result.get("suite") or "libero_spatial",
        "task_id": cat.get("task_id", result.get("task_id")),
        "status": status,
        "headline": cat["headline"],
        "analysis": cat["analysis"],
        "summary_md": summary,
        "success": success,
        "reason": reason,
        "running": running,
        "moves": moves,
        "env_steps": env_steps,
        "elapsed_s": elapsed,
        "n_close": n_close,
        "n_empty": n_empty,
        "n_blocked": n_blocked,
        "min_z": None if min_z > 8 else round(min_z, 3),
        "max_abs_pitch": round(max_abs_pitch, 1),
        "used_ori": used_ori,
        "story": story_u,
        "steps": steps,
        "task": (recs[0].get("instruction") if recs else None)
        or result.get("instruction")
        or cat.get("headline")
        or run_dir.name,
    }
    move_meta = {}
    for s in steps:
        mid = s.get("move_id")
        if mid is None:
            continue
        rec = move_meta.setdefault(mid, {})
        if s.get("note"):
            rec["note"] = s["note"]
        if s.get("feedback"):
            rec["feedback"] = s["feedback"]
        if s.get("named"):
            rec["named"] = s["named"]
        if s.get("target"):
            rec["target"] = s["target"]
        if s.get("target_rpy"):
            rec["target_rpy"] = s["target_rpy"]
    ctrl = pack_ctrl(run_dir, cat["id"], move_meta)
    packed["hasCtrl"] = bool(ctrl)
    packed["n_ctrl"] = len(ctrl)
    packed["ctrl"] = ctrl
    return packed


def sync_windows() -> None:
    win = WIN_SYNC
    if not win.parent.exists():
        return
    win.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(OUT / "index.html", win / "index.html")
    shutil.copyfile(DATA_JS, win / "data.js")
    bat = OUT / "open-in-windows.bat"
    if bat.exists():
        shutil.copyfile(bat, win / "open-in-windows.bat")
    for sub in ("frames", "ctrl"):
        src_root = OUT / sub
        if not src_root.exists():
            continue
        for src in src_root.rglob("*"):
            if src.is_file():
                dst = win / sub / src.relative_to(src_root)
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists() and dst.stat().st_size == src.stat().st_size:
                    continue
                shutil.copyfile(src, dst)
    print("synced", win)


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Pack LIBERO×Astra runs into viz/data.js")
    parser.add_argument("--no-win", action="store_true", help="skip the Windows Documents copy")
    parser.add_argument("--force", action="store_true", help="rebuild even if data.js is newer")
    args = parser.parse_args(argv)
    if not args.force and not is_stale() and DATA_JS.exists():
        print("viz: data.js already current")
        return
    FRAMES_OUT.mkdir(parents=True, exist_ok=True)
    CTRL_OUT.mkdir(parents=True, exist_ok=True)
    episodes = [pack_episode(c) for c in discover_catalog()]
    payload = {
        "meta": {
            "title": "LIBERO × Codex CLI · GPT-6 Astra",
            "built_at": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
            "n_episodes": len(episodes),
            "suite": "libero_spatial",
            "task_id": 0,
            "init_id": 0,
            "model": "gpt-6-astra",
            "effort": "medium",
            "task": "pick up the black bowl between the plate and the ramekin and place it on the plate",
            "architecture": [
                {"id": "planner", "title": "Codex CLI", "sub": "gpt-6-astra · medium"},
                {"id": "http", "title": "HTTP 桥", "sub": "POST /move  :8765"},
                {"id": "osc", "title": "OSC 插值", "sub": "xyz + 可选姿态"},
                {"id": "env", "title": "LIBERO", "sub": "Panda · EGL"},
                {"id": "obs", "title": "观测", "sub": "RGB + EEF + feedback"},
            ],
        },
        "episodes": episodes,
    }
    DATA_JS.write_text(
        "window.EPISODE = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print("wrote", DATA_JS, "episodes", len(episodes))
    if not args.no_win:
        sync_windows()
    for e in episodes:
        print(
            f"  {e['id']} status={e['status']} moves={e['moves']} steps={e['env_steps']} "
            f"close={e['n_close']} empty={e['n_empty']} blocked={e['n_blocked']} "
            f"nsteps={len(e['steps'])} nctrl={e.get('n_ctrl', 0)}"
        )


if __name__ == "__main__":
    main()
