# Episode summary

Instruction: pick up the ketchup and place it in the basket.

Official state reported success=false after give_up on move 22, at 193 environment steps. Remaining budgets: 3 moves and 407 steps.

Probed +x (agentview moved toward BOTTOM; cheat sheet held). Approached the gray-capped red ketchup with open jaws via −y, then spent many moves correcting XY because the wrist showed the bottle on the left pad rather than in the gap. Descended to neck height (z≈0.13–0.16). Closed twice; both times gripper_open settled at 0.05 (empty) and agentview still showed the bottle standing on the floor. After the first empty close the ketchup was left of the shut jaws, so the −y overshoot was real. Reopened, shifted +y, descended, closed again on a similar left-pad sliver. Too few moves remained to regrasp and place. All moves reached/ok; no blocked/contact. Neighbors (soup, milk, juice, cheese) were never grasped.

Hindsight: World +x is toward the bottom of agentview; +y left; −y right. Floor scene, support z≈0, home z≈0.263. Ketchup body ≈(x=−0.02, y=−0.19). Basket is +y / left, prior-success place ≈(0.02, 0.27) with release z≈0.21. Neck grasp wants z≈0.13 jaws-down. Real pinch holds gripper_open≈0.42; empty close is ≈0.05. A ketchup sliver on the LEFT wrist pad is not “between the pads” — do not close. Wrist-left sliver means more −y until the neck sits at bottom CENTER of the gap. 2 cm of y error misses this thin bottle. Do not spend the 25-move budget on XY hunting; 8–10 cm free-space −y to y≈−0.21, descend, close only on a clear between-pad neck, then 2 cm lift to confirm g stays ~0.4 before transport.
