# attempt_043 — FAIL max_moves (30 /move)

Launcher vs policy: this session is the episode launcher only. Nested clean Grok (`run_episode_grok_clean.sh`, grok-4.7, `--verbatim --always-approve --no-subagents --disable-web-search --disallowed-tools Agent`) was the robot policy and issued every POST /move. Launcher did not POST /move or GET /status except to confirm the bridge was up. grok_exit:0. Not a usage-limit / quota / insufficient_quota / rate-limit error.

Instruction: pick up the cream cheese and place it in the basket.
Official success (result.json / env.check_success only): false. reason=max_moves.
30 POST /move, 457 env steps, 2910.85 s. remaining_moves=0, remaining_env_steps=143, terminated=true. Final eef ≈ (0.086, −0.080, 0.045), gripper_open=0.05.

Suite libero_object, task 1, init 0. Planner grok. Model grok-4.7. Clean mode: isolated GROK_HOME (auth + config with memory and subagents off, no skills/), policy cwd under /tmp/grok-policy-cwd-*, `--system-prompt-override` from PROMPT.txt. LIBERO_MAX_MOVES=30. LIBERO_MAX_ENV_STEPS=600. LIBERO_WORLD_AXES=1.

Prompt: PROMPT_BASE_2.txt with {{LESSONS}} replaced by “(no extra accumulated lessons)”, plus the world-axes header (BOTH obs/agentview.png AND obs/wrist.png have a translucent world XYZ triad, red=+X, green=+Y, orange/blue=+Z). Close-now check and collision-avoid kept from BASE_2. compose_prompt.py was not run. LESSONS.md was not injected. world_axes_overlay=true from reset through the last move.

Story: Floor scene. Reset at home eef ≈ (−0.140, 0.001, 0.271), gripper_open 0.517, jaws-down, triad overlay on.
m1 probed +x 3 cm. The note said agentview moved toward BOTTOM, so +x stayed the cheat-sheet sign and +y was LEFT. The basket on the left was never approached.
Open-jaw travel went to about (0.02, −0.10), then straight descents z=0.20 → 0.10 → 0.05 → 0.038. Wrist notes called the light-blue box centered between the pads.
m7 closed with “close now would trap the object: yes”; gripper_open fell to 0.05 and the box stayed on the floor. The note called that empty and reopened.
The same miss repeated: slide +x or drop z, close, see the body still toward wrist image-up (+X), reopen. Closes at m7, m10, m13, m16, m18, m25, m28, and m30 all finished near g≈0.05–0.07.
m19 commanded z=0 and blocked/contact (stall, remaining z ≈ −1.4 cm), sliding off to z≈0.014 with only floor between the pads. Rose to z=0.10.
m21’s descent to z=0.016 also blocked and slid to about (0.106, −0.063). The hand stepped back over the box near (0.085, −0.082).
m25 closed again at z≈0.05 and shut empty. A −x backoff plus pitch +15 close (m28) still left g=0.05, box on the floor.
Last move nudged −1.2 cm y and closed. Official success stayed false. The cream cheese never left the floor.
Per-move notes did not name the red=+X / green=+Y / orange-blue=+Z colors. They kept the +x probe (BOTTOM of agentview) and treated wrist image-up as world +X. The planner’s AGENT_SUMMARY does say it used the wrist triad (“+x image-up, +y image-right”). m20’s “orange face further +x” reads as a scene object, not the overlay.

30 /move actually happened (budget 30). Two blocked/contact stalls (m19, m21); the rest reached. gripper=0 on the eight closes above; every one emptied. No give_up. No quota retry.

grok_session: /home/chener/LIBERO/astra_eval/runs/attempt_043_grok_libero_object_t1_i0/grok_session/%2Ftmp%2Fgrok-policy-cwd-uNNh/01a0d140-49c7-7601-8e80-469d3d27af58 (summary.json and chat_history.jsonl present). Copied by run_episode_grok_clean.sh before the temp home was deleted.
