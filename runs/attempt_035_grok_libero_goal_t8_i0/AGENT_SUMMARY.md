# Episode summary

Instruction: put the bowl on the plate (libero_goal, task 8, init 0).

Official result: success=false, terminated=true, reason=max_moves, after move 25 (399 env steps). Final measured eef (0.087, 0.033, 0.973), pitch 13.9, gripper_open 0.077.

What happened:
- +x probe (dx=+0.03) moved the gripper toward the bowl. Wrist +X is image-up; agentview +X is toward the bottom. Cheat sheet kept.
- Early closes around z=1.02 were lip pinches. A 3 cm lift dropped gripper_open from 0.05 to 0.019 and the bowl stayed on the table. Roll +15 on the -Y side blocked further descent near z=1.02 and blocked a later +x slide because a pad was in the bowl.
- Reopened and went to a lower +Y side-rim pose: about (-0.084, 0.031, 0.953), pitch 15.6, jaws open. Wrist showed the rim in the pad gap. Close left gripper_open=0.079.
- Last move carried that pose to (0.087, 0.033, 0.973) with gripper held at 0. Opening stayed 0.077, so the bowl traveled with the arm. Final images show the bowl overlapping the near edge of the plate, still pinched, not released and not fully seated. No planner calls left to open.

Feedback: most free-space moves reported reached, often with about 1 cm residual. Two blocked/contact events: descent through z=1.00 while centered/rolled on the bowl (stopped near z=1.02), and a +x slide while a rolled pad was still in the bowl.

Hindsight: World +x is toward the BOTTOM of agentview and the TOP of the wrist image; +y is LEFT in agentview and RIGHT in the wrist. Kitchen home z≈1.18. A jaws-down close near z=1.02 pinches the lip and empties to gripper_open≈0.02 on a small lift. The wall pinch that held was pitch≈15, yaw≈0, measured eef about (-0.08, +0.03, 0.95), with gripper_open staying near 0.08 through a carry. The finger gap is the bottom of the wrist frame, not the image center. Plate for this init is near x≈0.09, y≈0.03; stop there still closed and the bowl only overlaps the rim. Release with the gripper open after the bowl is centered on the plate. Small z targets are often marked reached about 1 cm short, so command past the intended height.
