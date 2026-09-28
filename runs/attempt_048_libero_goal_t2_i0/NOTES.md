# NOTES

## 指令
put the wine bottle on top of the cabinet

## 官方成功
false。只依据 result.json：success=false，reason=max_moves。桥在结束时用 env.check_success() 填写 success，本集为假。30 次移动，452 个 env steps，elapsed_s=430.66。结束时 eef (−0.1021, −0.2475, 1.1716)，roll/pitch/yaw=(−0.2, 15.6, −0.3)，gripper_open=0.727，remaining_moves=0，remaining_env_steps=148。

## 手臂做了什么
复位在 (−0.2096, −0.0136, 1.1621)，夹爪开度 0.517，姿态约为 0，world_axes_overlay=false，remaining_moves=30，env_steps=5（remaining_env_steps=595）。
第 1 步只做 +x 3 cm 探测，stopped=reached，开度升到 0.953，末端 (−0.186, −0.0137, 1.16)。
第 2–3 步张开接近：+x 9 cm、−y 2 cm 并下降 7 cm，再下降 6 cm，到达 (−0.0948, −0.0344, 1.0387)，开度 0.985。
第 4 步原位闭合，开度 0.05。第 5 步保持闭合上抬 2 cm，开度 0.019。第 6 步原位张开到 0.727；note 记为抬升后瓶底未跟随，判定空夹。
第 7–10 步张开后撤：连续 −x 2、2、3、3 cm，到达 (−0.1766, −0.0341, 1.0498)。第 11 步下降 2 cm。第 12 步原位闭合，开度 0.05。第 13 步闭合上抬 2 cm，开度 0.019。第 14 步再张开到 0.727；note 记为再次空夹。
第 15 步张开下降 4 cm，planned_env_steps=50，env_steps 从 135 增到 185，stopped=reached，残差约 1.8 cm，末端 (−0.1675, −0.0342, 1.0207)。第 16 步上抬 3 cm。第 17 步 −x 5 cm。
第 18 步下降 3.5 cm，planned_env_steps=50，stopped=reached，残差 1.8 cm，末端 (−0.2004, −0.0346, 1.0232)。第 19 步原位闭合，开度 0.05。第 20 步张开到 0.728；note 记为瓶口偏左未夹住。
第 21 步 −y 1.2 cm 并下降 2 cm，stopped=blocked，feedback 为 contact，剩余 z 约 −1.5 cm，末端 (−0.1816, −0.048, 1.0226)，开度 0.984。这是本集唯一一次 blocked。
第 22 步上抬 3 cm 并把 pitch 设为 15 度，到达 pitch 13.8°、z=1.0523。第 23 步 +x 3 cm 并下降 6 cm，到 (−0.161, −0.0445, 0.9965)，pitch 16.7°。第 24 步再下降 2 cm，z 几乎没降（0.9963），残差约 2 cm。
第 25 步原位闭合，开度 0.21。第 26 步保持闭合上抬 2 cm，开度 0.207，末端 (−0.1596, −0.0434, 1.0084)；note 记为非空夹。
第 27 步保持闭合上抬 12 cm，开度仍 0.207，末端升到 (−0.1602, −0.0434, 1.1211)。第 28 步 −y 10 cm 并上抬 6 cm，到 (−0.161, −0.1455, 1.1724)，开度 0.207。
第 29 步 +x 6 cm、−y 10 cm，指令保持闭合，但开度降到 0.013，末端 (−0.0965, −0.2511, 1.1781)；note 记为瓶从夹爪滑脱。第 30 步原位张开到 0.727，末端 (−0.1021, −0.2475, 1.1716)，state.success 仍为 false，随后 done reason=max_moves。

## 提示词
桥启动前，工作区 PROMPT.txt 由 PROMPT_BASE_3.txt 按字节复制（10997 字节）；桥刚就绪时 run 目录内的 PROMPT.txt 与 PROMPT_BASE_3.txt `cmp` 一致。没有 {{LESSONS}}，没有运行 compose_prompt.py，没有注入 LESSONS.md。LIBERO_WORLD_AXES=0，没有在提示词前附加世界坐标轴说明。Codex 使用 clean 的 `model_instructions_file` 指向工作区 `/home/chener/LIBERO/astra_eval/PROMPT.txt`。CODEX_HOME 为隔离临时目录 `/tmp/codex-clean-KIBs`，只符号链接 auth.json、models_cache.json、config.toml、sessions，没有 skills/ 或 plugins/，退出时已删除该临时目录，未删除 ~/.codex/sessions。回合结束后，run 目录里的 PROMPT.txt 仍与 PROMPT_BASE_3.txt 字节一致（10997 字节）；工作区 PROMPT.txt 同样仍一致。

## 限制
LIBERO_MAX_MOVES=30，LIBERO_MAX_ENV_STEPS=600，LIBERO_WORLD_AXES=0，planner=astra，suite=libero_goal，task_id=2，init_id=0。

## Codex 退出码
0。codex.log 中没有 ChatGPT usage limit 或 quota 错误。会话末尾记录 tokens used 60,780。
