# attempt_029 — SUCCESS (15 /move)

Launcher vs policy: this session is the episode launcher only. Nested Grok CLI (`grok --prompt-file PROMPT.txt --always-approve --verbatim --cwd astra_eval --max-turns 250 --disallowed-tools Agent`) was the robot policy and issued every POST /move. Launcher did not POST /move or GET /status except to confirm the bridge was up. grok_exit:0. Not a usage-limit/quota error.

Instruction: turn on the stove.
Official success: true. reason=success.
15 POST /move, 145 env steps, 493.87 s. remaining_moves=10 at terminate.

Prompt: PROMPT_BASE_2.txt with {{LESSONS}} replaced by “(no extra accumulated lessons)”. Close-now check and collision-avoid kept from BASE_2. compose_prompt.py was not run. LESSONS.md was not injected. LIBERO_MAX_MOVES=25. Planner grok. LIBERO_WORLD_AXES=1 on BOTH cameras (agentview.png and wrist.png translucent XYZ triads; world_axes_overlay=true from reset through last frame).

Story: Kitchen-table scene. Reset at home eef ≈ (−0.213, −0.003, 1.187), gripper_open 0.517, jaws-down. World-axes overlay on both cameras. Mandatory +x 3 cm probe confirmed +x → agentview BOTTOM. Open-jaw +y then −x/+y to sit above the black stove lever behind the burner at ≈(−0.370, 0.191, 1.183). Descended in steps with the handle kept between the open pads; skipped a close at the lever tip (z≈0.975). Closed at z≈0.963; gripper_open stayed 0.309 (real pinch, handle in the gap). Named gripper=0 on every later call. Three in-place −20° yaws to measured yaw=−53.8° turned the stove on. Official success on m15. Final eef ≈ (−0.426, 0.195, 0.960), roll≈−0.7°, yaw≈−54°, g=0.441. All 15 moves reported reached/ok; no blocked/contact.

15 /move actually happened (budget 25). Targeted the stove lever, not the burner. gripper=0 from m12–m15 after a real pinch (g≈0.31–0.44). Stove turned on (official success). WORLD_AXES=1 both cameras.
