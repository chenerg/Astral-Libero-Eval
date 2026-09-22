## Lessons (keep this section short; parent updates it after every run)

### General
- Do not stop after one blocked move. Raise, reset twist if needed, continue.
- Unnamed orientation holds the current pose. Never command 90° yaw in one call.
- After a close+lift, gripper_open≈0.02 means empty jaws. Next close: change xy/z/pitch.
- After a close, if the jaws did not fully shut, lift 2 cm only. If the object does not rise, go back down immediately. A 6–8 cm lift on a pinch slips.
- Wrist-image "up" is not world +y. Re-read both cameras after every move.
- Never transport to the goal until a 2 cm lift shows the object moving with the gripper.
- Home z is scene-dependent. Kitchen table ~1.17 (do not go below ~0.82). Floor object suite ~0.26; milk body close ~0.08–0.10. Read it from state.json.

### libero_object (milk → basket)
- Floor workspace, not the kitchen table.
- Close around the carton **body** at z≈0.08–0.10 with 15–20° pitch, not the cap (blocked ~z=0.12). A real wrap of this carton should hold **g≳0.40**; g=0.17 that drops to 0.02 on a 2 cm lift is a corner/gable pinch.
- Open-jaw overlay on the “Milk” face ≠ grasp. Set y from a high wrist view (z≥0.16, pitch ≤10°) with the carton *between* the pads, then descend with a 2–3 cm −x wall offset. Do not hunt y at grasp height.

### libero_spatial bowls (pick black bowl → plate)
- Parallel jaws need 10–20° pitch around the wall, not a vertical pinch on the rim.
- Close near the lowest reachable z (blocked ≈ on the rim). Typical close: ~15° pitch, z≈0.91–0.92, 2 cm test lift (open stayed ~0.16), then 5 cm more, then place. Off-center first drop → regrasp and nudge xy.
- After a pinch, **name `gripper=0` on every lift/transport**. Unnamed gripper can open the jaws and drop the pinch. Still name it.
- Wrist-centering ≠ contact. Bowl filling the wrist image often means the near rim is in the pads; that shoves the bowl. Put the wall *between* the pads.
- g≈0.02 after a 2 cm lift is empty. Change xy, keep 10–20° pitch; do not chase the rim in +x or use 30° at z<0.90.
- Close width ≈0.14 that drops to ≈0.07 on a 2 cm lift is a rim miss — do not retry that xy/z/pitch. Leave 4–6 moves after pickup to center; success can fire while still holding. If success is still false after the bowl is over the plate, OPEN (gripper=1). Do not spend remaining moves nudging while closed.
- After a close, judge left/right from **agentview**, not a full wrist image. g=0.05 + full wrist → step y then x until g≳0.14.
- If the target disappears *under* the gripper at grasp height, back off only 2–3 cm along the approach. A long retreat in x lands on the stove.
- Do not hunt y at low z with 20° pitch — the wrist is often blind and in-front side-peeks flip left/right. Set y from a high wrist view (z≥1.00, pitch ≤15°) with the bowl between the pads, then descend. Agentview open-jaw overlay ≠ grasp: the left pad can sit on the bowl while the closing axis misses.
- g≈0.7 and **no bowl in the wrist** is furniture contact (stove/table). Open and re-center; do not lift.
