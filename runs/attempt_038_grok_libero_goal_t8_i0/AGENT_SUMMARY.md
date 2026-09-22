# Episode summary: put the bowl on the plate

libero_goal task 8 init 0. Official success on move 18 (env step 183). success=true, terminated=true. Gripper still closed on the rim when the checker fired during the final descent (z≈0.97, gripper_open≈0.04).

## What I tried

- Probed +x by 3 cm from home (x≈-0.21, z≈1.18). Agentview shift was small at that height; later +y moved the gripper toward the LEFT of agentview, matching the cheat sheet. Treated +x as toward the BOTTOM of agentview (away from the arm), +y as image-left.
- Opened the jaws and stepped +x over the metal bowl, then lowered to z≈1.08.
- Pitched to +15° so the opening met the wall instead of pinching the lip from above. Slid to the +y rim (y≈0.05), then nudged back to y≈0.035 so the wrist showed one pad inside the bowl and one outside.
- Closed at z≈0.956. gripper_open settled at ≈0.06, then ≈0.04 on the lift, and stayed there. A 2 cm lift was ambiguous; a further 5 cm lift kept the rim in the pads and the bowl off the table.
- Carried +x in two steps (8 cm then 6 cm) to about x≈0.05, y≈0.04, above the plate. Leveled pitch to 0 while still holding. Lowered. The success bit flipped on the last lower, before the jaws opened.

## Feedback

Every /move returned stopped=reached and feedback=ok. No blocked/contact. Residuals were about 0.5–1.2 cm. The close did not drive gripper_open to ≈0.02, which matched a thin rim in the pads rather than an empty pinch.

## Why it worked

The bowl is wider than the parallel jaws, so a top-down pinch on the lip fails. The grasp that held was a 15° pitch on the +y rim, with the wrist showing the rim between the pads (one pad in the interior, one outside), at about z=0.95–0.96. Holding gripper=0 on every later call kept the rim. The plate is further +x than the bowl; placing at x≈0.05, y≈0.04, then descending, put the bowl on the plate.

## Hindsight

World +x is toward the BOTTOM of agentview. World +y is toward the LEFT of agentview. Kitchen table z≈0.90, home z≈1.18. Bowl wall close ≈ z=0.95–0.96 with about 15° pitch on the +y rim (eef y≈0.03–0.04 when the bowl center is near y=0). A real rim pinch holds gripper_open≈0.04 through a 5 cm lift; ≈0.02 after that lift is empty. Plate for this init is near x≈0.05, a bit further +x than the bowl. Wine bottle is behind the bowl (−x); cream-cheese box is to the left of the plate. Do not release until the agentview shows the bowl over the plate.
