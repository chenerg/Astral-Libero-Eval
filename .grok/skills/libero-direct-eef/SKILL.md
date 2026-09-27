---
name: libero-direct-eef
description: >
  Run LIBERO Direct-EEF sim evals from /home/chener/LIBERO/astra_eval: parent
  spawns a launcher subagent; Codex gpt-6-astra (clean = no Codex system prompt)
  or nested grok-4.7 is the policy; the launcher never POSTs /move. Use when the
  user asks to run LIBERO evals, Astra/Codex or Grok robot tests, clean Codex,
  clean Grok, run_episode_clean, run_episode_grok_clean, libero_spatial/object/goal
  episodes, world axes, PROMPT_BASE_3, PROMPT_BASE_2, or 开 subagent 跑仿真.
---

# LIBERO Direct-EEF eval

Root: `/home/chener/LIBERO/astra_eval`. Env: `conda activate libero`, `MUJOCO_GL=egl`.

## Roles (do not collapse)

| Role | Who | Allowed |
|---|---|---|
| Parent | this session | pick suite/task, spawn **one** launcher, wait, archive `EXPERIMENT.md` + `runs/index.jsonl` |
| Launcher | general-purpose subagent, `isolation: none` | write `PROMPT.txt`, `start_bridge.sh`, start Codex or nested Grok, NOTES, `analyze_run.py`, kill **this** bridge |
| Policy | `codex exec` or `grok --prompt-file` | `GET /status`, read `obs/*.png` + `obs/state.json`, `POST /move` or `/give_up`. Codex also reads the one attempt named by `LIBERO_HISTORY_RUN` when that variable is set |

Parent never runs `codex exec`, `grok --prompt-file`, `run_episode.sh`, `run_episode_clean.sh`, or `run_episode_grok_clean.sh`. Launcher never POSTs `/move`. One bridge at a time (port 8765). Astra default is **clean** (`run_episode_clean.sh`). Grok default is **clean** (`run_episode_grok_clean.sh`).

Default prompt for new ablations: **`PROMPT_BASE_3.txt`**, copied into `PROMPT.txt`. It has no `{{LESSONS}}` placeholder. Do **not** run `compose_prompt.py` unless the user asks to inject `LESSONS.md`. Images are always saved `img[::-1, ::-1]` (rot180). Success is only `env.check_success()`.

## Env vars

```bash
cd /home/chener/LIBERO/astra_eval
export LIBERO_SUITE=libero_goal          # libero_spatial | libero_object | libero_goal | libero_10 | libero_90
export LIBERO_TASK_ID=0
export LIBERO_INIT_ID=0
export LIBERO_PLANNER=astra              # astra | grok
export LIBERO_MAX_ENV_STEPS=600
export LIBERO_WORLD_AXES=0               # 1 = RGB triad on agentview AND wrist
export LIBERO_HISTORY_RUN=                # empty. One past attempt, only when this Codex run should read it
```

Planner `/move` budget (`LIBERO_MAX_MOVES`) is **50** for every suite (`libero_spatial`, `libero_object`, `libero_goal`, `libero_10`, `libero_90`), unless the user overrides. Physics steps stay `LIBERO_MAX_ENV_STEPS=600`.

```bash
export LIBERO_MAX_MOVES=50
```

`start_bridge.sh` names the run `runs/attempt_NNN_<planner>_<suite>_t<id>_i<init>/`. Confirm `obs/state.json` `remaining_moves` is 50. Nested Grok `--max-turns 250` still covers 50 moves.

## Prompt file (launcher)

When `LIBERO_HISTORY_RUN` is set, skip this snippet and run `run_episode_clean.sh`. That script writes the one designated attempt into `PROMPT.txt` before the bridge copies it.

