#!/usr/bin/env python3
"""Overlay world-frame XYZ on a saved agentview PNG. Does not touch the sim."""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

# Libero_Tabletop_Manipulation.agentview (libero_spatial / libero_goal).
# MuJoCo camera quat is wxyz. Default fovy is 45 deg.
TABLETOP_AGENTVIEW = {
    "pos": np.array([0.6586131746834771, 0.0, 1.6103500240372423]),
    "quat_wxyz": np.array(
        [0.6380177736282349, 0.3048497438430786, 0.30484986305236816, 0.6380177736282349]
    ),
    "fovy_deg": 45.0,
}

# RGB = XYZ
AXIS_BGR = {
    "X": (0, 0, 255),
    "Y": (0, 200, 0),
    "Z": (255, 80, 0),
}


def quat_wxyz_to_mat(q: np.ndarray) -> np.ndarray:
    w, x, y, z = [float(v) for v in q]
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ],
        dtype=np.float64,
    )


def opencv_camera_pose(pos: np.ndarray, quat_wxyz: np.ndarray) -> np.ndarray:
    """Camera-from-world pose in OpenCV convention (x right, y down, z forward).

    MuJoCo cameras look along -Z with +Y up. robosuite applies diag(1,-1,-1).
    """
    R_mujoco = quat_wxyz_to_mat(quat_wxyz)
    R_cv = R_mujoco @ np.diag([1.0, -1.0, -1.0])
    pose = np.eye(4)
    pose[:3, :3] = R_cv
    pose[:3, 3] = pos
    return pose


def project_world(
    points: np.ndarray,
    cam_pose: np.ndarray,
    fovy_deg: float,
    width: int,
    height: int,
):
    """World metres -> pixel (u, v) on the saved PNG (agentview or wrist).

    Projection is OpenCV (y down). robosuite obs is OpenGL; the bridge then
    stores img[::-1, ::-1] (rot180). That is an OpenCV image flipped left-right.

    Returns (uv [N,2], in_front [N] bool).
    """
    pts = np.asarray(points, dtype=np.float64).reshape(-1, 3)
    pose_inv = np.linalg.inv(cam_pose)
    cam = (pose_inv[:3, :3] @ pts.T + pose_inv[:3, 3:4]).T
    z = cam[:, 2]
    in_front = z > 1e-6
    z_safe = np.where(in_front, z, 1.0)
    f = 0.5 * height / np.tan(np.deg2rad(fovy_deg) / 2.0)
    u = f * cam[:, 0] / z_safe + width / 2.0
    v = f * cam[:, 1] / z_safe + height / 2.0
    u = width - 1.0 - u
    return np.stack([u, v], axis=1), in_front


def camera_pose_from_sim(sim, camera_name: str = "agentview"):
    """OpenCV camera pose (x right, y down, z forward) and fovy from a live MjSim."""
    cam_id = sim.model.camera_name2id(camera_name)
    pos = np.array(sim.data.cam_xpos[cam_id], dtype=np.float64)
    R_mujoco = np.array(sim.data.cam_xmat[cam_id], dtype=np.float64).reshape(3, 3)
    fovy = float(sim.model.cam_fovy[cam_id])
    pose = np.eye(4)
    pose[:3, :3] = R_mujoco @ np.diag([1.0, -1.0, -1.0])
    pose[:3, 3] = pos
    return pose, fovy


