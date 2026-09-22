# attempt_014 — aborted after GET /status (0 /move)

Instruction: pick up the black bowl between the plate and the ramekin and place it on the plate.
Official success: false. No result.json. Not a policy score.

Prompt: PROMPT_BASE_2.txt with {{LESSONS}} replaced by “(none — this episode uses PROMPT_BASE_2 only; no accumulated lessons)”. compose_prompt.py was not run. LESSONS.md was not injected. LIBERO_MAX_MOVES=15 (remaining_moves=15 at reset). Planner astra, Codex gpt-6-astra medium.

Story: Bridge reset libero_spatial task 0 init 0 at home eef ≈ (−0.21, −0.01, 1.17), gripper_open 0.517, feedback reset. Codex session 01a0c217-5cf2-7ec2-9647-93a05403916d attached the two reset images and the PROMPT_BASE_2 text. It issued one tool call: GET /status, read the instruction and the 15-move budget, then wrote that the next action should be the mandatory +3 cm +x axis probe. It then stopped (`tokens used 5,568`, CLI exit 0, wall ~21 s). No POST /move, no POST /give_up, no AGENT_SUMMARY.md. Arm never left home. Episode left live (terminated=false, remaining_moves=15) until the parent stopped the bridge.

Same early-exit pattern as attempt_003 (announce the next motion, then drop the session). Not a usage-limit/quota error. Codex was not retried.
