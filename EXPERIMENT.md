# LIBERO × Codex CLI GPT-6 Astra — 单任务实验记录

Date: 2026-09-20  
Machine: WSL, `conda activate libero`, `MUJOCO_GL=egl`, NVIDIA RTX 3080 Laptop  
Code: `/home/chener/LIBERO/astra_eval`

可汇报整理（配置、时间线、结果、Astra vs Grok、世界轴）：[`REPORT.md`](REPORT.md)（覆盖 2026-09-20–21）。本文件仍是逐局流水账。

---

## 1. Method

### 1.1 Question

GPT-6 Astra, reached **only** through local Codex CLI (`codex exec -m gpt-6-astra`), can it close the loop on one official LIBERO sim task: RGB in, Cartesian targets out, LIBERO `check_success()` as the only success bit?

This is RoboProbe **L3 / Direct-EEF** (survey method A): no VLA, no demonstration, no object pose, no depth.

### 1.2 Task

| Field | Value |
|---|---|
| Suite | `libero_spatial` |
| Task id | 0 |
| Init id | 0 of 50 official init states |
| Instruction | pick up the black bowl between the plate and the ramekin and place it on the plate |
| Robot | Panda, robosuite 1.4 `OSC_POSE`, 20 Hz, action dim 7 |
| Cameras | `agentview` + `robot0_eye_in_hand`, 256×256 RGB. Bridge always saves `img[::-1, ::-1]` (arm at top of agentview, table/objects at bottom). |
| Success | `env.check_success()` only |
| Budget | 600 env steps (official), 30 planner moves |

Official LIBERO protocol is 20 inits × 600 steps. This run is **one episode**.

### 1.3 Harness

`bridge_server.py` holds one `OffScreenRenderEnv` and serves:

- `GET /status`
- `POST /move` `{x,y,z,gripper,note}` — unnamed axes keep the current EEF
- `POST /give_up`

Interpolation: world-frame XYZ → OSC_POSE deltas (0.05 m per unit). Gripper `1=open, 0=closed`. Orientation is **held** (no yaw/pitch/roll tool). After `set_init_state`, 5 zero actions settle physics (LIBERO eval does the same).

Planner observations:

- `obs/agentview.png`, `obs/wrist.png`
- EEF xyz, gripper open fraction, remaining budgets, language instruction
- **Not** provided: object names, 6D poses, BDDL, reward

Planner: Codex CLI `gpt-6-astra`, `reasoning_effort=medium`, `reasoning_summary=auto`, `danger-full-access`. Prompt on stdin (Codex `-i` is variadic and will swallow a positional prompt). Override with `CODEX_REASONING_SUMMARY=none|concise|detailed`.

### 1.4 Attempt 1 — harness abort, not a policy score

ThreadingHTTPServer ran `/move` off the MuJoCo/EGL thread. Cameras went black after the first motion. Gripper sign was inverted (`+1` closes on this Panda). Astra gave up at 2 moves / 27 steps. Artifacts: `runs/spatial0_init0_attempt1/`.

Fixes: `HTTPServer` (single thread); gripper `+1` close / `-1` open. Sanity move kept image ~77 kB and `gripper=1` → open 0.95.

---

## 2. Run log

