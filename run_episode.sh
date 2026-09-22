#!/usr/bin/env bash
# Start a numbered LIBERO×Astra episode, then Codex CLI.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
source /home/chener/miniconda3/etc/profile.d/conda.sh
conda activate libero
export MUJOCO_GL=egl PYOPENGL_PLATFORM=egl
export LIBERO_SUITE="${LIBERO_SUITE:-libero_spatial}"
export LIBERO_TASK_ID="${LIBERO_TASK_ID:-0}"
export LIBERO_INIT_ID="${LIBERO_INIT_ID:-0}"
export LIBERO_MAX_MOVES="${LIBERO_MAX_MOVES:-30}"
export LIBERO_MAX_ENV_STEPS="${LIBERO_MAX_ENV_STEPS:-600}"
# 1/true/on: translucent world XYZ triad at agentview and wrist centers. Default off.
export LIBERO_WORLD_AXES="${LIBERO_WORLD_AXES:-0}"
python3 "$ROOT/compose_prompt.py"

n=0
for d in "$ROOT"/runs/attempt_*; do
  [[ -d "$d" ]] && n=$((n + 1))
done
# also count the two older named runs
for d in "$ROOT"/runs/spatial0_init0_attempt1 "$ROOT"/runs/spatial0_init0_attempt2; do
  [[ -d "$d" ]] && n=$((n + 1))
done
n=$((n + 1))
NAME=$(printf "attempt_%03d_%s_t%s_i%s" "$n" "$LIBERO_SUITE" "$LIBERO_TASK_ID" "$LIBERO_INIT_ID")
export LIBERO_RUN_DIR="$ROOT/runs/$NAME"
rm -rf "$ROOT/obs" "$ROOT/runs/current"
mkdir -p "$LIBERO_RUN_DIR/frames" "$ROOT/obs" "$ROOT/logs"
ln -sfn "$NAME" "$ROOT/runs/current"

# stop leftover bridge
if [[ -f "$ROOT/logs/bridge.pid" ]]; then
  kill "$(cat "$ROOT/logs/bridge.pid")" 2>/dev/null || true
fi
fuser -k 8765/tcp 2>/dev/null || true
sleep 1

python "$ROOT/bridge_server.py" >"$ROOT/logs/bridge.log" 2>&1 &
echo $! >"$ROOT/logs/bridge.pid"
for i in $(seq 1 45); do
  if curl -sf http://127.0.0.1:8765/status >/dev/null; then
    echo "bridge ready ($i) run=$NAME"
    break
  fi
  sleep 1
done
curl -sf http://127.0.0.1:8765/status >/dev/null

MODEL="${CODEX_MODEL:-gpt-6-astra}"
EFFORT="${CODEX_EFFORT:-medium}"
SUMMARY="${CODEX_REASONING_SUMMARY:-auto}"
echo "Codex $MODEL $EFFORT summary=$SUMMARY  run=$LIBERO_RUN_DIR world_axes=$LIBERO_WORLD_AXES"
: > "$ROOT/logs/codex.log"
codex exec \
  -m "$MODEL" \
  -c "model_reasoning_effort=\"${EFFORT}\"" \
  -c "model_reasoning_summary=\"${SUMMARY}\"" \
  -c "model_supports_reasoning_summaries=true" \
  -c "hide_agent_reasoning=false" \
  --dangerously-bypass-approvals-and-sandbox \
  --skip-git-repo-check \
  -C "$ROOT" \
  -i "$ROOT/obs/agentview.png" \
  -i "$ROOT/obs/wrist.png" \
  < "$ROOT/PROMPT.txt" \
  > "$ROOT/logs/codex.log" 2>&1
echo "codex_exit:$?"
cp -f "$ROOT/logs/codex.log" "$LIBERO_RUN_DIR/codex.log" || true
# keep a pointer from runs/current (symlink) and write index
python3 - << PY
import json, os, time
from pathlib import Path
root = Path("$ROOT")
run = Path("$LIBERO_RUN_DIR")
result = {}
rp = run / "result.json"
if rp.exists():
    result = json.loads(rp.read_text())
rec = {
    "t": time.time(),
    "run": run.name,
    "suite": os.environ["LIBERO_SUITE"],
    "task_id": int(os.environ["LIBERO_TASK_ID"]),
    "init_id": int(os.environ["LIBERO_INIT_ID"]),
    "success": result.get("success"),
    "reason": result.get("reason"),
    "moves": result.get("moves"),
    "env_steps": result.get("env_steps"),
    "elapsed_s": result.get("elapsed_s"),
    "prompt": str(run / "PROMPT.txt"),
}
with open(root / "runs" / "index.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(json.dumps(rec, indent=2))
PY
python3 "$ROOT/viz/build.py" --no-win >>"$ROOT/logs/viz_build.log" 2>&1 || true
