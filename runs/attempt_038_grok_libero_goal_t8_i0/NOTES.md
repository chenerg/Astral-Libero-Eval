# attempt_038 — SUCCESS (18 /move)

Launcher vs policy: this session is the episode launcher only. Nested Grok CLI (`grok --prompt-file PROMPT.txt --always-approve --verbatim --cwd astra_eval --max-turns 250 --disallowed-tools Agent`) was the robot policy and issued every POST /move. Launcher did not POST /move or GET /status except to confirm the bridge was up. grok_exit:0. Nested grok-4.7. Not a usage-limit/quota error.

Instruction: put the bowl on the plate.
Official success: true. reason=success.
18 POST /move, 183 env steps, 954.93 s. remaining_moves=7 at terminate.

Prompt: PROMPT_BASE_2.txt with {{LESSONS}} replaced by “(no extra accumulated lessons)”. Close-now check and collision-avoid kept from BASE_2. compose_prompt.py was not run. LESSONS.md was not injected. LIBERO_MAX_MOVES=25. Planner grok. LIBERO_WORLD_AXES=0 (no XYZ triad on PNGs; world_axes_overlay=false from reset through last frame).

Story: Kitchen-table scene. Reset at home eef ≈ (−0.207, 0.002, 1.179), gripper_open 0.517, jaws-down. No world-axes overlay. Mandatory +x 3 cm probe, then +x over the metal bowl and down. Pitched +15° and approached the +y rim so one pad was inside the bowl and one outside. Closed at z≈0.956; gripper_open settled ≈0.06 then ≈0.04 on lift (real rim pinch). Named gripper=0 on every later call. Lifted, carried +x to ≈(0.05, 0.04), leveled pitch to 0, then lowered onto the plate. Official success on m18 during the last descent. Final eef ≈ (0.051, 0.038, 0.973), roll≈−1.4°, yaw≈−1.5°, g=0.040. All 18 moves reported reached/ok; no blocked/contact.

18 /move actually happened (budget 25). Targeted the bowl rim then the plate. gripper=0 from m11–m18 after a real pinch (g≈0.04). Bowl on plate (official success). WORLD_AXES=0 both cameras.