| Run | What it is | Success | Moves / steps | Notes | Dir |
|---|---|---|---|---|---|
| 1 | harness bug | — | 2 / 27 | EGL thread + inverted gripper, black cameras | `runs/spatial0_init0_attempt1/` |
| 2 | first policy | no | 24 / 373 | 4× same-height top-down close | `runs/spatial0_init0_attempt2/` |
| 3 | ori bug + Codex abort | — | 1 / 17 | regulating unnamed rpy twisted wrist; Codex exited | `runs/attempt_003_libero_spatial_t0_i0/` |
| 4 | policy + pitch | no | 27 / 426 | pinch then 6–7 cm lift slips | `runs/attempt_004_libero_spatial_t0_i0/` |
| **5** | **policy + 2 cm test-lift** | **yes** | **29 / 466** | 15° pitch, short lift, regrasp, place | `runs/attempt_005_libero_spatial_t0_i0/` |
| 6 | spatial/1 init0 (subagent) | no | 28 / 377 | rim chase; unnamed gripper opened a 0.71 pinch | `runs/attempt_006_libero_spatial_t1_i0/` |
| 7 | spatial/2 init0 (subagent) | abort | 7 / 125 | Codex ChatGPT usage limit; last close on stove | `runs/attempt_007_libero_spatial_t2_i0/` |
| 8 | spatial/0 init0 **Grok policy** | no | 30 / 391 | Picked bowl, max_moves on plate; never opened | `runs/attempt_008_grok_libero_spatial_t0_i0/` |
| 9 | spatial/1 init0 **Grok policy** | no | 26 / 302 | 8 empty closes (g=0.05); never held; y-axis miss | `runs/attempt_009_grok_libero_spatial_t1_i0/` |
| 10 | spatial/2 init0 **Grok policy** | no | 30 / 321 | 9 empty closes; one rim graze g=0.11; never lifted | `runs/attempt_010_grok_libero_spatial_t2_i0/` |
| 11 | spatial/3 init0 **Grok policy** | abort | 17 / 210 | user stopped; approaching cookie-box bowl, never closed | `runs/attempt_011_grok_libero_spatial_t3_i0/` |
| 12 | object/7 init0 **Grok policy** rot180 | no | 30 / 372 | milk identified; one g=0.17 pinch slipped; never to basket | `runs/attempt_012_grok_libero_object_t7_i0/` |
| 13 | object/7 init0 Grok **PROMPT_BASE_2, no lessons**, 15 moves | no | 15 / 136 | chased Farmers Cheese not milk; one empty close g=0.05 | `runs/attempt_013_grok_libero_object_t7_i0/` |
| 14 | spatial/0 init0 Astra **PROMPT_BASE_2, no lessons**, 15 moves | abort | 0 / 5 | Codex GET /status then exit 0; no /move | `runs/attempt_014_astra_libero_spatial_t0_i0/` |
| 15 | spatial/0 init0 Astra **PROMPT_BASE_2, no lessons**, 15 moves | no | 12 / 166 | stayed in loop; two jaws-down empty lifts; give_up | `runs/attempt_015_astra_libero_spatial_t0_i0/` |
| **16** | spatial/0 init0 Astra **PROMPT_BASE_2 + bowl rim-between-pads**, 25 moves | **yes** | **19 / 198** | 15° pitch, wrist check, 2 cm+7 cm lift, place still closed | `runs/attempt_016_astra_libero_spatial_t0_i0/` |
| 17 | object/7 init0 Astra **PROMPT_BASE_2**, 25 moves | no | 25 / 263 | picked milk (g≈0.67); opened on last move beside basket | `runs/attempt_017_astra_libero_object_t7_i0/` |
| 18 | object/7 **resume a17** Codex session + 20 moves | no | 19 / 455 | replay pose matched; carton on side; two empty regrasps; give_up | `runs/attempt_018_astra_resume_libero_object_t7_i0/` |
| 19 | object/0 init0 Astra **PROMPT_BASE_2** close-check+collision, 25 moves | no | 25 / 264 | alphabet soup; grasped; visual in basket; official success false | `runs/attempt_019_astra_libero_object_t0_i0/` |
| **20** | object/4 init0 Astra ketchup **PROMPT_BASE_2**, 25 moves | **yes** | **21 / 232** | neck grasp g≈0.42; lift; release in basket | `runs/attempt_020_astra_libero_object_t4_i0/` |
| 21 | object/4 init0 **Grok** ketchup **PROMPT_BASE_2**, 25 moves | no | 22 / 193 | two empty closes g=0.05; XY hunt; give_up | `runs/attempt_021_grok_libero_object_t4_i0/` |
| 22 | object/4 init0 **Grok** ketchup **WORLD_AXES=1**, 25 moves | no | 20 / 175 | axes on; +x probe matched red triad; two empty closes; give_up | `runs/attempt_022_grok_libero_object_t4_i0/` |
| 23 | object/4 **nested grok CLI** ketchup axes both cams, 25 moves | no | 23 / 207 | launcher≠policy; two empty closes g=0.05; give_up | `runs/attempt_023_grok_libero_object_t4_i0/` |
| **24** | goal/0 init0 Astra open middle drawer, axes off | **yes** | **20 / 186** | roll −90°, handle pinch, pull drawer | `runs/attempt_024_astra_libero_goal_t0_i0/` |
| 25 | goal/7 init0 Astra turn on stove, axes off | no | 24 / 224 | three empty knob closes; give_up | `runs/attempt_025_astra_libero_goal_t7_i0/` |
| **26** | goal/8 init0 Astra bowl on plate, axes off | **yes** | **25 / 246** | 15° wall grasp after two empty pinches; place on plate | `runs/attempt_026_astra_libero_goal_t8_i0/` |
| **27** | goal/7 retry Astra stove **WORLD_AXES=1** | **yes** | **20 / 200** | pinch z≈0.955 g≈0.32; −yaw turns stove on | `runs/attempt_027_astra_libero_goal_t7_i0/` |
| 28 | goal/0 nested Grok drawer **WORLD_AXES=1** | no | 25 / 334 | max_moves; drawer not opened | `runs/attempt_028_grok_libero_goal_t0_i0/` |
| **29** | goal/7 nested Grok stove **WORLD_AXES=1** | **yes** | **15 / 145** | nested grok CLI; stove on | `runs/attempt_029_grok_libero_goal_t7_i0/` |
| 30 | goal/8 nested Grok bowl on plate **WORLD_AXES=1** | no | 24 / 221 | two lip pinches; give_up | `runs/attempt_030_grok_libero_goal_t8_i0/` |
| **31** | goal/7 Astra stove **WORLD_AXES=1** | **yes** | **21 / 192** | empty pinches then open-jaw −yaw descent turns stove | `runs/attempt_031_astra_libero_goal_t7_i0/` |
| 32 | goal/8 Astra bowl on plate **WORLD_AXES=1** | no | 24 / 239 | grasped and carried; quota abort 1 move left; official success false | `runs/attempt_032_astra_libero_goal_t8_i0/` |

