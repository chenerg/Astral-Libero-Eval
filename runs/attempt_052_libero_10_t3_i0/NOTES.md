# NOTES

## 指令
put the black bowl in the bottom drawer of the cabinet and close it

## 官方成功
false。只依据 result.json：success=false，reason=max_moves。桥在结束时用 env.check_success() 填写 success，本集为假。50 次移动，556 个 env steps，elapsed_s=859.29。结束时 eef (0.0555, 0.1504, 0.9424)，roll/pitch/yaw=(40.0, 1.8, −0.0)，gripper_open=0.983，remaining_moves=0，remaining_env_steps=44。

## 手臂做了什么
复位在 (−0.2172, −0.0147, 1.1698)，夹爪开度 0.517，姿态约为 0，world_axes_overlay=false，remaining_moves=50，env_steps=5（remaining_env_steps=595）。
第 1 步 +x 3 cm 探测，reached，开度升到 0.953，末端 (−0.1933, −0.0146, 1.168)。第 2–4 步向 +x、略 −y 并下降，到 (0.0578, −0.0511, 1.0185)。第 5 步再下降 2 cm，reached，z=1.0051。
第 6 步 +y 3.5 cm 去对侧沿，到 y=−0.021。第 7–8 步下降并前移，到 (0.0649, −0.0196, 0.9744)。第 9 步原地闭合，开度 0.05。第 10 步夹持抬 2 cm 到 z=0.9887，开度 0.019；记录写明碗未跟随。
第 11 步张开到 0.727。第 12–14 步连续下降到 z=0.9514。第 15 步第二次闭合，开度 0.07。第 16–17 步保持闭合抬到 z=1.0305，开度 0.045；记录写明碗跟随上移。
第 18 步 +y 10 cm 并抬 2.5 cm，到 (0.0624, 0.0791, 1.0532)。第 19 步再 +y 10 cm，stopped=blocked，只到 y=0.127，残差约 5.2 cm。第 20 步抬 7 cm 脱离，z=1.1111。第 21 步 +y 6 cm，reached，到 y=0.1845。
第 22 步前移 1.5 cm 并下降 2 cm。第 23 步再下降 2 cm，planned_env_steps=50，名义 reached 但 z 残差 1.8 cm，末端 (0.0709, 0.1843, 1.0971)。第 24 步张开，开度 0.628；记录写明在空腔上方释放，碗落入底层抽屉。
第 25 步 −y 12 cm 并抬 2.5 cm 退出，到 (0.0729, 0.0648, 1.1244)，开度 0.977。第 26–28 步外退并下降到 z=1.0118。第 29–30 步各 +y 2 cm 试推，到 y=0.0488，记录认为未明显推动。第 31 步 −y 4 cm。第 32–33 步再下降到 z=0.9843。
第 34–42 步连续 +y 约 2 cm 推面板，y 从 0.0249 到 0.1263，开度约 0.98；第 36 步起记录写面板向柜内移动、碗仍在抽屉内。第 43 步再 +y 2 cm，planned=50，名义 reached 但 y 只从 0.1263 到 0.1272，残差 1.9 cm。
第 44 步 −y 3 cm 并 roll 到约 18.6°。第 45 步下降并把 roll 加到约 39.3°，z=0.953。第 46–49 步保持约 40° 继续各 +y 2 cm，到 y=0.138。第 50 步 +y 2 cm 并下降 1.5 cm，reached，末端 (0.0555, 0.1504, 0.9424)，roll=40.0，开度 0.983。随后 max_moves，state.success 仍为 false。

## 提示词
桥启动前，工作区 PROMPT.txt 由 PROMPT_BASE_3.txt 按字节复制（11260 字节）；桥刚就绪时 run 目录内的 PROMPT.txt 与 PROMPT_BASE_3.txt `cmp` 一致。没有 {{LESSONS}}，没有运行 compose_prompt.py，没有注入 LESSONS.md。LIBERO_WORLD_AXES=0，没有在提示词前附加世界坐标轴说明。Codex 使用 clean 的 `model_instructions_file` 指向工作区 `/home/chener/LIBERO/astra_eval/PROMPT.txt`。CODEX_HOME 为隔离临时目录 `/tmp/codex-clean-ZOZ0`，只符号链接 auth.json、models_cache.json、config.toml、sessions，没有 skills/ 或 plugins/，退出时已删除该临时目录，未删除 ~/.codex/sessions。回合结束后，run 目录里的 PROMPT.txt 仍与 PROMPT_BASE_3.txt 字节一致（11260 字节）；工作区 PROMPT.txt 同样仍一致。

## 限制
LIBERO_MAX_MOVES=50，LIBERO_MAX_ENV_STEPS=600，LIBERO_WORLD_AXES=0，planner=astra，suite=libero_10，task_id=3，init_id=0。

## Codex 退出码
0。codex.log 中没有 ChatGPT usage limit 或 quota 错误。会话末尾记录 tokens used 70,860。启动时有一条非致命 websocket TLS handshake eof（随后请求继续并完成回合），不是用量限制。
