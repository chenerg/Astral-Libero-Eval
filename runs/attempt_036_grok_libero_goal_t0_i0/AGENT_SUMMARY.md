# open the middle drawer of the cabinet

Outcome: failed. `success=false` after 25/25 moves (371 env steps). Server result `reason=max_moves`. The middle drawer never moved.

## What was tried

Kitchen home was about (-0.22, 0.01, 1.17), jaws down, cabinet on the right of agentview. Probe `dx=+0.03` matched the cheat sheet: world +x is toward the BOTTOM of agentview, world +y toward the LEFT.

The cabinet front faces the table center (world +y). The middle handle is a horizontal bar along world x. The grasp pose that matches it is `roll=-90, pitch=0, yaw=-90`: fingers point world -y (into the face) and open along world z (above and below the bar). Reported roll/pitch/yaw from the status euler readout does not match those commands; the quat did. At that pose the approach axis was (0, -1, 0) and the finger-opening axis was (0, 0, -1).

Approach path: free-space move to about (0.03, -0.04, 1.02) while rotating in 20 deg steps, then drive -y toward the face. Two closes at z≈0.97 and z≈0.995, y≈-0.12 to -0.14, both finished with `gripper_open≈0.05` (empty). The wrist showed the bar still above the pads.

Raising above z≈1.00 while the wrist was horizontal was blocked even after backing off to y≈-0.07 (`remaining_z` 2–4 cm, feedback `blocked/contact`). During that contact the jaws also stuck near `gripper_open≈0.50` and would not finish opening. Dropping to z=0.99 and restoring roll=-90 let the jaws open again (`gripper_open≈0.97`). A 20 deg upward tilt (`roll=-110`) lifted the eef to z≈1.00 and reached y≈-0.145. The last move commanded y=-0.175 and `gripper=0` together; it stalled with 3 cm of -y left and the jaws never closed (`gripper_open=0.976`). No pull was left in the budget.

## Why it failed

The bar was never between the pads at close time. Empty closes go to `gripper_open≈0.05`. A real pinch on the ~1.6 cm bar should stay near 0.15–0.25. The reachable horizontal pose on this side of the table tops out near z=1.00, and the bar sits just above that, so the upper pad kept hitting under the bar instead of surrounding it. The final close was paired with a translation that stalled, so the close dwell never ran.

## Hindsight

World +x is toward the BOTTOM of agentview, +y toward the LEFT. Kitchen table top ≈ 0.90, home z ≈ 1.17. Do not command z below ≈ 0.82.

Cabinet origin is about (0.03, -0.24) with yaw π. Drawer joint `middle_level` slides on local +y, range -0.16 to 0.01. Open means qpos < -0.14, which pulls the front toward world +y (table center) by about 15 cm. Middle handle is a horizontal bar along world x, about 9 cm long and 1.6 cm thick, on the face that points toward +y.

Set `roll=-90, yaw=-90, pitch=0` in free space (around x=0.03, y=-0.05) before touching the face. Ignore the status euler numbers; check the quat. If +z stalls near 1.00 at the face, tilt to `roll=-110` (approach gains +z, opening stays mostly vertical) while still ~8 cm in front, then step -y by 2 cm. Close only when the wrist shows the bar in the gap, and close with no translation so the dwell finishes. After a real pinch, `gripper_open` stays well above 0.05. Name `gripper=0` on the pull and move +y by at least 0.15 m.