Index: `runs/index.jsonl`. Each run folder has `PROMPT.txt`, `transcript.jsonl`, `result.json`, `frames/` (one pair per planner `/move`), `ctrl/` + `steps.jsonl` (every 20 Hz control step: 7-D action + agentview/wrist), `codex.log`, `NOTES.md` or `AGENT_SUMMARY.md`. Older runs before this change only have `frames/` at `/move` boundaries.

### Attempt 5 result

Official success after 352 s. First placement was off-center; regrasped and lowered onto the plate on move 29.

---

## 2b. Results (attempt 2, kept for history)

Artifacts: `runs/spatial0_init0_attempt2/`

| Metric | Value |
|---|---|
| Official success | **False** |
| Termination | `give_up` after 3 empty lifts |
| Planner moves | 24 / 30 |
| Env steps | 373 / 600 |
| Wall clock | 359 s (~6.0 min) |
| Model | `gpt-6-astra` medium |
| Session | Codex `01a0bec6-d8b8-...` (see `codex.log`) |

Never reached the plate. The bowl stayed on the table. Nearby second bowl was slightly displaced during contact.

---

## 3. Policy execution analysis

### 3.1 Phase timeline

| Moves | Phase | What happened |
|---|---|---|
| 1–5 | Approach | Identified the correct bowl (between plate and ramekin). Flew from home `(-0.21, -0.01, 1.17)` to above the cluster `(-0.12, 0.21, 0.94)`, jaws open. Wrist view used for centering. |
| 6–7 | Grasp 1 | Closed at z≈0.94, lifted to z≈1.02. Bowl **did not come up**. Note: “target slipped”. |
| 8–13 | Grasp 2 | Reopened, recentered, closed at z≈0.95, lifted to 1.04. Empty again. |
| 14–19 | Grasp 3 | Same loop. Move 17 requested z=0.94 but interpolation burned **80 env steps** and drifted (collision / 1.2 cm stop). Empty lift. |
| 20–24 | Grasp 4 | Fourth close+lift, still empty. `give_up`. |

