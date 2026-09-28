# NOTES

## 指令
put the bowl on the plate

## 官方成功
true。只依据 result.json：桥在 `env.check_success()` 为真时写入 success=true、reason=success。规划器没有自行宣布成功。22 次移动，236 个 env steps，elapsed_s=335.72。结束时 eef (0.1048, 0.0421, 0.9823)，roll/pitch/yaw=(−0.2, 0.2, −0.3)，gripper_open=0.172，remaining_moves=8，remaining_env_steps=364。

## 手臂做了什么
复位在 (−0.2069, 0.0017, 1.1789)，夹爪开度 0.517，姿态约为 0，world_axes_overlay=false，remaining_moves=30，env_steps=5（remaining_env_steps=595）。
第 1 步只做 +x 3 cm 探测，stopped=reached，开度升到 0.953，末端 (−0.1823, 0.0018, 1.1775)。
第 2–3 步张开并接近：+x 10 cm / 下降 10 cm，再 +x 5 cm / 下降 10 cm，到达 (−0.0295, 0.002, 0.9884)，开度 0.988。
第 4–5 步只下降 2 cm 然后 1.5 cm，到 (−0.0273, 0.0021, 0.9687)，开度约 0.99，success 仍为 false。
第 6 步原位闭合，开度落到 0.05，位置不动（dist_m=0）。
第 7 步闭合并上抬 2 cm，开度 0.019，末端 z=0.9817。第 8 步原位张开，开度 0.727。note 记为空抓后的修正，success 仍为 false。
第 9–12 步张开并沿 −x 修正、后两步同时下降：−x 2 cm、再 −x 2 cm、−x 2 cm 并下降 2 cm、−x 1.5 cm 并下降 2 cm，到达 (−0.0783, 0.0021, 0.9562)，开度 0.998。
第 13 步再竖直下降 2 cm，实测末端 (−0.0712, −0.0003, 0.9435），开度 1.0。第 14 步原位闭合，开度 0.125，success 仍为 false。
第 15–17 步保持闭合上抬 2 cm、3 cm、6 cm，开度约 0.07，末端升到 (−0.0713, −0.0002, 1.0321）。
第 18–19 步闭合并搬运：+x 10 cm / +y 3 cm，再 +x 7 cm / +y 1 cm，到达 (0.101, 0.0412, 1.0414)，开度 0.07。
第 20–21 步保持闭合下降 5 cm 然后 2 cm，到 (0.1063, 0.0422, 0.9834)，开度 0.068，success 仍为 false。
第 22 步原位张开。开度只到 0.172，末端 (0.1048, 0.0421, 0.9823)，stopped=reached。这一步的 state.success 变为 true。
22 次移动全部 stopped=reached，transcript 中没有 blocked。官方成功出现在第 22 步结束时。

## 提示词
桥启动前，工作区 PROMPT.txt 由 PROMPT_BASE_3.txt 按字节复制；桥刚启动时 run 目录内的 PROMPT.txt 与 PROMPT_BASE_3.txt `cmp` 一致。没有 {{LESSONS}}，没有运行 compose_prompt.py，没有注入 LESSONS.md。LIBERO_WORLD_AXES=0，没有在提示词前附加世界坐标轴说明。Codex 使用 clean 的 `model_instructions_file` 指向工作区 `/home/chener/LIBERO/astra_eval/PROMPT.txt`。CODEX_HOME 为隔离临时目录 `/tmp/codex-clean-UVTT`，只符号链接 auth.json、models_cache.json、config.toml、sessions，没有 skills/ 或 plugins/，退出时已删除该临时目录。回合结束后，run 目录里的 PROMPT.txt 与当前 PROMPT_BASE_3.txt 不再一致：note 示例段被改过（History 句加长，Wrist 写成 Wristview，Target 句加了“我要处理的”），mtime 为 00:35:57；codex.log 里没有改这个文件的命令。工作区 PROMPT.txt 仍与 PROMPT_BASE_3.txt 字节一致。

## 限制
LIBERO_MAX_MOVES=30，LIBERO_MAX_ENV_STEPS=600，LIBERO_WORLD_AXES=0，planner=astra，suite=libero_goal，task_id=8，init_id=0。

## Codex 退出码
0。codex.log 中没有 ChatGPT usage limit 或 quota 错误。会话末尾记录 tokens used 47,385。
