#!/usr/bin/env python3
"""Print a compact post-run analysis from a run directory (for the parent agent)."""
import json
import sys
from pathlib import Path


def main():
    run = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/current").resolve()
    result = {}
    rp = run / "result.json"
    if rp.exists():
        result = json.loads(rp.read_text())
    moves = []
    tp = run / "transcript.jsonl"
    if tp.exists():
        for line in tp.read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("event") == "move":
                st = rec.get("state") or {}
                moves.append(
                    {
                        "id": rec.get("move_id"),
                        "named": rec.get("named"),
                        "z": st.get("eef_z"),
                        "pitch": st.get("pitch_deg"),
                        "g": st.get("gripper_open"),
                        "stop": rec.get("stopped"),
                        "fb": (rec.get("feedback") or "")[:120],
                    }
                )
    print("RUN", run.name)
    print(
        "success={success} reason={reason} moves={moves} steps={env_steps} s={elapsed_s}".format(
            success=result.get("success"),
            reason=result.get("reason"),
            moves=result.get("moves"),
            env_steps=result.get("env_steps"),
            elapsed_s=result.get("elapsed_s"),
        )
    )
    print("instruction:", result.get("instruction"))
    steps_p = run / "steps.jsonl"
    if steps_p.exists() and steps_p.stat().st_size:
        n_ctrl = sum(1 for line in steps_p.read_text().splitlines() if line.strip())
        n_png = len(list((run / "ctrl").glob("*.png"))) if (run / "ctrl").is_dir() else 0
        print(f"ctrl log: {n_ctrl} steps.jsonl rows, {n_png} pngs under ctrl/")
    print("--- moves ---")
    for m in moves:
        print(
            "m{id:02d} z={z} pitch={pitch} g={g} stop={stop} named={named} | {fb}".format(
                **{**m, "id": m["id"] or 0}
            )
        )
    summary = run / "AGENT_SUMMARY.md"
    if summary.exists():
        print("--- agent summary ---")
        print(summary.read_text()[:2500])


if __name__ == "__main__":
    main()