### 3.2 What the strategy did well

1. **Instruction following.** It picked the bowl *between* plate and ramekin, not the other black bowl or the ramekin.
2. **Closed-loop RGB.** Almost every note cites wrist-camera layout (“bowl high in the image”, “centered under jaws”) and then issues a small correction. This is the Inspect-EEF / Robocurve pattern.
3. **Procedure memory.** Approach → descend → close → vertical lift-check → if empty, reopen. It never tried to translate a failed grasp to the plate.
4. **Recovery intent.** After slip it did not freeze; it reacquired.

### 3.3 Why it failed (physical / control, not semantics)

1. **Grasp height is too high.** Closes at z ≈ 0.94–0.96. Tabletop objects in this scene sit lower. The fingers pinch above the rim or only graze it, so `gripper_open` goes 0.4 → 0.05 on lift while the bowl stays down. Astra *sees* the miss on the next wrist frame (good) but does not lower another 3–5 cm; it repeats the same height.
2. **No orientation tool.** Jaws stay world-down. A parallel-jaw bowl grasp usually needs the fingers beside the walls, not a vertical pinch on the rim. The model cannot pitch/yaw.
3. **Contact is invisible except as RGB.** No force, no “jaw width while holding object”. After close, `gripper_open=0.28–0.40` already hints the jaws did not fully close on a thin rim — a stronger harness would flag “empty/shallow grasp” before the lift.
4. **Interpolator stall.** Moves 11 and 17 asked for a few millimetres down, hit the 80-step cap, and **drifted in xy** (`-0.065 → -0.053`). That is the 1.2 cm “arrived” threshold fighting OSC against contact. Wasted 160 env steps on two calls.
5. **Wrist-frame vs world-frame.** Notes like “bowl above in the wrist image → move back” are sometimes the right world axis, sometimes not. Coarse approach worked; millimetre alignment did not.

This matches the RoboDojo Astra report: **semantic/spatial OK, physical contact weak.** LIBERO-Spatial/0 is exactly a contact-precision pick.

### 3.4 Agent self-report

`AGENT_SUMMARY.md` agrees: repeated RGB approaches, bowl shifted, lifts left it on the table, wants millimetre rim alignment next time.

### 3.5 What to change next (same task)

Harness:

- Expose **pitch/yaw** or a “top-down vs side grasp” flag.
- Return **jaw width + whether motion was collision-stopped**.
- If a `z` target is blocked, stop early and tell the planner “contact, delta_z remaining”.
- Flip or annotate camera axes in the prompt (`wrist +v` vs world `+y`).

Policy prompt:

- “If a lift leaves the object on the table, lower 2–4 cm before the next close; do not repeat the same z.”
- Cap retries of the identical close/lift template (it spent 4 cycles).

Eval:

- Keep this 1-episode log as a **failed contact case**, not a suite score.
- Next: same task, 3 inits, after the z/contact patch; then `libero_spatial` task 0–2.

---

## 4. How to rerun

```bash
conda activate libero
export MUJOCO_GL=egl
cd ~/LIBERO/astra_eval
# start bridge then Codex (do not pass the prompt after -i; use stdin)
python bridge_server.py
codex exec -m gpt-6-astra \
  -c 'model_reasoning_effort="medium"' \
  -c 'model_reasoning_summary="auto"' \
  -c 'model_supports_reasoning_summaries=true' \
  -c 'hide_agent_reasoning=false' \
  --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check \
  -C ~/LIBERO/astra_eval \
  -i obs/agentview.png -i obs/wrist.png \
  < PROMPT.txt
```
