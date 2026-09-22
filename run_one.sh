#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
mkdir -p obs runs/current logs

source /home/chener/miniconda3/etc/profile.d/conda.sh
conda activate libero
export MUJOCO_GL=egl
export PYOPENGL_PLATFORM=egl
export LIBERO_SUITE="${LIBERO_SUITE:-libero_spatial}"
export LIBERO_TASK_ID="${LIBERO_TASK_ID:-0}"
export LIBERO_INIT_ID="${LIBERO_INIT_ID:-0}"
export LIBERO_MAX_MOVES="${LIBERO_MAX_MOVES:-25}"
export LIBERO_MAX_ENV_STEPS="${LIBERO_MAX_ENV_STEPS:-600}"
export LIBERO_WORLD_AXES="${LIBERO_WORLD_AXES:-0}"

if curl -sf http://127.0.0.1:8765/status >/dev/null 2>&1; then
  echo "bridge already running"
else
  python "$ROOT/bridge_server.py" >"$ROOT/logs/bridge.log" 2>&1 &
  echo $! >"$ROOT/logs/bridge.pid"
  echo "started bridge pid=$(cat "$ROOT/logs/bridge.pid")"
  for i in $(seq 1 60); do
    if curl -sf http://127.0.0.1:8765/status >/dev/null 2>&1; then
      echo "bridge ready after ${i}s"
      break
    fi
    sleep 1
  done
  curl -sf http://127.0.0.1:8765/status >/dev/null
fi

echo "=== status ==="
python -m json.tool < obs/state.json | head -40

MODEL="${CODEX_MODEL:-gpt-6-astra}"
EFFORT="${CODEX_EFFORT:-medium}"
SUMMARY="${CODEX_REASONING_SUMMARY:-auto}"
echo "launching Codex model=$MODEL effort=$EFFORT summary=$SUMMARY"

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
  "$(cat "$ROOT/PROMPT.txt")"
