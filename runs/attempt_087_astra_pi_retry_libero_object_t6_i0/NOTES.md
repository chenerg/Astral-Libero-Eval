# Pi Astra high clean retry — butter into basket

Instruction: pick up the butter and place it in the basket.
Official result: success=true, reason=success; 29 moves, 327 env steps, episode elapsed=1531.12 s (25 min 31.12 s).
Configuration: Pi-agent 1.3.0 clean; provider=openai; actual model=gpt-6-astra; thinking=high; libero_object task_id=6 init_id=0; planner=astra_pi_retry.
Prompt: PROMPT_BASE_3.txt copied byte-for-byte into PROMPT.txt and forced as the complete provider system prompt; 11947 bytes, SHA256 04203426f27741af60e002958db81e6958ecf3bb328c2a1b0251b155d3d16cd6. Identical to Codex attempt 085 and the base prompt. No LESSONS injection; LIBERO_HISTORY_RUN empty.
Budgets: MAX_MOVES=50, MAX_ENV_STEPS=600, WORLD_AXES=0; reset verified instruction, 50 remaining moves, axes=false, success=false, terminated=false.
Timing: Pi session records span 1670.675 s (27 min 50.675 s), from 2026-10-20T09:21:14.114Z to 2026-10-20T09:49:04.789Z. Runner metadata window (immediately before Pi launch through bridge cleanup) is 1671.082 s; full shell wall time including bridge startup was not separately recorded. Official episode average is 52.797 s/move.

Episode story (10 lines):
1. Policy inspected status and both reset cameras, then made the required +x 3 cm axis probe.
2. It identified the right-rear CREAM BUTTER package and approached with two -y segments at safe height.
3. Moves 4–10 descended cautiously, including multiple separate 2 cm requests and a final y/z adjustment.
4. The first close (move 11, z about 0.029) was empty: gripper_open fell to about 0.05.
5. Policy reopened and used two +x corrections, then made a second empty close on move 15 without transporting an empty gripper.
6. It reopened, lowered another 2 cm request (about 1.3 cm actual), and the third close at z about 0.015 held the package with gripper_open about 0.485.
7. A small closed test lift confirmed the object followed; two larger lifts raised it to z about 0.233.
8. Moves 22–26 transported the held butter through three +y segments and two diagonal x/y segments, explicitly keeping gripper=0.
9. Moves 27–28 lowered over the basket to z about 0.150 with stable grip and no blocked/contact feedback.
10. Move 29 opened the gripper; env.check_success() immediately returned true. Pi read final images, wrote AGENT_SUMMARY.md, and exited 0.

Comparison with Codex attempt_085_astra_libero_object_t6_i0: both succeeded in 29 moves. Pi used 327 vs 317 env steps (+10, about 3.15%). Official episode elapsed was 1531.12 vs 652.76 s (+878.36 s, 2.3456x). Pi session wall was 1670.675 vs Codex task_complete duration 669.354 s (different harness timing boundaries). Pi made three closes before pickup; Codex made two. Pi logs contain 62 completed provider turns totaling 1633.939 s, 31 bash tool calls, and 61 read tool calls. These observations explain this sample's longer wall time but do not isolate a general harness-overhead effect.

This was the single user-authorized retry after attempt 086's OAuth failure. No retry occurred inside this run. pi.err is empty; runner status=completed, Pi exit code=0, shell runner exit code=0. The runner stopped only its captured bridge, runner.json records bridge_closed=true, and the launcher confirmed no listener on 8765. Credentials were not archived. NOTES and analysis are launcher artifacts; index.jsonl and EXPERIMENT.md are reserved for the parent.
