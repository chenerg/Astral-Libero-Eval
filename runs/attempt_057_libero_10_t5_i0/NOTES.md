# NOTES

- instruction: pick up the book and place it in the back compartment of the caddy
- success: false (result.json only; reason max_moves). env success never flipped true.
- prompt file: PROMPT_BASE_3.txt via run_episode_clean.sh (PROMPT.txt is a byte copy; cmp matches)
- LIBERO_MAX_MOVES=50
- LIBERO_WORLD_AXES=0 (world_axes_overlay false)
- planner: astra, mode: clean

## What the gripper did

Reset above the table near (-0.297, 0.013, 1.174) with the jaws at home and remaining_moves 50.
The first moves probed +x, then the open gripper drove toward the book and yawed near -30° then +30° to line up with it.
Two closes around (-0.11, 0.13, z≈1.03) went fully shut (gripper_open ≈0.05). Short lifts did not hold anything, so the jaws opened.
The arm shifted in -x. A third close near (-0.189, 0.144, z=1.019) stopped around gripper_open 0.39 instead of sealing shut.
Lifts to z≈1.21 kept that opening. The arm then carried in -y and yawed to about 90°.
It lowered near (-0.390, -0.038, z≈1.10) and opened, treating that as a drop into a caddy cell. Official success stayed false.
Two more closes at that cell went fully shut again (empty, ≈0.05) and were released.
A later close near z=1.029 stopped around 0.38. The arm lifted back to z≈1.21 and drove further -y toward y≈-0.28.
An 8 cm descent there was blocked by contact, about 3.5 cm short. The gripper backed up, then nudged to about (-0.397, -0.297).
It lowered 6 cm to z=1.121 and opened on move 50. The bridge stopped at max_moves (50 moves, 588 env steps, 1080.73 s).
result.json success is false. The book was not scored in the back compartment of the caddy.