```bash
python3 - <<'PY'
from pathlib import Path
import os
p = Path("/home/chener/LIBERO/astra_eval/PROMPT_BASE_3.txt").read_text()
if os.environ.get("LIBERO_WORLD_AXES", "0").strip().lower() in ("1", "true", "on"):
    p = (
        "LIBERO_WORLD_AXES=1: BOTH obs/agentview.png AND obs/wrist.png have a "
        "translucent world XYZ triad (red=+X, green=+Y, orange/blue=+Z). "
        "World xyz in /move does not flip.\n\n" + p
    )
Path("/home/chener/LIBERO/astra_eval/PROMPT.txt").write_text(p)
PY
bash start_bridge.sh
cp -f PROMPT.txt "$LIBERO_RUN_DIR/PROMPT.txt"
```

Wait for `bridge ready`. Confirm `obs/state.json` instruction, `remaining_moves`, and `world_axes_overlay`.

## Policy: Codex Astra — clean (default)

Clean = **PROMPT_BASE_3 is the system prompt**. Codex must not keep its built-in “You are Codex…” developer instructions, skills, plugins, AGENTS.md, or apps/permissions/collaboration/environment wrappers.

Launcher shortcut (still not the parent):

```bash
bash /home/chener/LIBERO/astra_eval/run_episode_clean.sh
```

That script writes `PROMPT.txt` from `PROMPT_BASE_3`, starts the bridge, then:

```bash
CLEAN_HOME=$(mktemp -d /tmp/codex-clean-XXXX)
ln -s /home/chener/.codex/auth.json "$CLEAN_HOME/auth.json"
ln -s /home/chener/.codex/models_cache.json "$CLEAN_HOME/models_cache.json"
ln -s /home/chener/.codex/config.toml "$CLEAN_HOME/config.toml"
ln -s /home/chener/.codex/sessions "$CLEAN_HOME/sessions"
export CODEX_HOME="$CLEAN_HOME"

codex exec \
  -m gpt-6-astra \
  -c 'model_reasoning_effort="medium"' \
  -c 'model_instructions_file="/home/chener/LIBERO/astra_eval/PROMPT.txt"' \
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
  -C /home/chener/LIBERO/astra_eval \
  -i /home/chener/LIBERO/astra_eval/obs/agentview.png \
  -i /home/chener/LIBERO/astra_eval/obs/wrist.png \
  -o "$LIBERO_RUN_DIR/LAST_MESSAGE.md" \
  "The two attached images are the reset obs/agentview.png and obs/wrist.png. Begin the episode now."
```

Key difference vs default Codex: **do not** `< PROMPT.txt` as the user message. That leaves the stock system prompt in place. Clean uses `model_instructions_file=PROMPT.txt` and a one-line user kickoff. Isolated `CODEX_HOME` without `skills/` or `plugins/` so the process cannot load the host skill catalog.

`LIBERO_HISTORY_RUN` stays empty unless the user names one past episode for this Codex run. Pass an attempt directory name (`attempt_060_libero_10_t8_i0`), a number (`60`), or `current`. `run_episode_clean.sh` then puts that single directory at the top of `PROMPT.txt` and in the kickoff, and tells Codex not to open any other `runs/attempt_*`. Do not set it on every episode. Grok clean ignores it. The quoted kickoff above is the no-history line; with the variable set, the script inserts `Designated prior episode: <path>` and tells Codex to read that directory's `NOTES.md`, `AGENT_SUMMARY.md`, and `result.json` before the first move.

Quota: stop the bridge, NOTES with the error, do not retry.

## Policy: Codex Astra — stock system prompt (only if the user asks)

Do not put the prompt after `-i`. Stdin is the **user** message; Codex still injects “You are Codex…”.

```bash
codex exec \
  -m gpt-6-astra \
  -c 'model_reasoning_effort="medium"' \
  --dangerously-bypass-approvals-and-sandbox \
  --skip-git-repo-check \
  -C /home/chener/LIBERO/astra_eval \
  -i /home/chener/LIBERO/astra_eval/obs/agentview.png \
  -i /home/chener/LIBERO/astra_eval/obs/wrist.png \
  < /home/chener/LIBERO/astra_eval/PROMPT.txt
```

