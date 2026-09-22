# Trial summary

Instruction: turn on the stove (libero_goal, task 7, init 0).
Official state reported success=true after 15 moves and 145 physics steps, with 10 moves and 455 steps remaining. The HTTP result also reported termination for success.

Probed +x (agentview moved toward BOTTOM; cheat sheet confirmed). Open-jaw approach: +y 12 cm, then −x/+y to sit above the black control behind the burner at ≈(−0.370, 0.191, 1.183). Descended in steps with the handle kept between the open pads. Skipped a close at the lever tip. Closed at measured z=0.963; gripper_open stayed 0.309 (handle in the gap). Named gripper=0 on every later call. Three in-place −20° yaws to measured yaw=−53.8° turned the stove on. Final eef ≈ (−0.426, 0.195, 0.960), g=0.441. All 15 moves reported reached/ok; no blocked/contact.

Hindsight: World +x moves toward the bottom of agentview; +y moves left in agentview and right in wrist. No axis inversion needed. Kitchen table ≈0.90, home z≈1.187. The black stove lever sits behind the burner (more −x, y≈0.19). Pinch with reset jaws at eef z≈0.96; z≈0.975 is the tip and closes empty (g≈0.05). A real pinch holds g≈0.31–0.44. Turn the fixed handle in place; do not lift. Negative world yaw turns this control on (success near yaw −44° to −54°). These are observed end-effector poses, not independently measured object coordinates.
