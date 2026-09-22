# attempt_024 — SUCCESS (20 /move)

Instruction: open the middle drawer of the cabinet.
Official success: true. reason=success.
20 POST /move, 186 env steps, 262.21 s. remaining_moves=5 at terminate. Not a usage-limit/quota error. Codex exit 0, ~54.7k tokens.

Prompt: PROMPT_BASE_2.txt with {{LESSONS}} replaced by “(no extra accumulated lessons)”. Close-now check (“close now would trap the object”) and collision-avoid (“would collide” / never send a Cartesian target that would collide) kept from BASE_2. compose_prompt.py was not run. LESSONS.md was not injected. LIBERO_MAX_MOVES=25. LIBERO_WORLD_AXES=0 (world_axes_overlay=false). Planner astra, Codex gpt-6-astra medium.

Story: Kitchen-table scene. Reset at home eef ≈ (−0.217, 0.009, 1.171), gripper_open 0.517, jaws-down. Mandatory +x 3 cm probe (m01) confirmed +x → agentview BOTTOM. Cabinet is image-right with three horizontal handles. Open-jaw −y 10 cm then +x 10 cm at z≈1.17 (m02–m03) through clear space in front of the cabinet. Side-approach roll in 20° steps to −90° (m04–m08) with pitch/yaw returned to 0. Lower 10 cm (m09) to z≈1.057, then +x 8 cm and a combined +x 5.5 / −z 3.5 cm (m10–m11) to align along the middle handle at ≈(0.021, −0.071, 1.024). Five small −y inserts (m12–m16, 2/2/2/2/1.5 cm) until the bar sat between the pads. m17 close-check was “yes”; gripper=0 settled at g=0.228. 2 cm +y test pull (m18) kept g=0.228 and the drawer followed; two 8 cm +y pulls (m19–m20) opened it. Official success on m20. Final eef ≈ (0.027, 0.009, 1.019), roll ≈ −90°, g=0.228. Agentview after the last pull shows the middle drawer open; top and bottom drawers stay closed. All 20 moves reported reached/ok; no blocked/contact.

20 /move actually happened (budget 25). Targeted the middle drawer handle, not the top or bottom. gripper=0 only on m17–m20 after the bar was between both pads. Drawer opened (official success). WORLD_AXES=0.
