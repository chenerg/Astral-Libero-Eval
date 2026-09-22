# attempt_036 — FAIL (25 /move, max_moves)

Launcher vs policy: this session is the episode launcher only. Nested Grok CLI (`grok --prompt-file PROMPT.txt --always-approve --verbatim --cwd astra_eval --max-turns 250 --disallowed-tools Agent`) was the robot policy and issued every POST /move. Launcher did not POST /move or GET /status except to confirm the bridge was up. grok_exit:0. Nested grok-4.7. Not a usage-limit/quota error.

Instruction: open the middle drawer of the cabinet.
Official success: false. reason=max_moves.
25 POST /move, 371 env steps, 2453.74 s. remaining_moves=0 at terminate.

Prompt: PROMPT_BASE_2.txt with {{LESSONS}} replaced by “(no extra accumulated lessons)”. Close-now check and collision-avoid kept from BASE_2. compose_prompt.py was not run. LESSONS.md was not injected. LIBERO_MAX_MOVES=25. Planner grok. LIBERO_WORLD_AXES=0 (no XYZ triad on PNGs; world_axes_overlay=false from reset through last frame).

Story: Kitchen-table scene. Reset at home eef ≈ (−0.217, 0.009, 1.171), gripper_open 0.517, jaws-down. No world-axes overlay. Mandatory +x 3 cm probe confirmed +x → agentview BOTTOM. High-z approach to the cabinet while rotating in 20° steps to roll=−90, yaw=−90 (fingers above/below the horizontal middle handle). Two closes at z≈0.97–1.00, y≈−0.12 to −0.14, both finished empty (gripper_open≈0.05). Raising above z≈1.00 in that horizontal pose blocked even after backing off. A late roll=−110 tilt reached y≈−0.145, z≈1.002; the last close+drive stalled 3 cm short with jaws still open (g=0.976). Final eef ≈ (0.023, −0.145, 1.002), roll≈174.9°, pitch≈−75.9°, yaw≈93.0°, g=0.976. Drawer never moved.

25 /move actually happened (budget 25). Targeted the middle drawer handle, not the top. gripper=0 closes were empty (g≈0.05) or never finished (g=0.976). Drawer stayed shut (official fail). WORLD_AXES=0 both cameras.
