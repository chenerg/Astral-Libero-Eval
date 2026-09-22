# attempt_004 — full episode, fail

Policy run (harness OK). 27 moves, 426 steps, 389 s, give_up.

Did use lessons from attempt 2: identified the right bowl, used pitch ±15–25°, descended to z≈0.91–0.92, followed empty_grasp / holding_or_pinching, never hauled an empty gripper to the plate.

Still failed:
- Three close+lift cycles. Two reported holding_or_pinching (open 0.49 then 0.28) then a **6–7 cm** lift slipped to empty_grasp (open 0.03–0.06).
- Deeper z=0.89–0.91 often `blocked/contact`.
- One 90° yaw request (move 12) twisted the wrist (roll 23°) and stalled.

Next: after pinch, lift 2 cm only; cap yaw/pitch change per move at ~20°; longer close dwell.
