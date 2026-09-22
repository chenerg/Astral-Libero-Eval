# Trial summary

Instruction: turn on the stove (libero_goal, task 7, init 0).
Official state reported success=true after 20 moves and 200 physics steps, with 5 moves and 400 steps remaining. The HTTP result also reported termination for success.

Probed +x, approached the stove control using the two RGB views, and descended with open jaws. Initial pinch near eef z=0.975 was too shallow: jaw fraction fell to 0.019 during a yaw test and the handle did not follow. Opened and approached lower. At measured z=0.955, closing held jaw fraction near 0.317 and engaged the handle. Positive yaw did not appreciably turn the control; reversing and continuing negative yaw actuated it. Official success arrived at measured yaw=-44.3 degrees, eef=(-0.4315, 0.1943, 0.9539), jaw fraction=0.386. Cartesian feedback remained reached; no blocked/contact events occurred.

Hindsight: World +x moves toward the bottom of agentview and upward in the reset wrist view; +y moves left in agentview and right in wrist. No axis inversion needed. Kitchen support appears near z=0.90; home measured z=1.187. For this scene the narrow stove handle can be pinched with reset jaws at measured eef z about 0.955, whereas z about 0.975 was too shallow. Use image alignment and measured jaw opening to distinguish handle engagement from an empty close. The handle is a fixed fixture: turn it in place rather than lifting. Negative world yaw turned this control on; the final successful wrist yaw was about -44 degrees. These are observed end-effector poses, not independently measured object coordinates.
