# attempt_003 — aborted after 1 move

Not a policy score.

- Codex `gpt-6-astra` medium, session `01a0bed3-4062-7723-9d2f-aa00242566d6`.
- First `/move` to (0.03, -0.16, 1.08). Harness tried to regulate roll/pitch/yaw back to 0 even though the agent did not request orientation. Quaternion sign/euler conversion twisted the wrist (roll −51°) and stall detection fired at dist=0.26 m.
- Codex wrote “next move should raise the arm…” then **exited** (`tokens used 6161`) without another `/move` or `/give_up`. No `result.json`.

Fixes for attempt_004: ori action is zero unless pitch/roll/yaw named; stall only after 20 steps; prompt forbids stopping after one blocked move.
