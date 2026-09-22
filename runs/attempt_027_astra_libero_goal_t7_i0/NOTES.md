# attempt_027 — SUCCESS (20 /move)

Retry of attempt_025 (WORLD_AXES=0, 24 /move, give_up, stove still off) with LIBERO_WORLD_AXES=1 on both cameras.

Instruction: turn on the stove.
Official success: true. reason=success.
20 POST /move, 200 env steps, 305.74 s. remaining_moves=5 at terminate. Not a usage-limit/quota error. Codex exit 0, ~83.1k tokens.

Prompt: PROMPT_BASE_2.txt with {{LESSONS}} replaced by “(no extra accumulated lessons)”, plus a WORLD_AXES header that both obs/agentview.png and obs/wrist.png carry a translucent world XYZ triad (red=+X, green=+Y, orange/blue=+Z). Close-now check (“close now would trap the object”) and collision-avoid (“would collide” / never send a Cartesian target that would collide) kept from BASE_2. compose_prompt.py was not run. LESSONS.md was not injected. LIBERO_MAX_MOVES=25. LIBERO_WORLD_AXES=1 (world_axes_overlay=true on agentview and wrist). Planner astra, Codex gpt-6-astra medium.

Story: Kitchen-table scene. Reset at home eef ≈ (−0.213, −0.003, 1.187), gripper_open 0.517, jaws-down. Mandatory +x 3 cm probe (m01) confirmed +x → agentview BOTTOM (axes overlay present on both views). Stove and black control sit image-left. Open-jaw +y 12 cm then combined −x/+y approach (m02–m04) to ≈(−0.370, 0.191, 1.183) above the control. Descend 10 cm, −x 3.5 / +y 1.2 cm, then 7/2/2/1.5 cm lowers (m05–m10) to z≈0.977 with the handle between open pads. First close (m11) at z≈0.975 with “close now would trap: yes”; gripper_open fell to 0.05 then 0.019 on +20° yaw (m12) — empty/shallow, lever did not turn. Reopened and reset yaw (m13), lowered 2 cm (m14) to z≈0.957. Second close (m15) at z≈0.955 held g=0.317 (handle in the gap). +20° yaw (m16) g=0.391, control did not turn (off-stop). Reversed −20° (m17) then two more −20° yaws (m18–m19) to yaw≈−40°. Final −20° yaw (m20) reached yaw≈−44°. Official success on m20. Final eef ≈ (−0.432, 0.194, 0.954), yaw ≈ −44°, g=0.386. All 20 moves reported reached/ok; no blocked/contact.

20 /move actually happened (budget 25). One empty/shallow close at z≈0.975 (g=0.05→0.019) then a retained pinch at z≈0.955 (g≈0.32–0.39). Negative world yaw turned the stove on (official success). WORLD_AXES=1 on both cameras.
