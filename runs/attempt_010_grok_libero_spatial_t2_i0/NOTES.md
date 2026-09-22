# attempt_010 — FAIL (max_moves)

Grok policy. 30 moves, 321 env steps, 1435 s. Official `check_success()` false, reason `max_moves`.

Instruction: pick up the black bowl from table center and place it on the plate.

Story:
- Hovered over the center gray bowl (not stove, not silver bowl) at x≈0.03, y=0, z=1.06. Wrist showed the bowl between the pads. Pitched 20° and descended. Did not retreat onto the stove (a7 failure mode).
- Nine closes at z≈0.91–0.92, pitch 20°. Eight were empty (g=0.05/0.02). One rim graze (m16, x=0.044, y=-0.008, z=0.920, g=0.11) never became `holding_or_pinching`. Never lifted. Never went to the plate.
- 20° pitch at grasp height hid the bowl from the wrist (only the cookie box). Agentview “bowl under the gripper” with open jaws was treated as alignment; closing then missed. Open fingers span ~8 cm, so the left pad can overlay the bowl while the closing axis is to its right.
- Spent many moves hunting y at z=0.912. Tiny y changes flipped the bowl from fully-left to fully-right in agentview because the pads were often *in front* of the bowl (−x), not on the wall. First empty close already at m6; no g≳0.14 by move 12.

What to reuse:
- Stay within ~3 cm of the visible center bowl in x. Do not retreat onto the stove.
- Re-center y from a high wrist view (z≥1.00, pitch ≤15°) where the bowl sits between the pads. Do not hunt y at grasp height using agentview side-peeks.
- Open-jaw overlay in agentview ≠ contact. Close only after arriving (gripper-only close). g=0.05 after an in-place close at “overlay” xy means pads in the hollow or in front — change xy, do not retry.
- The only contact on this init was g=0.11 at x≈0.044, y≈-0.008, z≈0.920. Next run: get a real wall close (g≳0.20) by ~move 12 from that xy with a 1–2 cm −x offset, then 2 cm test lift.
