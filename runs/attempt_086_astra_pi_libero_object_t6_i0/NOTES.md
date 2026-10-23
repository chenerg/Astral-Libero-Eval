# Pi Astra high clean — authentication failure before policy execution

Instruction: pick up the butter and place it in the basket.
Official result: unavailable; no result.json was synthesized. This is an infrastructure/authentication error, not an official task failure.
Configuration: libero_object task_id=6 init_id=0; planner=astra_pi; runner=Pi clean; model=openai/gpt-6-astra; thinking=high; Pi version=1.3.0.
Prompt: PROMPT_BASE_3.txt, archived as this run's PROMPT.txt; strict pi_force_system.ts override; no LESSONS injection; LIBERO_HISTORY_RUN empty.
Budgets: MAX_MOVES=50, MAX_ENV_STEPS=600, WORLD_AXES=0; reset verified 50 remaining moves and no world-axis overlay.

Episode story (8 lines):
1. This comparison began only after the completed Codex run's bridge had stopped and port 8765 was confirmed free.
2. A read-only Pi model listing confirmed openai/gpt-6-astra supports thinking and images.
3. The bridge reset the identical libero_object task_id=6 init_id=0 scene.
4. The launcher verified the instruction, 50 remaining moves, and disabled world-axis overlay.
5. Pi initialized its isolated clean home, policy working directory, session archive, and exact system prompt override.
6. Its first provider request failed before any tool execution: OAuth refresh failed for openai, HTTP 400 invalid_grant.
7. No /move or /give_up was issued, and there were zero policy moves; the five environment steps are reset settling steps only.
8. In accordance with the skill and parent instructions, no retry or credential mutation was attempted; the runner stopped only its captured bridge and port 8765 was confirmed closed.

Pi process exit code: 0 despite stopReason=error in pi.log/session. Runner exit code: 1 because no official result.json was produced.
runner.json preserves status=policy_exited_without_result with added auth_error detail; pi.log and pi_session contain the original provider error. pi.err is empty.
The Pi runner did not append runs/index.jsonl; parent should archive this attempt as an infrastructure failure, success=null.
analyze_run.py completed (analysis.txt), reporting null official result fields, five reset-settling steps and no policy moves. No valid performance or strategy comparison against Codex can be drawn from this attempt.
Timing: archived Pi session timestamp span=1.065 s (08:49:12.435Z to 08:49:13.500Z); provider request durationMs=1002. runner.json metadata span=1.454 s excludes bridge startup. Seconds/move is undefined because no move occurred.
Comparison prompt SHA256 matches the Codex attempt exactly: 04203426f27741af60e002958db81e6958ecf3bb328c2a1b0251b155d3d16cd6.
