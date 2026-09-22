# attempt_013 — FAIL (max_moves)

Grok policy. Prompt was PROMPT_BASE_2 with no lessons. MAX_MOVES=15.
15 moves, 136 env steps, 999.74 s. Official `check_success()` false, reason `max_moves`.

Instruction: pick up the milk and place it in the basket.

Story:
- Floor scene (libero_object). Home EEF ≈ (−0.15, −0.01, 0.26). Basket image-left in agentview; never approached it.
- Axis probe +x 3 cm: gripper moved toward BOTTOM of agentview (cheat sheet confirmed). +y = LEFT of agentview.
- Mis-ID: chased the blue “Farmers Cheese” carton (center cluster) instead of the tall orange milk carton on the image-right. All 15 moves were around cheese/butter/ketchup. Milk was never the grasp target.
- High-z xy hunt (m2–m5) overshot +x then +y onto butter. Descend at z=0.15 (m6) showed cheese still upper in the wrist with empty floor between the pads.
- Best overlay was around xy≈(−0.05, −0.03) at z≈0.10–0.15 (m7, m9, m12): cheese large in the upper wrist, ketchup at the right pad, floor at the fingertips. Agentview “gripper over carton” was the body projection, not the floor point — pads were still +x of the object.
- m13 descended to z=0.05 and drifted onto butter. m14 raised to z=0.08 and shifted toward cheese. m15 last-move close at z=0.045, xy≈(−0.032, −0.054): `gripper_open=0.05` (empty), cheese still on the floor in both cameras. No lift, no transport.

What went wrong (this episode only; not writing LESSONS.md):
- Wrong object (cream cheese vs milk) burned the 15-move budget before any carton-body wrap.
- Wrist-upper + empty pads means the floor projection is past the object; do not close from an agentview overlay. g=0.05 after close is empty — no 2 cm lift was even possible on the last move.
