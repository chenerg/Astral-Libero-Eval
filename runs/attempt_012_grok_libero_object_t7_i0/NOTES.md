# attempt_012 — FAIL (max_moves)

Grok policy. 30 moves, 372 env steps, 2030 s. Official `check_success()` false, reason `max_moves`.

Instruction: pick up the milk and place it in the basket.

`ctrl/` and `steps.jsonl` both exist (per-step 20 Hz archive).

Story:
- Scene is floor manipulation (wood plank, home EEF z≈0.26), not the kitchen table. Milk is the tall carton with the orange “Milk” / cow face, image-right of agentview; basket is image-left. Never went to the basket.
- Hovered over the carton at xy≈(−0.09, −0.21), 15–18° pitch, z≈0.09–0.12. Identified it correctly; did not pick bowls, cans, or the basket.
- Five in-place closes (m10, m17, m22, m28, m30) were empty (g=0.05). One close (m13, xy≈(−0.08, −0.211), z=0.098, pitch 18°) was `holding_or_pinching` g=0.17; the 2 cm test lift dropped to g=0.02 and the carton stayed on the floor (corner/gable pinch, not a body wrap).
- 18° pitch at grasp height hid the carton from the wrist (pads looked at empty floor / butter). Agentview “jaws on milk” with open fingers was treated as alignment; the left pad sat on the near “Milk” face while the closing axis was to the right. Same overlay-miss as spatial/2 bowls.
- Spent many moves hunting y at z≈0.09–0.12. High wrist views (z≈0.16, pitch 10°) still showed the carton on the left pad; descending from those xy hit the cap (blocked z≈0.12) instead of sliding the pads down the walls. First real contact only at m13, not by ~move 12. Pickup never happened.

What to reuse on milk/carton tasks:
- Floor workspace: close around z≈0.08–0.10 (body of ~11 cm carton). Do not use kitchen bowl z≈0.91 or “z≥0.82”.
- A 0.17 close that thins to 0.02 on a 2 cm lift is a corner/cap miss. Real body wrap of this carton should hold g≳0.40 (5.3 cm / 8 cm span).
- Set y from a high wrist view (z≥0.16, pitch ≤10°) with the carton *between* the pads, then descend on that xy with a 2–3 cm −x offset so 15–20° pads meet the walls, not the cap. Do not hunt y at z≈0.09 using agentview overlays.
- Open-jaw overlay ≠ contact. g=0.05 after an in-place close means pads in front or on one face — change xy (usually +y on this init, carton was left of the jaws), keep pitch; get g≳0.20 by ~move 12 and a 2 cm lift that still shows the carton in the wrist.
