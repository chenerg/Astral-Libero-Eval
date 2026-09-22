# Trial summary

Instruction: turn on the stove (libero_goal, task 7, init 0).

Official state reported success=true on move 19, at 177 physics steps. The HTTP result reason was success, and the final state was terminated. Six planner calls and 423 physics steps remained. Measured yaw stopped at -48.9 degrees when the success check ended the move (commanded -60).

Probed +x by 3 cm. The world triad on agentview has red +X toward the bottom of the frame and green +Y toward the left, matching the cheat sheet. No axis was inverted. Open jaws moved +y, then -x/+y, to the black lever behind the burner. A slide that stayed too far -x left the lever high in the wrist (under the palm). Raising a few centimetres and sliding +x brought the lever down between the fingertips. Closed at measured z=0.962; gripper_open stayed 0.306, a real pinch. Named gripper=0 on every later call. In-place yaw -20, then -40, then toward -60 turned the lever. Success fired at measured yaw=-48.9, eef=(-0.415, 0.200, 0.961), gripper_open=0.402. All moves reported reached/ok.

Hindsight: World +x moves toward the bottom of agentview; +y moves left in agentview and right in the reset wrist. No axis inversion. Kitchen table is about z=0.90; home measured z=1.187. The black stove lever sits behind the burner (more -x, y about 0.19). Pinch with reset jaws at measured eef z about 0.96; a real pinch holds gripper_open about 0.31-0.40. The handle is fixed: turn it in place, do not lift. Negative world yaw turns this control on; success arrived near measured yaw -49 degrees. The reach check stops around 1 cm short, so near the lever command a little past the desired xyz. These are observed end-effector poses, not independently measured object coordinates.
