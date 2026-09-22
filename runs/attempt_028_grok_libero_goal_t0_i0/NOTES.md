# attempt_028 — FAIL (25 /move, max_moves)

Launcher vs policy: this session is the episode launcher only. Nested Grok CLI (`grok --prompt-file PROMPT.txt --always-approve --verbatim --cwd astra_eval --max-turns 250 --disallowed-tools Agent`) was the robot policy and issued every POST /move. Launcher did not POST /move or GET /status except to confirm the bridge was up. grok_exit:0. Not a usage-limit/quota error.

Instruction: open the middle drawer of the cabinet.
Official success: false. reason=max_moves.
25 POST /move, 334 env steps, 1142.98 s. remaining_moves=0 at terminate.

Prompt: PROMPT_BASE_2.txt with {{LESSONS}} replaced by “(no extra accumulated lessons)”. Close-now check and collision-avoid kept from BASE_2. compose_prompt.py was not run. LESSONS.md was not injected. LIBERO_MAX_MOVES=25. Planner grok. LIBERO_WORLD_AXES=1 on BOTH cameras (agentview.png and wrist.png translucent XYZ triads; world_axes_overlay=true from reset through last frame).

Story: Kitchen-table scene. Reset at home eef ≈ (−0.217, 0.009, 1.171), gripper_open 0.517, jaws-down. World-axes overlay on both cameras. Mandatory +x 3 cm probe confirmed +x → agentview BOTTOM. High-z −y toward the cabinet, then +x along the face. Descent blocked by the drying rack at z≈1.10. Cleared the rack with +x/+y, then dropped to z≈1.03 for the middle handle. Jaws-down −y approach hit the handle face-on (outer pad). Spent five moves yawing to 90° so pads would close along X, then approached ≈(−0.01, −0.09, 1.03) and closed twice. Both closes went to gripper_open≈0.05, then ≈0.018 on the +y pull — empty jaws; drawer never moved. Final eef ≈ (−0.000, 0.046, 1.030), roll≈0.9°, yaw≈90.4°, g=0.018. The horizontal handle needs roll ≈ −90° (fingers above/below the bar), not yaw 90°; a real pinch on this handle holds g≳0.20. Successful prior pose on this init ≈ (0.027, −0.132, 1.019), roll≈−90, g≈0.228, then pull +y. All 25 moves used; no remaining budget.

25 /move actually happened (budget 25). Targeted the middle drawer handle, not the top. gripper=0 closes were empty (g≈0.05/0.02). Drawer stayed shut (official fail). WORLD_AXES=1 both cameras.
