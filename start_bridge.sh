#!/usr/bin/env bash
# Start only the LIBERO Direct-EEF bridge (no Codex). For Grok-as-policy episodes.
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

n=0
for d in "$ROOT"/runs/attempt_*; do
  [[ -d "$d" ]] && n=$((n + 1))
done
for d in "$ROOT"/runs/spatial0_init0_attempt1 "$ROOT"/runs/spatial0_init0_attempt2; do
  [[ -d "$d" ]] && n=$((n + 1))
done
n=$((n + 1))
PLANNER="${LIBERO_PLANNER:-grok}"
NAME=$(printf "attempt_%03d_%s_%s_t%s_i%s" "$n" "$PLANNER" "$LIBERO_SUITE" "$LIBERO_TASK_ID" "$LIBERO_INIT_ID")
export LIBERO_RUN_DIR="$ROOT/runs/$NAME"
rm -rf "$ROOT/obs"
mkdir -p "$LIBERO_RUN_DIR/frames" "$ROOT/obs" "$ROOT/logs"
ln -sfn "$NAME" "$ROOT/runs/current"

if [[ -f "$ROOT/logs/bridge.pid" ]]; then
  kill "$(cat "$ROOT/logs/bridge.pid")" 2>/dev/null || true
fi
fuser -k 8765/tcp 2>/dev/null || true
sleep 1

python "$ROOT/bridge_server.py" >"$ROOT/logs/bridge.log" 2>&1 &
echo $! >"$ROOT/logs/bridge.pid"
for i in $(seq 1 45); do
  if curl -sf http://127.0.0.1:8765/status >/dev/null; then
    echo "bridge ready ($i) run=$NAME world_axes=$LIBERO_WORLD_AXES"
    echo "$LIBERO_RUN_DIR"
    exit 0
  fi
  sleep 1
done
echo "bridge failed to start" >&2
tail -30 "$ROOT/logs/bridge.log" >&2
exit 1
