# Episode summary

Instruction: turn on the stove and put the moka pot on it
Suite: libero_10, task_id 2, init_id 0 (KITCHEN_SCENE3)
Result: success=false, terminated on max_moves (40/40). Env steps 422. Final gripper_open=0.05 (empty close). Stove was not turned on and the moka pot was never lifted.

## What I tried

- Axis probe +x from home. Agentview motion was toward the BOTTOM of the frame, matching the prompt cheat sheet. +y is image-left.
- Hovered over the stove/knob region (around x=0.05 to 0.13, y=0.08 to 0.17, z=1.16 down to 0.91).
- Top-down closes at z≈0.95–0.98 returned gripper_open≈0.05: jaws met on air. Wrist at pitch 0 looks forward, so a knob under the palm often sits below the frame.
- Pitch +20 made the agentview clearer: knob sits at the front-right corner of the burner, between the stove plate and the moka pot.
- Best wrist alignment (z≈1.08–1.16, x≈0.11, y≈0.08–0.11): knob large, just above/outside the left finger, stove in the right half of the gap. Small -y walked off the knob onto the moka. Small +y put the jaws back over the stove front.
- A low backward slide (-x at z≈0.93) stalled in contact (blocked, x stuck near 0.093). The contact was behind the pads, not in the gap; the wrist still showed empty table.
- Final two moves yawed +20 then +40 while closing. gripper_open stayed ≈0.05. The knob was not trapped, so yaw did not turn the hinge. Moka was never grasped.

## Why it failed

The knob hinge needs qpos ≥ 0.5 rad about its vertical axis, which requires the knob body between the pads and then a wrist yaw. I never got a non-empty close (gripper_open stayed ~0.05). Most of the budget was spent chasing a lateral offset: the wrist camera looks forward from a +5 cm hand-x offset, so the knob stayed on the left edge of the wrist image even when the agentview jaws were nearly over it. Descending at the “almost centered” xy either passed the knob in +x (wrist became empty table) or closed above it. With moves exhausted, the moka place never started.

## Hindsight

- World +x is toward the BOTTOM of agentview; world +y is toward the LEFT of agentview. Images are rot180. Trust that mapping; the first +x probe agreed.
- Kitchen table support is about z=0.90, home eef z≈1.19. Do not command z below ≈0.82. An empty close at z≈0.95–0.99 (gripper_open≈0.05) means the pads are above the knob or beside it, not around it.
- Flat-stove knob is a vertical hinge (button joint axis local +Z, range about −0.005 to 2.1 rad). Turned on iff qpos ≥ 0.5 rad (~29 deg). Positive yaw (CCW from above) matches the joint’s +Z. Grasp the knob body, then yaw +20 twice while holding gripper=0.
- The knob is the small black cylinder just off the front-right corner of the burner plate (image-right of the plate, image-left of the moka), not the burner rings. Moka is immediately to its image-right (−y). A −y overshoot from the knob lands on the moka.
- Wrist camera is on right_hand at pos (0.05, 0, 0), looking out. Pads are at the BOTTOM of the wrist frame. “Knob left of the left pad” is a real lateral miss, not just parallax, but objects directly under the palm disappear from the wrist once z drops and the camera looks at the table ahead. Use a high (z≈1.10–1.16), pitch-0 wrist view to center, then descend only 2 cm at a time.
- Close only when the wrist shows the knob in the gap between the pads. gripper_open≈0.05 after a close is an empty pinch. Do not yaw an empty gripper.
- Panda finger opening at yaw 0 is along the hand local Y. Full open is required; one /move sometimes only reaches gripper_open≈0.73, so send gripper=1 again before the close.
