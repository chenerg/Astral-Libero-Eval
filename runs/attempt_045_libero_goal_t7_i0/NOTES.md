# NOTES

## 指令
turn on the stove

## 官方成功
true。只依据 result.json：桥在 `env.check_success()` 为真时写入 success=true、reason=success。规划器没有自行宣布成功。14 次移动，190 个 env steps，elapsed_s=246.88。结束时 eef (−0.4307, 0.1936, 0.9427)，roll/pitch/yaw=(0.5, 0.8, −44.8)，gripper_open=0.392，remaining_moves=16，remaining_env_steps=410。

## 手臂做了什么
复位在 (−0.2128, −0.0033, 1.187)，夹爪开度 0.517，姿态约为 0，world_axes_overlay=false，remaining_moves=30，env_steps=5（remaining_env_steps=595）。
第 1 步只做 +x 3 cm 探测，stopped=reached，开度升到 0.953，末端 (−0.1868, −0.0032, 1.1866)。
第 2–4 步在空中靠近灶台旋钮：+y 10 cm 并下降 6 cm，再 −x 8 cm / +y 3.5 cm / 下降 5 cm，然后 −x 8 cm / +y 7.5 cm，到达 (−0.3432, 0.1937, 1.0762)，夹爪仍全开（0.991）。
第 5–7 步继续 −x 并下降：−x 6.5 cm、下降 5.5 cm，再竖直下降 6 cm 到 z≈0.961，最后 +y 8 mm、下降 1.8 cm，停在 (−0.4167, 0.1943, 0.9462)，开度 0.998。
第 8 步只闭合，开度落到 0.321，位置几乎不动（stopped=reached，dist_m=0），success 仍为 false。
第 9–10 步保持闭合并向 +yaw 各转 20°。第 9 步 yaw 到 18.2（目标 20.2），开度 0.395。第 10 步 planned_env_steps=50，位置到达（dist_m=0.0014），但 yaw 只到 30.3，低于目标 38.2，开度 0.477，success 仍为 false。
第 11–13 步改为每次 −yaw 20° 并保持闭合：实测 yaw 依次为 11.0、−8.2、−27.5，开度约 0.33–0.37，success 仍为 false。
第 14 步再 −yaw 20°（目标 yaw −47.5）。实测 yaw −44.8，开度 0.392，末端 (−0.4307, 0.1936, 0.9427），stopped=reached。这一步的 state.success 变为 true。
14 次移动全部 stopped=reached，transcript 中没有 blocked/contact。官方成功出现在第 14 步结束时。

## 提示词
PROMPT.txt 在桥启动前由 PROMPT_BASE_3.txt 按字节复制；run 目录内的 PROMPT.txt 与 PROMPT_BASE_3.txt `cmp` 一致。没有 {{LESSONS}}，没有运行 compose_prompt.py，没有注入 LESSONS.md。LIBERO_WORLD_AXES=0，没有在提示词前附加世界坐标轴说明。Codex 使用 clean 的 `model_instructions_file` 指向该 PROMPT.txt。CODEX_HOME 为隔离临时目录，只符号链接 auth.json、models_cache.json、config.toml、sessions，没有 skills/ 或 plugins/。

## 限制
LIBERO_MAX_MOVES=30，LIBERO_MAX_ENV_STEPS=600，LIBERO_WORLD_AXES=0，planner=astra，suite=libero_goal，task_id=7，init_id=0。

## Codex 退出码
0。codex.log 中没有 ChatGPT usage limit 或 quota 错误。会话末尾记录 tokens used 44,280。
