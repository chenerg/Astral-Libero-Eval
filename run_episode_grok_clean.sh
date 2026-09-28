#!/usr/bin/env bash
# Nested Grok policy with PROMPT_BASE_3 (or $LIBERO_PROMPT_BASE) as the *system* prompt.
# Strips Grok's default system prompt, user/project skills, memory, and
# subagents (same idea as run_episode_clean.sh for Codex).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export ROOT
cd "$ROOT"
source /home/chener/miniconda3/etc/profile.d/conda.sh
conda activate libero
export MUJOCO_GL=egl PYOPENGL_PLATFORM=egl
export LIBERO_SUITE="${LIBERO_SUITE:-libero_spatial}"
export LIBERO_TASK_ID="${LIBERO_TASK_ID:-0}"
export LIBERO_INIT_ID="${LIBERO_INIT_ID:-0}"
export LIBERO_MAX_ENV_STEPS="${LIBERO_MAX_ENV_STEPS:-600}"
export LIBERO_WORLD_AXES="${LIBERO_WORLD_AXES:-0}"
export LIBERO_PLANNER="${LIBERO_PLANNER:-grok}"
export LIBERO_MAX_MOVES="${LIBERO_MAX_MOVES:-50}"

python3 - << 'PY'
import os
from pathlib import Path
root = Path(os.environ["ROOT"])
base_name = os.environ.get("LIBERO_PROMPT_BASE", "PROMPT_BASE_3.txt").strip() or "PROMPT_BASE_3.txt"
base_path = root / base_name
if not base_path.is_file():
    raise SystemExit(f"prompt file not found: {base_path}")
text = base_path.read_text()
print("prompt base", base_path.name)
flag = os.environ.get("LIBERO_WORLD_AXES", "0").strip().lower()
if flag in ("1", "true", "on"):
    text = (
        "LIBERO_WORLD_AXES=1: BOTH obs/agentview.png AND obs/wrist.png have a translucent "
        "world XYZ triad (red=+X, green=+Y, orange/blue=+Z). Use them to check the coordinate "
        "cheat sheet. World xyz in /move does not flip.\n\n"
        + text
    )
(root / "PROMPT.txt").write_text(text)
print("wrote", root / "PROMPT.txt", "bytes", len(text))
PY

bridge_out=$(bash "$ROOT/start_bridge.sh")
printf '%s\n' "$bridge_out"
LIBERO_RUN_DIR=$(printf '%s\n' "$bridge_out" | awk '/\/runs\/attempt_[0-9]+_/{p=$0} END{print p}')
export LIBERO_RUN_DIR
if [[ ! -d "${LIBERO_RUN_DIR:-}" ]]; then
  echo "start_bridge did not report a run dir" >&2
  exit 1
fi
cp -f "$ROOT/PROMPT.txt" "$LIBERO_RUN_DIR/PROMPT.txt"

CLEAN_HOME=$(mktemp -d /tmp/grok-clean-XXXX)
POLICY_CWD=$(mktemp -d /tmp/grok-policy-cwd-XXXX)
ln -s /home/chener/.grok/auth.json "$CLEAN_HOME/auth.json"
ln -s /home/chener/.grok/models_cache.json "$CLEAN_HOME/models_cache.json"
cat >"$CLEAN_HOME/config.toml" <<'TOML'
[memory]
enabled = false
[subagents]
enabled = false
TOML
ln -s "$ROOT/obs" "$POLICY_CWD/obs"
export GROK_HOME="$CLEAN_HOME"

# Session files live under $GROK_HOME. Copy them out before the temp home is removed.
copy_grok_session() {
  [[ -n "${LIBERO_RUN_DIR:-}" && -d "${CLEAN_HOME:-}/sessions" ]] || return 0
  mkdir -p "$LIBERO_RUN_DIR/grok_session"
  cp -a "$CLEAN_HOME/sessions/." "$LIBERO_RUN_DIR/grok_session/"
  echo "grok session -> $LIBERO_RUN_DIR/grok_session"
}
cleanup_grok_home() {
  copy_grok_session || true
  rm -rf "$CLEAN_HOME" "$POLICY_CWD"
}
trap cleanup_grok_home EXIT

MODEL="${GROK_MODEL:-grok-4.7}"
echo "Grok clean $MODEL  run=$LIBERO_RUN_DIR world_axes=$LIBERO_WORLD_AXES moves=$LIBERO_MAX_MOVES"
: > "$ROOT/logs/grok.log"
grok -p "Begin the episode now. Read /home/chener/LIBERO/astra_eval/obs/agentview.png and /home/chener/LIBERO/astra_eval/obs/wrist.png, GET http://127.0.0.1:8765/status, then POST /move until success=true or terminated=true." \
  --system-prompt-override "$(cat "$ROOT/PROMPT.txt")" \
  -m "$MODEL" \
  --verbatim \
  --always-approve \
  --no-subagents \
  --disable-web-search \
  --disallowed-tools "Agent" \
  --cwd "$POLICY_CWD" \
  --max-turns 250 \
  > "$ROOT/logs/grok.log" 2>&1
echo "grok_exit:$?"
cp -f "$ROOT/logs/grok.log" "$LIBERO_RUN_DIR/grok.log" || true
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
    "launcher": "run_episode_grok_clean.sh",
}
with open(root / "runs" / "index.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(json.dumps(rec, indent=2))
PY
python3 "$ROOT/viz/build.py" --no-win >>"$ROOT/logs/viz_build.log" 2>&1 || true
