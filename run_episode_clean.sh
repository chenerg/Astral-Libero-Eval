#!/usr/bin/env bash
# Same episode as run_episode.sh, but the Codex system prompt is PROMPT_BASE_3
# instead of the built-in "You are Codex…" instructions.
# Skills, plugins, AGENTS.md, and the apps/permissions/collaboration/environment
# wrappers are turned off for this process only. Tool schemas stay.
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
export LIBERO_MAX_MOVES="${LIBERO_MAX_MOVES:-50}"
export LIBERO_MAX_ENV_STEPS="${LIBERO_MAX_ENV_STEPS:-600}"
# 1/true/on: translucent world XYZ triad at agentview and wrist centers. Default off.
export LIBERO_WORLD_AXES="${LIBERO_WORLD_AXES:-0}"

python3 - << 'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["ROOT"])
runs = root / "runs"

def resolve_history(spec: str):
    spec = (spec or "").strip()
    if spec.lower() in ("", "0", "off", "none", "false", "no"):
        return None
    found = []

    def add(path: Path):
        if not path.exists():
            return
        resolved = path.resolve()
        if resolved.parent != runs.resolve() or not resolved.name.startswith("attempt_"):
            return
        if resolved.is_dir() and resolved not in found:
            found.append(resolved)

    raw = Path(spec)
    if raw.is_absolute():
        add(raw)
    else:
        add(runs / spec)
        if spec.startswith("runs/"):
            add(root / spec)
        if (runs / spec).is_symlink():
            add(runs / spec)
        if spec.isdigit():
            for path in runs.glob(f"attempt_{int(spec):03d}_*"):
                add(path)
        else:
            for path in list(runs.glob(spec)) + list(runs.glob(spec + "*")):
                add(path)
            if not spec.startswith("attempt_"):
                for path in runs.glob("attempt_*" + spec + "*"):
                    add(path)
    if not found:
        raise SystemExit(f"LIBERO_HISTORY_RUN not found: {spec}")
    if len(found) > 1:
        names = "\n".join(path.name for path in found)
        raise SystemExit(f"LIBERO_HISTORY_RUN ambiguous:\n{names}")
    return found[0]

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
hist = resolve_history(os.environ.get("LIBERO_HISTORY_RUN", ""))
(root / "logs").mkdir(parents=True, exist_ok=True)
path_file = root / "logs" / "history_run.path"
if hist is None:
    path_file.write_text("")
    print("history run (none)")
else:
    meta = {}
    result_path = hist / "result.json"
    if result_path.exists():
        meta = json.loads(result_path.read_text())
    instruction = meta.get("instruction") or "(unknown)"
    success = meta.get("success")
    suite = meta.get("suite") or "?"
    task_id = meta.get("task_id", "?")
    init_id = meta.get("init_id", "?")
    text = (
        "指定历史记录（这一集只允许读这一个目录）：\n"
        f"路径：{hist}\n"
        f"场景：{suite} task_id={task_id} init_id={init_id}\n"
        f"instruction：{instruction}\n"
        f"success：{success}\n"
        "开场先读该目录里的 NOTES.md、AGENT_SUMMARY.md、result.json。"
        "需要动作细节再读 transcript.jsonl 和 frames/。"
        "不要打开其他 runs/attempt_*。\n"
        "这一集的官方指令以 obs/state.json 为准。"
        "若指定记录是别的任务，只借用操作经验，不要把那一集的目标当成这一集的目标。\n\n"
        + text
    )
    path_file.write_text(str(hist))
    print("history run", hist)
(root / "PROMPT.txt").write_text(text)
print("wrote", root / "PROMPT.txt", "bytes", len(text))
PY

n=0
for d in "$ROOT"/runs/attempt_*; do
  [[ -d "$d" ]] && n=$((n + 1))
done
for d in "$ROOT"/runs/spatial0_init0_attempt1 "$ROOT"/runs/spatial0_init0_attempt2; do
  [[ -d "$d" ]] && n=$((n + 1))
done
n=$((n + 1))
NAME=$(printf "attempt_%03d_%s_t%s_i%s" "$n" "$LIBERO_SUITE" "$LIBERO_TASK_ID" "$LIBERO_INIT_ID")
export LIBERO_RUN_DIR="$ROOT/runs/$NAME"
rm -rf "$ROOT/obs" "$ROOT/runs/current"
mkdir -p "$LIBERO_RUN_DIR/frames" "$ROOT/obs" "$ROOT/logs"
ln -sfn "$NAME" "$ROOT/runs/current"

# Auth and the model cache stay shared. skills/ and plugins/ are not linked, so
# this process does not load the Codex skill catalog from CODEX_HOME.
CLEAN_HOME=$(mktemp -d /tmp/codex-clean-XXXX)
ln -s /home/chener/.codex/auth.json "$CLEAN_HOME/auth.json"
ln -s /home/chener/.codex/models_cache.json "$CLEAN_HOME/models_cache.json"
ln -s /home/chener/.codex/config.toml "$CLEAN_HOME/config.toml"
ln -s /home/chener/.codex/sessions "$CLEAN_HOME/sessions"
export CODEX_HOME="$CLEAN_HOME"
trap 'rm -rf "$CLEAN_HOME"' EXIT

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
SUMMARY="${CODEX_REASONING_SUMMARY:-detailed}"
export HIST_PATH="$(cat "$ROOT/logs/history_run.path" 2>/dev/null || true)"
KICKOFF="The two attached images are the reset obs/agentview.png and obs/wrist.png. Begin the episode now."
if [[ -n "$HIST_PATH" ]]; then
  KICKOFF="The two attached images are the reset obs/agentview.png and obs/wrist.png. Designated prior episode: ${HIST_PATH}. Read NOTES.md, AGENT_SUMMARY.md, and result.json there before the first move. Begin the episode now."
fi
echo "Codex clean $MODEL $EFFORT summary=$SUMMARY  run=$LIBERO_RUN_DIR world_axes=$LIBERO_WORLD_AXES history=${HIST_PATH:-none}"
: > "$ROOT/logs/codex.log"
codex exec \
  -m "$MODEL" \
  -c "model_reasoning_effort=\"${EFFORT}\"" \
  -c "model_reasoning_summary=\"${SUMMARY}\"" \
  -c "model_supports_reasoning_summaries=true" \
  -c "hide_agent_reasoning=false" \
  -c "model_instructions_file=\"${ROOT}/PROMPT.txt\"" \
  -c include_permissions_instructions=false \
  -c include_apps_instructions=false \
  -c include_collaboration_mode_instructions=false \
  -c include_environment_context=false \
  -c project_doc_max_bytes=0 \
  -c 'personality="none"' \
  --disable multi_agent \
  --disable plugins \
  --disable apps \
  --enable skip_host_skill_discovery \
  --dangerously-bypass-approvals-and-sandbox \
  --skip-git-repo-check \
  -C "$ROOT" \
  -i "$ROOT/obs/agentview.png" \
  -i "$ROOT/obs/wrist.png" \
  -o "$LIBERO_RUN_DIR/LAST_MESSAGE.md" \
  "$KICKOFF" \
  > "$ROOT/logs/codex.log" 2>&1
echo "codex_exit:$?"
cp -f "$ROOT/logs/codex.log" "$LIBERO_RUN_DIR/codex.log" || true
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
    "launcher": "run_episode_clean.sh",
    "history_run": os.environ.get("HIST_PATH") or None,
}
with open(root / "runs" / "index.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(json.dumps(rec, indent=2))
PY
python3 "$ROOT/viz/build.py" --no-win >>"$ROOT/logs/viz_build.log" 2>&1 || true
