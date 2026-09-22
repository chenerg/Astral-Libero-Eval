# Restored episode recovery

Instruction: pick up the milk and place it in the basket.

Result: success=false, terminated=true after give_up. Used 19 of the fresh 20 planner moves; physics count reached 455 of 600. One remaining call could not complete regrasp, lift verification, transport, and separate release.

The restored milk continued falling and settled on its side near the can. Rotated yaw in increments of at most 20 degrees to approximately 75 degrees, approached the body, and descended. Two closes near measured eef z=0.062 failed retention tests: measured jaw opening fell to approximately 0.020 and the milk remained on the floor. Corrected xy and tried a lower approach. That approach returned blocked/contact at z=0.0573 against target z=0.0419, with residuals approximately 1.5cm in x and z. Retracted 3cm with open jaws instead of repeating the blocked target. No transport or release followed an empty grasp.

Hindsight: World +x maps toward agentview bottom and +y left. Floor support is approximately z=0. The red carton marked MILK became sideways after settling. Yaw approximately 75 degrees brought its narrow width across the jaws, but did not itself ensure alignment. The carton remained left of the actual wrist pinch point despite filling much of the image. Lowering alone was ineffective and eventually blocked. Next attempt needs better lateral centering and possibly another yaw or tilt before descent. Final eef approximately (-0.049, 0.124, 0.081), yaw 74.9 degrees, gripper open approximately 0.981. Preserve enough calls to verify grasp, align over the basket interior, descend, and release in a separate move.
