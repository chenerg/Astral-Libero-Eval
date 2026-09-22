# attempt_007 — libero_spatial t2 i0, abort (usage limit)

Instruction: pick up the black bowl from table center and place it on the plate.
Harness OK; Codex CLI died after 7 moves / 125 env steps / 124 s. `check_success()` false. Never lifted. `codex_exit` was 1 (`set -e` skipped the index write); tokens used 17384. Retry window: Sep 21st, 2026 12:31 AM.

Correct object: the small gray/black bowl in the open table center (between the left stove and the right silver bowl). Not the stove burner, not the far silver bowl.

Approach: home → x=0 z=1.06 (m1) → x=0.035 z=0.97 with 15° pitch (m2). Gripper was over the bowl (agentview: bowl hidden under the wrist). m3 descended to x=0.005 z=0.925; bowl reappeared just +x of the pads.

Retreat (m4–m6): agent treated “bowl obscured” as a cue to back off in −x. x −0.002 → −0.069 → −0.109, over the stove. Pitch stayed ~15°. Bowl sat untouched to the right of the hand.

Close (m7): gripper=0 at z=0.918, `holding_or_pinching` g=0.688. Wrist shows table + cookie box, no bowl. Pads closed on stove hardware, not the wall. Codex then hit the ChatGPT usage limit before the 2 cm test lift, so `gripper=0` on lift was never tested.

LESSONS that helped: 15° wall pitch from the first descent; close height ~z=0.92; named gripper=0 on the close itself.
LESSONS that failed / never ran: wrist-centering ≠ contact — here the opposite, losing the bowl in agentview caused an 8–12 cm −x retreat onto the stove. g≈0.69 + empty wrist is not a bowl pinch (same number as spatial/1 rim pinch, different object). Named-gripper-on-lift never executed.

Next on this init: keep xy within ~2 cm of the visible center bowl when it disappears under the gripper; do not retreat onto the stove. If g≈0.7 and the wrist has no bowl, open and re-center on the gray bowl. Do not start a second Codex until the usage window resets.