`bash run_episode.sh` is this path plus `compose_prompt.py` (injects `LESSONS.md`). Use only when the user wants the stock Codex wrapper.

## Policy: nested Grok — clean (default)

Clean = **PROMPT_BASE_3 is the system prompt**. Do not keep Grok’s default system prompt, user/project skills (including `libero-direct-eef`), memory, web search, or subagents.

Launcher shortcut (still not the parent):

```bash
bash /home/chener/LIBERO/astra_eval/run_episode_grok_clean.sh
```

That script starts the bridge then:

```bash
CLEAN_HOME=$(mktemp -d /tmp/grok-clean-XXXX)   # no skills/ — only auth + empty config
POLICY_CWD=$(mktemp -d /tmp/grok-policy-cwd-XXXX)  # not astra_eval, so project skills are not scanned
export GROK_HOME="$CLEAN_HOME"

grok -p "Begin the episode now. Read …/obs/agentview.png and …/obs/wrist.png, GET /status, then POST /move until success or terminated." \
  --system-prompt-override "$(cat /home/chener/LIBERO/astra_eval/PROMPT.txt)" \
  -m grok-4.7 \
  --verbatim --always-approve --no-subagents --disable-web-search \
  --disallowed-tools "Agent" \
  --cwd "$POLICY_CWD" \
  --max-turns 250
```

`--system-prompt-override` replaces the default Grok system prompt and skips `--rules`. Isolated `GROK_HOME` has no `skills/`. `--cwd` is an empty temp dir so `astra_eval/.grok/skills` is not discovered. Do **not** `--cwd` astra_eval and `--prompt-file PROMPT.txt` — that leaves the stock Grok prompt and loads this eval skill into the policy.

`run_episode_grok_clean.sh` copies `$GROK_HOME/sessions` to `$LIBERO_RUN_DIR/grok_session/` before it deletes the temp home. Layout matches `~/.grok/sessions/<encoded-cwd>/<session-id>/`. Leave that copy in the run dir.

## Policy: nested Grok — stock (only if the user asks)

```bash
grok --prompt-file /home/chener/LIBERO/astra_eval/PROMPT.txt \
  -m grok-4.7 \
  --always-approve --verbatim \
  --cwd /home/chener/LIBERO/astra_eval \
  --max-turns 250 \
  --disallowed-tools "Agent"
```

This still injects the default Grok system prompt and project skills. Use only for comparison against clean.

## After the policy exits (launcher)

1. `NOTES.md` in the run dir: instruction, success, 8–15 line story, prompt file, MAX_MOVES, WORLD_AXES, planner, and `LIBERO_HISTORY_RUN` if set.
2. `python3 /home/chener/LIBERO/astra_eval/analyze_run.py "$LIBERO_RUN_DIR"`
3. `kill $(cat /home/chener/LIBERO/astra_eval/logs/bridge.pid); fuser -k 8765/tcp || true`
4. Return run dir, `result.json` fields, NOTES, 3 bullets. Do not edit `LESSONS.md` unless the parent asked.

## After the launcher returns (parent)

1. Confirm 8765 is down.
2. Append one line to `runs/index.jsonl` and a row to `EXPERIMENT.md`.
3. Next episode only after the previous bridge is dead. Sequential tasks = sequential launchers (or one launcher that loops start→policy→kill).

## HTTP contract (for policy prompts)

- `GET http://127.0.0.1:8765/status`
- `POST /move` JSON: `x/y/z` or `dx/dy/dz`, optional `roll_deg/pitch_deg/yaw_deg`, `gripper` `1=open 0=closed`, `note`
- `POST /give_up` `{"reason":"..."}`
- Unnamed axes hold. After a close, name `gripper=0` on lifts. Official success is `state.json` `success` only.

## Artifacts

`PROMPT.txt`, `transcript.jsonl`, `result.json`, `frames/` (one pair per `/move`), `ctrl/` + `steps.jsonl` (every 20 Hz step), `codex.log` or `grok.log`, `grok_session/` (clean Grok session copied out of the temp home), `NOTES.md`.
