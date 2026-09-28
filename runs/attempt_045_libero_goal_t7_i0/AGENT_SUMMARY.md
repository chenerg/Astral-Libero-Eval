# Episode summary
Instruction: turn on the stove.
Official response reported success=true after move 14, 190 physical steps.

Probed +x, approached black control using wrist images, descended with open jaws, and closed around handle. Measured grip opening was 0.321. Positive yaw did not activate and lagged target; reversed in increments of 20 degrees. Official success arrived at measured yaw -44.8 degrees while maintaining gripper=0. All moves returned ok, with no blocked/contact; positive yaw had an 8-degree orientation residual.

Hindsight: World +x appears toward agentview BOTTOM (initial probe visually small), +y moves hand LEFT. In downward wrist view, -x moved the stove upward and +y moved it left. Grasp region is near lower center of wrist image, not image center. Successful measured end-effector grip region was approximately x=-0.424,y=0.198,z=0.943 in this reset; these are measured hand positions, not object coordinates. Support height was not measured. The narrow black handle was gripped above its circular base. Do not lift this attached control. Negative world yaw with closed jaws actuates stove; positive yaw resisted without success. Grip opening around 0.32–0.39 was compatible with engagement.
