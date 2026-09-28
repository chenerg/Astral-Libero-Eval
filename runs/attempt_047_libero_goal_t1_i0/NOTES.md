# NOTES

## 指令
put the bowl on the stove

## 官方成功
true。只依据 result.json：桥在 `env.check_success()` 为真时写入 success=true、reason=success。规划器没有自行宣布成功。30 次移动，334 个 env steps，elapsed_s=387.47。结束时 eef (−0.2153, 0.1197, 0.9764)，roll/pitch/yaw=(−0.2, 0.8, −0.6)，gripper_open=0.11，remaining_moves=0，remaining_env_steps=266。

## 手臂做了什么
复位在 (−0.217, −0.0137, 1.1606)，夹爪开度 0.517，姿态约为 0，world_axes_overlay=false，remaining_moves=30，env_steps=5（remaining_env_steps=595）。
第 1 步只做 +x 3 cm 探测，stopped=reached，开度升到 0.953，末端 (−0.1934, −0.0134, 1.1586)。
第 2–6 步张开接近：+x 8 cm 并下降 8 cm，再下降 10 cm、+y 1.2 cm 并下降 2 cm，再下降 2 cm 与 1.8 cm，到达 (−0.1201, −0.0052, 0.9537)，开度 0.995。
第 7 步原位闭合，开度 0.055。第 8 步保持闭合上抬 2 cm，开度 0.02。第 9 步原位张开到 0.727；note 记为抬升后碗未跟随，success 仍为 false。
第 10–12 步张开修正：+x 2 cm / +y 1.5 cm，再两次下降 2 cm，到 (−0.0983, 0.0021, 0.9504)。第 13 步原位闭合，开度 0.119。第 14 步闭合上抬 2 cm，开度 0.021。第 15 步再张开到 0.727，success 仍为 false。
第 16–18 步继续张开对齐并下降：+y 3.5 cm、+y 0.9 cm 并下降 2 cm、再下降 2 cm。第 18 步 planned_env_steps=50，env_steps 从 160 增到 210，stopped=reached，末端 (−0.0878, 0.0247, 0.9478)，开度 0.93。
第 19 步原位闭合，开度 0.1。第 20 步张开并上抬 3 cm，开度 0.728；note 记为宽碗整口抓取失败，success 仍为 false。
第 21–23 步改夹单侧碗沿：−y 1.2 cm 并下降 2 cm，再两次下降 2 cm，到达 (−0.0855, 0.0075, 0.9366)，开度 0.986。
第 24 步原位闭合，开度 0.1。第 25–26 步保持闭合上抬 2 cm 然后 8 cm，开度约 0.09，末端升到 (−0.0856, 0.0073, 1.0218)；note 记为碗随抬升。
第 27–28 步保持闭合搬运：−x 5.5 cm / +y 9.5 cm，再 −x 6.5 cm / +y 2.2 cm，到达 (−0.2144, 0.1191, 1.0142)，开度 0.083。
第 29 步保持闭合下降 4.5 cm，到 (−0.2152, 0.1195, 0.9765)，开度 0.08，success 仍为 false。第 30 步原位张开，开度只到 0.11，末端 (−0.2153, 0.1197, 0.9764)，stopped=reached，这一步 state.success 变为 true。
30 次移动全部 stopped=reached，transcript 中没有 blocked。官方成功出现在第 30 步结束时。

## 提示词
桥启动前，工作区 PROMPT.txt 由 PROMPT_BASE_3.txt 按字节复制（10997 字节）；桥刚就绪时 run 目录内的 PROMPT.txt 与 PROMPT_BASE_3.txt `cmp` 一致。没有 {{LESSONS}}，没有运行 compose_prompt.py，没有注入 LESSONS.md。LIBERO_WORLD_AXES=0，没有在提示词前附加世界坐标轴说明。Codex 使用 clean 的 `model_instructions_file` 指向工作区 `/home/chener/LIBERO/astra_eval/PROMPT.txt`。CODEX_HOME 为隔离临时目录 `/tmp/codex-clean-ftr5`，只符号链接 auth.json、models_cache.json、config.toml、sessions，没有 skills/ 或 plugins/，退出时已删除该临时目录，未删除 ~/.codex/sessions。回合结束后，run 目录里的 PROMPT.txt 仍与 PROMPT_BASE_3.txt 字节一致（10997 字节）；工作区 PROMPT.txt 同样仍一致。

## 限制
LIBERO_MAX_MOVES=30，LIBERO_MAX_ENV_STEPS=600，LIBERO_WORLD_AXES=0，planner=astra，suite=libero_goal，task_id=1，init_id=0。

## Codex 退出码
0。codex.log 中没有 ChatGPT usage limit 或 quota 错误。会话末尾记录 tokens used 58,456。
