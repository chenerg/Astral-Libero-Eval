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
export LIBERO_MAX_MOVES="${LIBERO_MAX_MOVES:-50}"
export LIBERO_MAX_ENV_STEPS="${LIBERO_MAX_ENV_STEPS:-600}"
# 1/true/on: translucent world XYZ triad at agentview and wrist centers. Default off.
export LIBERO_WORLD_AXES="${LIBERO_WORLD_AXES:-0}"

mkdir -p "$ROOT/logs"
# Refuse an occupied port before replacing observations or runs/current. Never
# terminate a process merely because it happens to own our usual port/PID file.
exec 9>"$ROOT/logs/bridge-start.lock"
flock -n 9 || { echo "another bridge startup is in progress" >&2; exit 1; }
python3 - <<'PY'
import socket
with socket.socket() as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("127.0.0.1", 8765))
    except OSError as exc:
        raise SystemExit(f"refusing to start: port 8765 is occupied ({exc})")
PY

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

python "$ROOT/bridge_server.py" 9>&- >"$ROOT/logs/bridge.log" 2>&1 &
bridge_pid=$!
echo "$bridge_pid" >"$ROOT/logs/bridge.pid"
echo "$bridge_pid" >"$LIBERO_RUN_DIR/bridge.pid"
bridge_ready=0
trap 'if [[ "$bridge_ready" == 0 ]]; then kill "$bridge_pid" 2>/dev/null || true; fi' EXIT
for i in $(seq 1 45); do
  kill -0 "$bridge_pid" 2>/dev/null || break
  if curl -sf http://127.0.0.1:8765/status >/dev/null; then
    bridge_ready=1
    echo "bridge ready ($i) run=$NAME world_axes=$LIBERO_WORLD_AXES"
    echo "$LIBERO_RUN_DIR"
    exit 0
  fi
  sleep 1
done
echo "bridge failed to start" >&2
tail -30 "$ROOT/logs/bridge.log" >&2
exit 1
