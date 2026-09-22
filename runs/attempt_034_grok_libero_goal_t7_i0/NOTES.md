# attempt_034 — SUCCESS (19 /move)

Launcher vs policy: this session is the episode launcher only. Nested Grok CLI (`grok --prompt-file PROMPT.txt --always-approve --verbatim --cwd astra_eval --max-turns 250 --disallowed-tools Agent`) was the robot policy and issued every POST /move. Launcher did not POST /move or GET /status except to confirm the bridge was up. grok_exit:0. Nested grok-4.7. Not a usage-limit/quota error.

Instruction: turn on the stove.
Official success: true. reason=success.
19 POST /move, 177 env steps, 1084.72 s. remaining_moves=6 at terminate.

Prompt: PROMPT_BASE_2.txt with {{LESSONS}} replaced by “(no extra accumulated lessons)”. Close-now check and collision-avoid kept from BASE_2. compose_prompt.py was not run. LESSONS.md was not injected. LIBERO_MAX_MOVES=25. Planner grok. LIBERO_WORLD_AXES=1 on BOTH cameras (agentview.png and wrist.png translucent XYZ triads; world_axes_overlay=true from reset through last frame).

Story: Kitchen-table scene. Reset at home eef ≈ (−0.213, −0.003, 1.187), gripper_open 0.517, jaws-down. World-axes overlay on both cameras. Mandatory +x 3 cm probe confirmed +x → agentview BOTTOM. Open-jaw +y then −x/+y to the black stove lever behind the burner. A slide that stayed too far −x left the lever high in the wrist (under the palm); raised a few centimetres and slid +x so the lever sat between the fingertips. Closed at measured z≈0.962; gripper_open stayed 0.306 (real pinch). Named gripper=0 on every later call. In-place yaw −20, then −40, then toward −60 turned the lever. Official success on m19 at measured yaw=−48.9°. Final eef ≈ (−0.415, 0.200, 0.961), roll≈−0.6°, yaw≈−48.9°, g=0.402. All 19 moves reported reached/ok; no blocked/contact.

19 /move actually happened (budget 25). Targeted the stove lever, not the burner. gripper=0 from m16–m19 after a real pinch (g≈0.31–0.40). Stove turned on (official success). WORLD_AXES=1 both cameras.
