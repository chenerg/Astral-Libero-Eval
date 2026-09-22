# attempt_037 — SUCCESS (15 /move)

Launcher vs policy: this session is the episode launcher only. Nested Grok CLI (`grok --prompt-file PROMPT.txt --always-approve --verbatim --cwd astra_eval --max-turns 250 --disallowed-tools Agent`) was the robot policy and issued every POST /move. Launcher did not POST /move or GET /status except to confirm the bridge was up. grok_exit:0. Nested grok-4.7. Not a usage-limit/quota error.

Instruction: turn on the stove.
Official success: true. reason=success.
15 POST /move, 145 env steps, 476.13 s. remaining_moves=10 at terminate.

Prompt: PROMPT_BASE_2.txt with {{LESSONS}} replaced by “(no extra accumulated lessons)”. Close-now check and collision-avoid kept from BASE_2. compose_prompt.py was not run. LESSONS.md was not injected. LIBERO_MAX_MOVES=25. Planner grok. LIBERO_WORLD_AXES=0 (no XYZ triad on PNGs; world_axes_overlay=false from reset through last frame).

Story: Kitchen-table scene. Reset at home eef ≈ (−0.213, −0.003, 1.187), gripper_open 0.517, jaws-down. No world-axes overlay. Probe +x 3 cm then +y toward the stove on the left of agentview. Open-jaw −x/+y to the black stove lever behind the burner, then stepped down to z≈0.96 with the handle between the pads. Closed at measured z≈0.963; gripper_open stayed 0.309 (real pinch). Named gripper=0 on every later call. Three in-place yaw −20° steps turned the lever. Official success on m15 at measured yaw=−53.8°. Final eef ≈ (−0.426, 0.195, 0.960), roll≈−0.7°, yaw≈−53.8°, g=0.441. All 15 moves reported reached/ok; no blocked/contact.

15 /move actually happened (budget 25). Targeted the stove lever, not the burner. gripper=0 from m12–m15 after a real pinch (g≈0.31–0.44). Stove turned on (official success). WORLD_AXES=0 both cameras.
