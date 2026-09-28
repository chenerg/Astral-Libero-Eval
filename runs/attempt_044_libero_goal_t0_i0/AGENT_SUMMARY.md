# Episode summary
Official instruction: open the middle drawer of the cabinet.
HTTP result reported success=true at move 29, env step 390.

Probed +x, approached cabinet from +y, rotated roll incrementally to -90 degrees for a side grasp. Initial contact near cabinet top required retreat and lift. First grasp pulled slightly but slipped (gripper_open fell to 0.03). Shifted +x by 6 cm to engage farther along the handle. Second grasp moved the middle drawer; repeated pulls at roll -90/-75 encountered blocked/contact. Adjusted roll to approximately -60, then pulled +y by 10 cm and continued, triggering official success.

## Hindsight
World +x maps toward agentview BOTTOM; -y approaches cabinet on image right, +y opens drawer. Home z=1.1712. Support surface height was not measured. Middle-handle side grasp worked near measured eef x=0.046, y=-0.145, z=1.020 with roll=-90; final effective pull posture roll approximately -61, z=1.036. Wrist grasp pads are at bottom of image: center-image handle alignment alone was insufficient. Measured gripper_open around 0.75 can represent successful handle engagement in this geometry; near 0.03 after retreat indicated an empty grasp. Moving roll toward -60 improved clearance/engagement after blocked pulls; the exact source of those contacts was not confirmed.