def draw_triad(img: np.ndarray, origin_uv, tips: dict, labels=True, legend=False) -> np.ndarray:
    out = img.copy()
    ox, oy = int(round(origin_uv[0])), int(round(origin_uv[1]))
    cv2.circle(out, (ox, oy), 4, (255, 255, 255), -1)
    cv2.circle(out, (ox, oy), 5, (0, 0, 0), 1)
    for name, uv in tips.items():
        tx, ty = int(round(float(uv[0]))), int(round(float(uv[1])))
        color = AXIS_BGR[name]
        length = float(np.hypot(tx - ox, ty - oy))
        if not np.isfinite(uv[0]) or length < 10:
            # Axis nearly along the view (common for world +Z in a downward wrist).
            cv2.circle(out, (ox, oy), 9, (0, 0, 0), 3)
            cv2.circle(out, (ox, oy), 9, color, 2)
            if labels:
                cv2.putText(
                    out, name, (ox + 8, oy - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3, cv2.LINE_AA
                )
                cv2.putText(
                    out, name, (ox + 8, oy - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv2.LINE_AA
                )
            continue
        cv2.arrowedLine(out, (ox, oy), (tx, ty), (0, 0, 0), 4, tipLength=0.18)
        cv2.arrowedLine(out, (ox, oy), (tx, ty), color, 2, tipLength=0.18)
        if labels:
            lx, ly = tx + (8 if tx >= ox else -18), ty + (16 if ty >= oy else -8)
            cv2.putText(
                out, name, (lx, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3, cv2.LINE_AA
            )
            cv2.putText(
                out, name, (lx, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv2.LINE_AA
            )
    if legend:
        text = "world +X red  +Y green  +Z blue"
        cv2.putText(out, text, (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(out, text, (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def overlay_world_axes_bgr(
    img_bgr: np.ndarray,
    cam_pose: np.ndarray,
    fovy_deg: float,
    *,
    alpha: float = 0.5,
    axis_len: float = 0.18,
    labels: bool = True,
    legend: bool = False,
) -> np.ndarray:
    """Draw world XYZ at the image-center optical axis. alpha=1 opaque, 0.5 translucent."""
    img = np.ascontiguousarray(img_bgr)
    h, w = img.shape[:2]
    f = 0.5 * h / np.tan(np.deg2rad(fovy_deg) / 2.0)
    target_px = 0.22 * min(w, h)
    depth = max((f * axis_len) / max(target_px, 1.0), 1e-3)
    origin_w = cam_pose[:3, 3] + depth * cam_pose[:3, 2]
    world_pts = np.vstack(
        [
            origin_w,
            origin_w + np.array([axis_len, 0.0, 0.0]),
            origin_w + np.array([0.0, axis_len, 0.0]),
            origin_w + np.array([0.0, 0.0, axis_len]),
        ]
    )
    uv, in_front = project_world(world_pts, cam_pose, fovy_deg, w, h)
    tips = {}
    for name, idx in (("X", 1), ("Y", 2), ("Z", 3)):
        tips[name] = uv[idx] if bool(in_front[idx]) else uv[0]
    layer = draw_triad(img, uv[0], tips, labels=labels, legend=legend)
    a = float(np.clip(alpha, 0.0, 1.0))
    if a >= 1.0:
        return layer
    if a <= 0.0:
        return img
    return cv2.addWeighted(layer, a, img, 1.0 - a, 0)


def main():
    root = Path(__file__).resolve().parent
    p = argparse.ArgumentParser()
    p.add_argument("--src", default=str(root / "obs" / "agentview.png"))
    p.add_argument("--out", default=str(root / "obs_orient" / "agentview_world_axes.png"))
    p.add_argument("--axis-len", type=float, default=0.18, help="world metres")
    p.add_argument("--alpha", type=float, default=1.0, help="1=opaque, 0.5=translucent")
    args = p.parse_args()

    src = Path(args.src)
    img = cv2.imread(str(src), cv2.IMREAD_COLOR)
    if img is None:
        raise SystemExit(f"cannot read {src}")

    cam = opencv_camera_pose(TABLETOP_AGENTVIEW["pos"], TABLETOP_AGENTVIEW["quat_wxyz"])
    out = overlay_world_axes_bgr(
        img,
        cam,
        TABLETOP_AGENTVIEW["fovy_deg"],
        alpha=args.alpha,
        axis_len=args.axis_len,
        legend=True,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), out)
    compare = np.concatenate([img, out], axis=1)
    compare_path = out_path.with_name(out_path.stem + "_compare.png")
    cv2.imwrite(str(compare_path), compare)
    print(f"src={src}")
    print(f"out={out_path}")
    print(f"compare={compare_path}")
    print(f"alpha={args.alpha}")


if __name__ == "__main__":
    main()
