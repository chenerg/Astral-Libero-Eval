# NOTES

## 指令
open the top drawer and put the bowl inside

## 官方成功
false。只依据 result.json：success=false，reason=give_up:已用23次规划，多次柜沿接触且把手尚未可靠进入两垫；剩7次不足以完成开抽屉、抓碗验证和搬运释放。桥在结束时用 env.check_success() 填写 success，本集为假。23 次移动，397 个 env steps，elapsed_s=468.91。结束时 eef (0.0546, −0.1099, 1.0884)，roll/pitch/yaw=(4.2, 19.5, 90.1)，gripper_open=1.0，remaining_moves=7，remaining_env_steps=203。

## 手臂做了什么
复位在 (−0.2019, −0.0085, 1.1761)，夹爪开度 0.517，姿态约为 0，world_axes_overlay=false，remaining_moves=30，env_steps=5（remaining_env_steps=595）。
第 1–3 步自由空间探测：+x 3 cm、+y 3 cm、+z 3 cm，均 stopped=reached，开度升到 0.984，末端 (−0.175, 0.016, 1.2005)。
第 4 步 −y 10 cm 并下降 6 cm，到达 (−0.1775, −0.0785, 1.1405)，开度 0.99。
第 5 步向把手斜移 +x 7 cm、−y 6 cm、下降 7 cm，stopped=blocked，剩余 z 约 −2.7 cm，末端 (−0.1028, −0.1358, 1.0971)，开度 0.945。
第 6 步抬 3 cm 并向柜外 +y 退 3 cm，reached，到 (−0.1037, −0.1092, 1.1228)。第 7 步 +x 9 cm 并下降 5 cm，blocked，pitch 偏到 −18.5°，末端 (0.0328, −0.1198, 1.1409)，剩余 z 约 −6.8 cm。
第 8 步 +y 5 cm、抬 3 cm 并令姿态归零，仍 blocked，实测 pitch −10°，末端 (0.063, −0.0727, 1.1914)。第 9 步柜外 +x 2 cm 并下降 10 cm，reached（planned_env_steps=50），到 (0.0982, −0.0743, 1.1026)。第 10 步再下降 8 cm，blocked，z 几乎未动（1.0973），剩余 z 约 −7.5 cm。
第 11–12 步向柜外退并转 yaw：+y 6 cm、抬 2 cm、yaw 20°，再下降 8 cm、yaw 到 39°，均 reached，末端 (0.115, −0.013, 1.049)，yaw 37.8°。
第 13 步 −x 8 cm、−y 4 cm、yaw 57°，blocked，roll 偏到 −11.8°，末端 (0.0725, −0.0541, 1.0705)。第 14 步抬 3 cm 并把 yaw 设到 77°，blocked，实测 yaw 77.1°、z=1.1148。第 15 步 yaw 到 90° 并向柜 −y 2 cm，reached，末端 (0.1004, −0.0735, 1.1206)，yaw 89.4°。
第 16 步 +x 4 cm、−y 4 cm，reached（planned_env_steps=50），到 (0.1301, −0.113, 1.1112)，yaw 90.1°。第 17 步 −x 9 cm 并抬 2 cm，blocked，roll −11.7°，末端 (0.0747, −0.1153, 1.1564)。第 18 步向柜外 +y 2 cm 并抬 2 cm，reached，到 (0.0828, −0.0958, 1.1834)。
第 19 步保持 yaw 90 下降 8 cm，reached，z 到 1.1073。第 20 步 −x 2 cm、−y 1.5 cm，reached，末端 (0.0558, −0.105, 1.101)。第 21 步 −y 2 cm、下降 1.5 cm，reached，到 (0.0491, −0.1175, 1.0859)。第 22 步再 −y 8 mm、下降 8 mm，名义 reached 但末端几乎不动 (0.0482, −0.1176, 1.0852)，残差约 1.1 cm。
第 23 步只令 roll=−20°，stopped=reached，但实测姿态变成 roll 4.2°、pitch 19.5°、yaw 90.1°，末端 (0.0546, −0.1099, 1.0884)，开度 1.0。全程夹爪保持张开，没有闭合、没有抓碗。随后 give_up，state.success 仍为 false。

## 提示词
桥启动前，工作区 PROMPT.txt 由 PROMPT_BASE_4.txt 按字节复制（10256 字节）；桥刚就绪时 run 目录内的 PROMPT.txt 与 PROMPT_BASE_4.txt `cmp` 一致。没有 {{LESSONS}}，没有运行 compose_prompt.py，没有注入 LESSONS.md。LIBERO_WORLD_AXES=0，没有在提示词前附加世界坐标轴说明。Codex 使用 clean 的 `model_instructions_file` 指向工作区 `/home/chener/LIBERO/astra_eval/PROMPT.txt`。CODEX_HOME 为隔离临时目录 `/tmp/codex-clean-BzMY`，只符号链接 auth.json、models_cache.json、config.toml、sessions，没有 skills/ 或 plugins/，退出时已删除该临时目录，未删除 ~/.codex/sessions。回合结束后，run 目录里的 PROMPT.txt 仍与 PROMPT_BASE_4.txt 字节一致（10256 字节）；工作区 PROMPT.txt 同样仍一致。

## 限制
LIBERO_MAX_MOVES=30，LIBERO_MAX_ENV_STEPS=600，LIBERO_WORLD_AXES=0，planner=astra，suite=libero_goal，task_id=3，init_id=0。

## Codex 退出码
0。codex.log 中没有 ChatGPT usage limit 或 quota 错误。会话末尾记录 tokens used 54,606。
