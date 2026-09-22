# attempt_008 — FAIL (max_moves)

Grok policy. 30 moves, 391 env steps, 1529 s. Official `check_success()` false, reason `max_moves`.

Instruction: pick up the black bowl between the plate and the ramekin and place it on the plate.

Story:
- Hovered over the rear bowl, 15° pitch, descended. Three close+2cm-lift cycles at z≈0.923–0.931, pitch 15–18°, xy near the attempt_005 grasp. Each close had gripper_open≈0.14 (no `holding_or_pinching`) and dropped to ≈0.07 on the test lift; bowl stayed on the table (rim pinch).
- Roll/yaw drifted to −6°; reset ori, still a 0.14 rim pinch.
- Changed strategy: −3 cm in x (toward robot), pitch 20°, close at z=0.915. That produced `holding_or_pinching` with open=0.25, which stayed 0.23 through a 2 cm lift and 0.23 through a 5.5 cm lift. Bowl visibly rose.
- Carried to the plate still holding. Side-wall grasp offset the bowl from the EEF, so attempt_005 place xy (≈0.07, 0.15) left it on the plate’s right edge. Spent remaining moves nudging +y onto the plate while still closed. Last pose (0.08, 0.22, 0.93), open=0.15, bowl overlapping the plate but not accepted. Never opened the jaws; hit 30-move cap.

What to reuse:
- A 0.14 close that thins to 0.07 on a 2 cm lift is a rim miss. Do not retry the same z/xy/pitch.
- Real wall grasp: ~20° pitch, ~3 cm −x from bowl center, z≈0.91–0.915, open≈0.25 that holds through the test lift.
- Side-wall grasp offsets the bowl vs a near-wall grasp; do not copy attempt_005 place xy blindly. Leave 4–6 moves after pickup to center and lower (success can trigger while still holding).
