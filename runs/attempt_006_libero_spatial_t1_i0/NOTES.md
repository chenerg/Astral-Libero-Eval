# attempt_006 — libero_spatial t1 i0, fail

Instruction: pick up the black bowl next to the ramekin and place it on the plate.
Policy run (harness OK). 28 moves, 377 env steps, 397 s, give_up. `check_success()` false. Never placed.

Correct object: the patterned black bowl beside the white ramekin (front-right), not the stove pan or the back silver bowl.

Approach: home → +y toward the right cluster, 15° pitch (lesson), then xy into the bowl at ~(-0.26, 0.31). Descend z 0.98 → 0.918.

Grasp 1 (m8–9): close at z=0.918, g=0.05, 2 cm test lift g=0.019. Empty. No `empty_grasp_suspected` (lift was only ~1 cm; that flag needs >4 cm). Wrist showed the bowl still on the table.

Grasp 2 (m13–15): close at z=0.921, `holding_or_pinching` g=0.71. Wrist filled with the bowl, pads on the near rim, not around the wall. Agent correctly lifted only 2 cm (LESSONS overrode the bridge string “lift 5–8 cm”). Gripper was unnamed on m14/m15, so the bridge copied g_cmd=0.71 ≥ 0.5 and commanded OPEN. Jaws 0.71 → 0.76 → 0.97; pinch gone.

Chasing (m16–25): empty closes at the same height (g=0.05, 0.058, 0.052) shoved the bowl +x toward the plate (EEF x −0.27 → −0.07). 30° pitch + z=0.893 blocked (m21); raised and reset pitch to 15° (lesson).

Grasp 3 (m26–28): 5° pitch, close z=0.91, 2 cm lift with explicit gripper=0, g=0.02. Empty. Bowl now sitting near the plate. Gave up with 2 moves left.

LESSONS that helped: 15° wall pitch; 2 cm test lift; do not haul to the plate without a verified rise; after blocked, raise and continue; ±20° ori cap (no 90° yaw).
LESSONS that failed / were incomplete: unnamed gripper does **not** hold a pinch when `gripper_open`≥0.5 — it opens. Wrist-centering ≠ jaw contact; rim-in-camera closes push the bowl. `empty_grasp_suspected` missed the first empty 2 cm lift.

Next on similar bowl→plate: name `gripper=0` on every lift/transport after a pinch; put the wall between the pads, not in the image center; if g≈0.02 or a too-open pinch (g≈0.7) at z≈0.92, change xy rather than chasing the rim in +x; keep 10–20° pitch, do not go 30° at z<0.90.
