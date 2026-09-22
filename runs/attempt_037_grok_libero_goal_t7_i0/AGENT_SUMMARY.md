# turn on the stove — success

Instruction: turn on the stove (libero_goal, task 7, init 0).

Result: success=true after 15 planner moves, 145 env steps. Final eef ≈ (−0.426, 0.195, 0.960), yaw=−53.8°, gripper_open=0.441. Official check flipped true on the third in-place negative yaw. All 15 moves reported reached/ok; no blocked/contact.

What I tried: Probed +x by 3 cm. The wrist view shifted toward the top of the wrist frame, matching +x toward the bottom of agentview, so the cheat sheet was kept. Open-jaw approach: +y 12 cm, then −x/+y to sit above the black control behind the burner at ≈(−0.370, 0.191, 1.183). Descended in steps (10 cm, then 7 cm, then 2 cm steps) with the handle kept between the open pads. Did not close at z=0.975 (known shallow tip). Closed at measured z=0.963; gripper_open stayed 0.309 (handle in the gap). Named gripper=0 on every later call. Three in-place −20° yaws (measured yaw −19.1°, −38.8°, −53.8°) turned the stove on. Jaw fraction rose 0.309 → 0.367 → 0.401 → 0.441 as the lever rotated, which is a held pinch, not an empty close.

Why it worked: the pinch was on the handle body, not the tip, and the fixed control was rotated in place instead of lifted.

Hindsight: World +x moves toward the bottom of agentview; +y moves left in agentview and right in wrist. No axis inversion needed. Kitchen table ≈0.90, home z≈1.187. The black stove lever sits behind the burner (more −x, y≈0.19). Pinch with reset jaws at eef z≈0.96; z≈0.975 is the tip and closes empty (g≈0.05). A real pinch holds g≈0.31–0.44. Turn the fixed handle in place; do not lift. Negative world yaw turns this control on (success near yaw −44° to −54°). The reach check stops around 1 cm short, so near the lever command a little past the desired xyz. These are observed end-effector poses, not independently measured object coordinates.
