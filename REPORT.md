# LIBERO × 视觉语言规划器：Direct-EEF 闭环实验报告

**实验窗口：** 2026-09-20 20:20 – 2026-09-21 20:30（UTC+8，约 24 小时）  
**机器：** WSL Linux，`conda activate libero`，`MUJOCO_GL=egl`，NVIDIA RTX 3080 Laptop  
**代码：** `/home/chener/LIBERO/astra_eval`  
**原始流水账：** [`EXPERIMENT.md`](EXPERIMENT.md)　**回放页：** [`viz/index.html`](viz/index.html)

---

## 0. 一页摘要

在官方 LIBERO 仿真里，用 **RGB + 语言指令 → 世界系笛卡尔目标** 的闭环（RoboProbe L3 / Direct-EEF）评估两个规划器：

| 规划器 | 入口 | 模型设定 |
|---|---|---|
| **Astra** | 本地 Codex CLI `codex exec -m gpt-6-astra` | `reasoning_effort=medium` |
| **Grok** | 本地 Grok CLI（后期为 nested `grok --prompt-file`） | 同一份 `PROMPT.txt`，同一座 HTTP 桥 |

**官方成功判据只有 `env.check_success()`。** 规划器看不到物体位姿、BDDL、深度或奖励。每条 episode 是 **一个 suite × 一个 task × 一个 init（init 0）**，不是官方 20-init 套件分。

截至 2026-09-21 20:30：

| | 完成 episode | 官方成功 | 备注 |
|---|---:|---:|---|
| Astra | 16（含 2 次 harness 中断、1 次额度中断、1 次 resume） | **6** | spatial/0×2、object/4 番茄酱、goal/0 抽屉、goal/7 灶（开坐标轴）、goal/8 碗 |
| Grok | 13（含 1 次用户中止） | **1** | goal/7 开灶（双相机坐标轴）；goal/8 空夹失败 |
| 合计归档 | 32 个 run 目录 | 7 成功 | `runs/attempt_*` + 两个早期 named run |

**三句话结论：**

1. 同一座桥、同一套相机约定下，Astra 能在厨房桌面（碗、抽屉、灶）和地面（番茄酱瓶颈）上完成接触级闭环；Grok 在对照任务上多次停在空夹或错误姿态。
2. 失败几乎都发生在 **夹爪缝是否包住物体**，而不是语言理解：两个模型都能点名正确物体，并做 +x 探针确认图像方向。
3. 世界坐标轴叠加（`LIBERO_WORLD_AXES=1`）能稳住轴向符号、帮助灶具这类「高度 + 绕 z 转动」任务；它 **不** 替代腕部缝隙对齐，也 **不** 告诉模型抽屉把手该用 roll 还是 yaw。

---

## 1. 实验配置

### 1.1 问题设定

能否只靠两路 RGB 和语言指令，让一个通用视觉语言模型以 **绝对世界系笛卡尔目标** 驱动 Panda，在 LIBERO 官方 `check_success()` 上闭环？

这是 **Direct-EEF**：没有 VLA 权重、没有示教、没有物体 6D、没有深度。观测是文件（`obs/agentview.png`、`obs/wrist.png`、`obs/state.json`），动作是 HTTP `POST /move`。

### 1.2 仿真与机器人

| 项 | 设定 |
|---|---|
| 环境 | `OffScreenRenderEnv`（LIBERO / robosuite 1.4） |
| 机器人 | Franka Panda，`OSC_POSE`，`control_delta=true`，20 Hz，动作维 7 |
| 插值 | 世界系直线段，约 0.05 m / 0.5 rad 每物理步，到达阈值 ≈ 1.2 cm |
| 夹爪命令 | `1` = 开，`0` = 关。Panda 底层 `+1` 闭合、`-1` 张开（本机核实后写进桥） |
| 预算 | 官方 600 env steps；规划器默认 30 次 `/move`，对照实验多为 25 |
| Init | 每个任务官方 50 个 init 中的 **id 0** |
| 随机种子 | `env.seed(0)` + `set_init_state(inits[0])`，reset 后再走 5 步零动作稳物理 |

### 1.3 评测的任务（全部 init 0）

| Suite | Task | 指令 | 场景高度 |
|---|---|---|---|
| `libero_spatial` | 0 | pick up the black bowl between the plate and the ramekin and place it on the plate | 厨房桌，home z≈1.17，桌面 ≈0.90 |
| `libero_spatial` | 1 | pick up the black bowl next to the ramekin and place it on the plate | 同上 |
| `libero_spatial` | 2 | pick up the black bowl from table center and place it on the plate | 同上 |
| `libero_spatial` | 3 | pick up the black bowl on the cookie box … | 同上（Grok 中途停下） |
| `libero_object` | 0 | pick up the alphabet soup and place it in the basket | 地面，home z≈0.26 |
| `libero_object` | 4 | pick up the ketchup and place it in the basket | 地面 |
| `libero_object` | 7 | pick up the milk and place it in the basket | 地面 |
| `libero_goal` | 0 | open the middle drawer of the cabinet | 厨房桌 |
| `libero_goal` | 7 | turn on the stove | 厨房桌 |
| `libero_goal` | 8 | put the bowl on the plate | 厨房桌 |

`libero_10` 未跑。

### 1.4 观测与坐标

规划器每步可读：

- **agentview** 256×256 RGB（第三人称）
- **wrist** `robot0_eye_in_hand` 256×256 RGB（眼在手上，fovy 75°）
- `state.json`：指令、suite/task/init、EEF xyz、相对 reset 的 roll/pitch/yaw（度）、`gripper_open`∈[0,1]、剩余预算、`success`、`terminated`、`feedback`

**不提供：** 物体名列表以外的几何、6D 位姿、深度、力、BDDL、reward。

图像保存约定与 OpenVLA / π0 的 LIBERO 评测一致：`img[::-1, ::-1]`。保存后：

- agentview：**机械臂在画面上方**，桌面/物体在下方
- wrist：**夹爪垫在画面底部**
- 世界 `/move` 的 xyz **不随 PNG 旋转翻转**

Agentview 轴向速查（写进 prompt）：

| 世界轴 | 在 agentview 上的表观 |
|---|---|
| +x | 夹爪移向画面 **底部**（远离躯干、深入工作区） |
| −x | 移向画面顶部（回到躯干） |
| +y | 画面 **左** |
| −y | 画面 **右** |
| +z | 升高（不是图像向上）；物体在腕部图里变小 |

腕部图「向上」**不是** 世界 +y。左右以 agentview 为准。

EEF 位姿是 MuJoCo/robosuite **世界系** 米：`robot0_eef_pos` 为 Panda `grip_site`，quat 为 eef body。厨房桌 home ≈ (−0.21, −0.01, 1.17)；地面套件 home ≈ (−0.15, −0.01, 0.26)。不要把厨房的 z 下限 0.82 用到地面（地面下限 ≈ 0.03）。

### 1.5 HTTP 桥（`bridge_server.py`）

单进程 `HTTPServer`（第一晚多线程把 EGL 相机打黑之后改回单线程），`127.0.0.1:8765`：

| 方法 | 作用 |
|---|---|
| `GET /status` | 刷新 `obs/*.png` 与 `state.json` |
| `POST /move` | 只改 JSON 里 **点名** 的轴；未点名的 xyz/rpy 保持当前值；未点名的 gripper 保持 **上一次命令**（不是模拟的 `gripper_open`） |
| `POST /give_up` | 规划器主动结束，需 `reason` / `hindsight` |

`/move` 回包带 `last_move`：点名轴、目标、`final_dist_m`、`stopped`∈{reached, blocked}、`feedback`。`feedback` 只有两类：

- `blocked/contact`：卡住，笛卡尔目标没到
- `ok` / `reset`：插值走完或开局

夹持是否成功 **只看图像 + `gripper_open`**。早期的 `empty_grasp_suspected` / `holding_or_pinching` 模板已删掉，避免规划器被字符串带跑。

每 20 Hz 控制步归档到 `runs/<attempt>/ctrl/` 与 `steps.jsonl`（7 维动作 + 两路 RGB）。每个 `/move` 边界另存 `frames/`。

### 1.6 Prompt 与两套规划器入口

后期对照统一用 **`PROMPT_BASE_2.txt`**，`{{LESSONS}}` 替换成 “(no extra accumulated lessons)”。也就是：**不把上一局的战报灌进下一局**，只保留静态规则：

- 强制开局 +x 3 cm 探针，核对图像方向
- 闭合前在 note 里写 `close now would trap the object: yes/no`；只有腕部图里物体在 **两垫之间的缝** 才允许 `gripper=0`
- 平移前判断会不会撞；撞了先抬 / 改姿态
- 闭合后先 +z 2 cm 验夹，物体没起来立刻回去改 xy/z/pitch
- 取向每步最多 ±20°
- 真夹住之后每次 lift/transport **必须点名 `gripper=0`**

Astra 入口：`run_episode.sh` → `codex exec -m gpt-6-astra`，prompt 走 stdin（Codex `-i` 是可变参数，位置参数会被吃掉），只在开局把两张 reset 图用 `-i` 附上。后续观测靠读文件。

Grok 入口：`start_bridge.sh` 只起桥；策略进程是 Grok CLI。后期改为 nested：

```text
grok --prompt-file PROMPT.txt --always-approve --verbatim \
     --cwd /home/chener/LIBERO/astra_eval \
     --max-turns 250 --disallowed-tools Agent
```

两套规划器打同一座桥、同一套图像、同一份 prompt。

### 1.7 世界坐标轴叠加（可选）

`LIBERO_WORLD_AXES=1` 时，桥在 **保存后的 PNG** 上画半透明世界 XYZ 三轴（α=0.5），**不往 MuJoCo 场景里加 geom**：

- +X 红，+Y 绿，+Z 蓝（图上 Z 偏橙）
- 原点在该相机光轴、画面中心附近
- agentview 相机位姿相对固定；wrist 每帧从 `robot0_eye_in_hand` 重读

投影按 robosuite OpenCV 外参（`diag(1,-1,-1)`）再补一次水平翻转，对齐 `img[::-1, ::-1]` 后的像素。

![Agentview 世界轴（厨房桌）](report_assets/fig_axes_agentview.png)

![Wrist 世界轴（地面木板，垫在画面底部）](report_assets/fig_axes_wrist.png)

Prompt 里有一句：画面中心半透明 RGB 三轴是世界 +X/+Y/+Z，不是场景物体。

### 1.8 本报告怎么计「成功」

- **成功** = `result.json` 里 `success=true`，来源只有 LIBERO `check_success()`。
- 视觉上「看起来进篮子」不算（见 attempt_019）。
- harness 崩溃、Codex 额度、用户中止单独标注，不计入规划器能力，但列入时间线。
- 样本量是 **单 init 定性**，不能当成套件成功率。

---

## 2. 改进时间线

按墙钟顺序。每一段都改了「下一局规划器实际面对的世界」。

### 阶段 A · 把桥跑通（9-20 20:20–20:50）

| 时间 | Run | 发生了什么 |
|---|---|---|
| 20:22 | spatial0 attempt1 | `ThreadingHTTPServer` 在非 EGL 线程里 `/move`，相机变黑；夹爪符号反了。Astra 2 步放弃。 |
| 20:30 | spatial0 attempt2 | 单线程 + 夹爪符号修正。第一次真正的策略：四次同高度顶视闭合，碗不起。 |
| 20:39 | attempt_003 | 未点名的 rpy 被调节逻辑拧腕；Codex 退出。 |
| 20:48 | attempt_004 | 打开 pitch。侧壁夹到了，但 6–7 cm 一次抬起，捏滑。 |
| **20:57** | **attempt_005** | **Prompt：先 2 cm 验夹、取向 ±20°/步、没起来不准运。官方成功。** 15° 侧壁，短抬，再抓，放到盘上。 |

这是第一晚的核心控制课：**接触精度，不是语义。** 碗在盘和烤盅之间能被认出来；失败在闭合高度和抬升幅度。

### 阶段 B · 把课写进 LESSONS，并开始对照 Grok（9-20 21:00–9-21 00:10）

| 时间 | Run | 发生了什么 |
|---|---|---|
| 21:09 | attempt_006 spatial/1 | 真夹到 g≈0.71，但后续 `/move` **没点名 gripper=0**，桥按「保持上次命令」把爪打开。碗被推走。 |
| 21:18 | attempt_007 spatial/2 | Codex ChatGPT 额度用尽，7 步中断，爪停在灶上。 |
| 23:09–00:10 | Grok 008–010 | 同一套 spatial 0/1/2。Grok 在 t0 **夹起过碗**，运到盘边却 **30 步内从未张开**；t1/t2 是连续空夹。 |

新规则进 `LESSONS.md`：真夹之后每次都写 `gripper=0`；腕部充满 ≠ 接触；空夹 g≈0.02 要改 xy，不要沿 +x 追沿。

### 阶段 C · 图像约定、PROMPT_BASE_2、地面套件（9-21 上午–下午）

| 时间 | 改动 |
|---|---|
| 上午 | PNG **固定** `img[::-1, ::-1]`。Prompt 描述「臂在上、桌在下」，不再对规划器讲 rot180 实现细节。 |
| 上午 | `ctrl/` + `steps.jsonl`：20 Hz 全轨迹，支持 resume 重放物理。 |
| 11:15 | Grok object/7 牛奶：识别对了，一次 g=0.17 屋脊捏，2 cm 抬空。 |
| 11:47 | **PROMPT_BASE_2、不注入 LESSONS、15 步预算** 的公平对照。Grok 把 Farmers Cheese 当成牛奶。 |
| 11:54 | Astra 同样 BASE_2：GET `/status` 后直接退出（014）。 |
| 12:03 | Astra 015：留在循环里，但全程 jaws-down，两次空抬，15 步不够。 |
| 14:36 | **Astra 016**：BASE_2 静态「碗沿必须在两垫之间」+ 25 步。15° 侧壁，一次闭合就夹住，19 步成功。 |
| 14:47–15:21 | 地面：牛奶（017 夹起，最后一步在篮子旁张开）、resume 018 侧倒纸盒再抓失败、字母汤 019 **视觉在篮内但官方 success=false**。 |
| **15:37** | **Astra 020 番茄酱成功**：瓶颈 g≈0.42，2 cm 验夹，放入篮子。 |

016 说明：哪怕不注入上一局战报，只要 prompt 把「缝里才闭合」写死，Astra 能在 spatial/0 上复现成功，而且比 005 更干净（19 vs 29 步）。

019 是评测课：官方 checker 比「看起来在篮里」更严。规划器不能自己宣布成功。

### 阶段 D · Grok 对照番茄酱 + 世界轴（9-21 16:00–17:10）

| 时间 | Run | 轴 | 结果 |
|---|---|---|---|
| 16:03 | Grok 021 | 关 | 两次空夹 g=0.05，闭合时 x≈−0.018（成功抓大约在 x≈−0.11，差 ~9 cm） |
| 16:33 | Grok 022 | **仅 agentview** | +x 探针与红轴一致；仍两次空夹，在 y 上振荡 |
| 17:07 | Grok 023 nested CLI | **双相机** | 腕部图里瓶子「在垫柱之间」其实在指尖前方（世界 +x），仍空夹 |

世界轴解决了「+x 是不是画面底部」；没有解决「腕部图里的色块是不是夹缝里的物体」。

### 阶段 E · Goal 套件与坐标轴对照（9-21 17:40–20:30）

| 时间 | Run | 任务 | 轴 | 结果 |
|---|---|---|---|---|
| 17:40 | Astra 024 | 开中层抽屉 | 关 | **成功**。roll 分五步到 −90°，横杆进缝，g≈0.23，+y 拉出 |
| 17:49 | Astra 025 | 开灶 | 关 | 三次空夹，闭合高度偏高（z≈1.00 / 0.97），give_up |
| 17:58 | Astra 026 | 碗放盘 | 关 | **成功**。两次空夹后第三次侧壁捏住 |
| **18:07** | **Astra 027** | **开灶（025 的同 init 重试）** | **双相机开** | **成功**。浅夹一次后在 z≈0.955、g≈0.32 咬住，−yaw 转到 −44° |
| 20:08 | Grok 028 | 开中层抽屉 | 双相机开 | 失败。用 **yaw 90°** 正对横杆，空夹；成功姿态是 **roll −90°** |
| **20:18** | **Grok 029** | **开灶** | **双相机开** | **Grok 本窗口唯一官方成功**。z≈0.963、g≈0.31，三次 −20° yaw |
| 20:18– | Grok 030 | 碗放盘 | 双相机开 | **撰写时仍在跑**（已约 19 步，尚未闭合） |

---

## 3. 实验结果

### 3.1 全表

成功标 **是**；中断单独写原因。墙钟为归档时间（UTC+8）。

| Run | 规划器 | 任务 | 轴 | 成功 | 步数 / 物理步 | 墙钟 | 要点 |
|---|---|---|---|---|---|---|---|
| att.1 | Astra | spatial/0 | — | 中断 | 2 / 27 | 2.3 min | EGL 线程 + 夹爪反号 |
| att.2 | Astra | spatial/0 | — | 否 | 24 / 373 | 6.0 min | 四次同高顶视空夹 |
| 003 | Astra | spatial/0 | — | 中断 | 1 / 17 | — | 未点名 rpy 拧腕 |
| 004 | Astra | spatial/0 | — | 否 | 27 / 426 | 6.5 min | 侧壁夹到，一次抬太高滑掉 |
| **005** | Astra | spatial/0 | — | **是** | **29 / 466** | **5.9 min** | 2 cm 验夹 + 再抓放置 |
| 006 | Astra | spatial/1 | — | 否 | 28 / 377 | 6.6 min | 真夹被未点名 gripper 打开 |
| 007 | Astra | spatial/2 | — | 额度 | 7 / 125 | 2.1 min | Codex usage limit |
| 008 | Grok | spatial/0 | — | 否 | 30 / 391 | 25.5 min | 夹起运到盘，**从未张开** |
| 009 | Grok | spatial/1 | — | 否 | 26 / 302 | 28.8 min | 8 次空夹，y 轴没对上 |
| 010 | Grok | spatial/2 | — | 否 | 30 / 321 | 23.9 min | 9 次空夹，一次沿 graze g=0.11 |
| 011 | Grok | spatial/3 | — | 用户停 | 17 / 210 | — | 接近饼干盒上的碗，未闭合 |
| 012 | Grok | object/7 牛奶 | rot180 | 否 | 30 / 372 | 33.8 min | 物体对；屋脊捏 g=0.17 抬空 |
| 013 | Grok | object/7 | BASE_2 | 否 | 15 / 136 | 16.7 min | 追 cheese，15 步用尽 |
| 014 | Astra | spatial/0 | BASE_2 | 中断 | 0 / 5 | 0.4 min | `/status` 后退出 |
| 015 | Astra | spatial/0 | BASE_2 | 否 | 12 / 166 | 3.8 min | jaws-down 两次空抬 |
| **016** | Astra | spatial/0 | BASE_2 | **是** | **19 / 198** | **4.7 min** | 15° 侧壁一次夹住 |
| 017 | Astra | object/7 | BASE_2 | 否 | 25 / 263 | 5.3 min | 夹起牛奶，篮缘旁张开 |
| 018 | Astra resume | object/7 | — | 否 | 19 / 455 | 6.4 min | 侧倒纸盒再抓失败 |
| 019 | Astra | object/0 汤罐 | BASE_2 | 否 | 25 / 264 | 5.4 min | 视觉在篮内，官方 false |
| **020** | Astra | object/4 番茄酱 | BASE_2 | **是** | **21 / 232** | **5.1 min** | 瓶颈 g≈0.42，放入篮子 |
| 021 | Grok | object/4 | BASE_2 | 否 | 22 / 193 | 19.6 min | 空夹；x 偏了 ~9 cm |
| 022 | Grok | object/4 | 轴 on | 否 | 20 / 175 | 22.6 min | 轴向探针正确，仍空夹 |
| 023 | Grok nested | object/4 | 双相机轴 | 否 | 23 / 207 | 22.7 min | 腕部「在柱间」= 指尖前方 |
| **024** | Astra | goal/0 抽屉 | 关 | **是** | **20 / 186** | **4.4 min** | roll −90°，g≈0.23，拉出 |
| 025 | Astra | goal/7 灶 | 关 | 否 | 24 / 224 | 5.9 min | 三次空夹，z 偏高 |
| **026** | Astra | goal/8 碗 | 关 | **是** | **25 / 246** | **5.9 min** | 第三次侧壁捏住并放置 |
| **027** | Astra | goal/7 灶 | **双相机轴** | **是** | **20 / 200** | **5.1 min** | z≈0.955，−yaw |
| 028 | Grok nested | goal/0 抽屉 | 双相机轴 | 否 | 25 / 334 | 19.0 min | yaw 90° 空夹 |
| **029** | Grok nested | goal/7 灶 | **双相机轴** | **是** | **15 / 145** | **8.2 min** | z≈0.963，−yaw 到 −54° |
| 030 | Grok nested | goal/8 碗 | 双相机轴 | 否 | 24 / 221 | 19.7 min | 唇沿空夹 g=0.14→0.02，give_up |
| 032 | Astra | goal/8 碗 | 双相机轴 | 额度 | 24 / 239 | 5.2 min | 碗已放到盘上，最后 1 步额度中断 |

Astra 单局墙钟大约 **4–6 min**，token 大约 5–9 万（成功局常见 5.3–8.3 万）。Grok 单局大约 **8–34 min**，多数在 15–25 min。

### 3.2 按套件看 Astra

**libero_spatial（碗 → 盘）**

- 从「顶视捏沿」改到「10–20° pitch、沿进两垫缝、2 cm 验夹」之后，**同一 init 上两次官方成功**（005、016）。
- 016 在不注入 LESSONS 时仍成功，说明静态 prompt 已经够这条任务。
- spatial/1 暴露 harness 语义：未点名 gripper 保持的是 **命令** 不是宽度，会把真夹打开。
- 成功放置帧（016）：碗已在盘上，爪仍可闭合——官方 checker 在未张开时也会给 true。

![Astra 016：黑碗已在盘上（官方成功）](report_assets/fig_a016_bowl_success.png)

Astra 016 agentview 全程（20 Hz 控制步，约 10 s，2× 邻近放大）：

<video src="report_assets/vid_a016_bowl_success.mp4" controls width="512"></video>

**libero_object（地面，拣入篮）**

| 物体 | 结果 | 接触数字 |
|---|---|---|
| 牛奶纸盒 t7 | 夹起 (g≈0.67) 后在篮缘张开 | 真夹；失败在最后一步把开爪和横移写在一起 |
| 字母汤 t0 | 视觉在篮内 | 官方 false（checker 比 RGB 严） |
| 番茄酱 t4 | **官方成功** | 瓶颈、jaws-down、g≈0.42 全程稳定 |

番茄酱成功路径很干净：探针 → 高处 −y 平移 → 逐步降到 z=0.130 → 腕部确认瓶颈在缝中 → 闭合 g=0.426 → 2 cm 验夹 g=0.419 瓶子起来 → 抬到 0.28 → 越过邻居 → 篮口 z=0.213 张开。21 步全部 `reached/ok`。

![Astra 020 闭合瞬间腕部：瓶颈填满两垫之间](report_assets/fig_a020_close_wrist.png)

![Astra 020 结束：番茄酱立在篮中，邻居仍在地上](report_assets/fig_a020_ketchup_success.png)

Astra 020 agentview 全程（20 Hz，约 12 s）：

<video src="report_assets/vid_a020_ketchup_success.mp4" controls width="512"></video>

**libero_goal**

- **抽屉 t0：** 需要沿世界 +x 的手指（roll ≈ −90°），横杆进缝后 g≈0.23，再 +y 拉。Astra 一次成功。
- **开灶 t7：** 无轴时三次咬空（闭合在杠杆尖、z 偏高）；开轴后降到 z≈0.955，g≈0.32，负 yaw 成功。
- **碗→盘 t8：** 两次空夹后第三次侧壁成功，用满 25 步。

![Astra 024：中层抽屉被拉出，roll ≈ −90°](report_assets/fig_a024_drawer_success.png)

Astra 024 agentview 全程（20 Hz，约 9 s）：

<video src="report_assets/vid_a024_drawer_success.mp4" controls width="512"></video>

![Astra 027：灶已打开（画面左上旋钮偏转），世界轴仍在](report_assets/fig_a027_stove_success.png)

Astra 027 agentview 全程（20 Hz，约 10 s）：

<video src="report_assets/vid_a027_stove_success.mp4" controls width="512"></video>

Astra 026 agentview 全程（20 Hz，约 12 s）：碗放盘成功。

<video src="report_assets/vid_a026_bowl_success.mp4" controls width="512"></video>

### 3.3 反复出现的失败模式

1. **开口叠加 ≠ 接触。** agentview 里张开的爪投影在物体上，闭合轴却在物体旁或前方。空夹特征：`gripper_open` 立刻到 ≈0.05。
2. **腕部充满 ≠ 在缝里。** 碗/瓶占满腕部图，常常是近沿顶在垫上，或物体还在指尖前方（世界 +x）。
3. **一次抬太高。** 浅捏 g≈0.14–0.17，2 cm 验夹会掉到 0.02；6–8 cm 直接滑。
4. **未点名 gripper 打开真夹**（006）。
5. **运到目标后不张开**（Grok 008）或 **张开与横移写在同一调用、丢在篮外**（Astra 017）。
6. **官方 checker 严于视觉**（019）。
7. **姿态选错自由度：** 抽屉横杆要用 roll，Grok 028 用了 yaw 90°，爪垫打在把手面上。

`LESSONS.md` 里现在的可迁移数字（供下一轮，**对照实验故意不注入**）：

- 厨房碗侧壁：pitch 10–20°，z≈0.91–0.92，真夹 g≳0.14 且 2 cm 抬仍保持
- 地面牛奶身：z≈0.08–0.10，真包裹 g≳0.40；g=0.17 再掉到 0.02 是屋脊
- 番茄酱瓶颈（该 init）：eef ≈ (−0.11, −0.23, 0.13)，g≈0.42；篮口释放 ≈ (0.02, 0.27, 0.21)
- 中层抽屉（该 init）：≈ (0.03, −0.13, 1.02)，roll −90°，g≈0.23，再 +y
- 灶杠杆（该 init）：z≈0.955–0.963，g≈0.31–0.44，**原地负 yaw**，不要抬

### 3.4 Astra 失败：Codex 额度与规划器步数

Astra 的失败不全是夹不住。有两类把已经接近完成的 episode 掐断：**ChatGPT / Codex 额度**，以及 **规划器 `/move` 预算用尽**。下面几局都有 agentview 全程。

**A. Codex 额度用尽（CLI 报 usage limit，进程退出）**

| Run | 任务 | 中断时 | token | 当时场景 |
|---|---|---|---|---|
| 007 | spatial/2 桌心碗 | 7 /move，125 物理步 | 1.7 万 | 15° 下降后 −x 退到灶上，闭合 g≈0.69，腕部没有碗。额度在 2 cm 验夹之前到来。 |
| 032 | goal/8 碗放盘 | 24 /move（预算 25），剩 1 步 | 8.4 万 | 侧壁夹住、运到盘上、张开。画面里碗压在盘上，官方 `check_success()` 仍为 false。额度在最后一次微调前到来。 |

007 结束：爪停在灶上，目标碗在画面右侧未动。

![Astra 007：额度中断，爪在灶上](report_assets/fig_a007_quota.png)

Astra 007 agentview（按 `/move` 边界，约 4 s）：

<video src="report_assets/vid_a007_quota.mp4" controls width="512"></video>

032 结束：碗与盘重叠，爪已张开上收。官方仍未给成功。

![Astra 032：额度中断，碗在盘上但 checker 未过](report_assets/fig_a032_quota.png)

Astra 032 agentview 全程（20 Hz，约 12 s）：

<video src="report_assets/vid_a032_quota.mp4" controls width="512"></video>

**B. 规划器步数用尽（`max_moves` 或剩余步不够再抓一次）**

对照实验默认 25 次 `/move`。Astra 026 用满 25 步仍然成功；017 / 019 同样用满 25 步，失败发生在释放。015 当时预算只有 15 步。

| Run | 任务 | 结束方式 | 还剩 | 当时场景 |
|---|---|---|---|---|
| 015 | spatial/0 碗 | give_up | 3 | 全程 jaws-down，两次空抬。15 步预算不够做侧壁再抓。 |
| 017 | object/7 牛奶 | max_moves | 0 | 第三次闭合 g≈0.67 真夹，运到篮缘。最后一步把 +y 与 `gripper=1` 写在一起，纸盒掉在篮外。 |
| 018 | 017 的 resume | give_up | 1 | 侧倒纸盒再抓两次空夹，剩 1 步不够「再抓 + 验夹 + 运 + 单独张开」。 |
| 019 | object/0 字母汤 | max_moves | 0 | 真夹 g≈0.75，张开后罐子视觉上在篮内。官方 checker 仍为 false，没有剩余步数再放一次。 |
| 025 | goal/7 开灶 | give_up | 1 | 三次空夹，见 §4.4 视频。 |

015 结束：碗仍在桌上，爪已空。

![Astra 015：15 步预算用完前放弃](report_assets/fig_a015_budget.png)

Astra 015 agentview 全程（20 Hz，约 8 s）：

<video src="report_assets/vid_a015_budget.mp4" controls width="512"></video>

017 结束：牛奶纸盒立在篮外地面。

![Astra 017：25 步用尽，牛奶掉在篮旁](report_assets/fig_a017_milk_fail.png)

Astra 017 agentview 全程（20 Hz，约 13 s）：

<video src="report_assets/vid_a017_milk_fail.mp4" controls width="512"></video>

018 是 017 的物理续跑：侧倒后再抓失败。

Astra 018 agentview 全程（20 Hz，约 10 s）：

<video src="report_assets/vid_a018_budget.mp4" controls width="512"></video>

019 结束：字母汤罐在篮内，官方仍为 false。

![Astra 019：25 步用尽，视觉在篮内](report_assets/fig_a019_soup_fail.png)

Astra 019 agentview 全程（20 Hz，约 13 s）：

<video src="report_assets/vid_a019_soup_fail.mp4" controls width="512"></video>

**怎么读这两类失败**

- 额度中断发生在 Codex CLI 进程层，桥和物理还活着。007 停在错误接触上；032 停在「看起来已经放好、checker 未翻转」上。两者都少了最后几次 `/move`。
- 步数用尽发生在策略层：真夹之后把开爪和横移写在同一步（017），或释放后没有余量应付更严的官方 checker（019）。026 用满 25 步成功，说明 25 步对 goal 碗够用，对「先空夹两次再运牛奶/汤罐」不够。
- 014（GET `/status` 后退出、0 次 `/move`）是会话早退，不是额度，也没有可看的运动视频。

---

## 4. Astra 与 Grok 对照

同一座桥、同一 init、同一语言指令。后期还固定 `PROMPT_BASE_2`、不注入 LESSONS、25 步预算。

### 4.1 任务级对照

| 任务 | Astra | Grok | 差距落在哪 |
|---|---|---|---|
| spatial/0 碗 | 005 **是**，016 **是** | 008 否（夹起，盘上不放） | Grok 接触过，释放策略用尽预算 |
| spatial/1 碗 | 006 否（真夹被打开） | 009 否（8 次空夹） | 两边都没放成；Grok 从未接触 |
| spatial/2 碗 | 007 额度中断 | 010 否（9 次空夹） | Grok 全程空夹 |
| object/7 牛奶 | 017 夹起丢在篮旁 | 012 屋脊捏；013 认成 cheese | Astra 完成抓取；Grok 抓取或认物失败 |
| object/4 番茄酱 | **020 是**（1 次闭合） | 021/022/023 否（各 2 次空夹） | 见 4.2 |
| goal/0 抽屉 | **024 是**（roll −90°） | 028 否（yaw 90°） | 见 4.3 |
| goal/7 灶 | 025 否 → **027 是**（开轴） | **029 是**（开轴） | 两边开轴后都能做；无轴 Astra 失败 |
| goal/8 碗 | **026 是** | 030 否（唇沿空夹） | 见下方视频 |

在 **已结束且非中断** 的对照里，Astra 官方成功 6 次，Grok 1 次。Grok 的成功出现在「开轴 + 开灶」这条 Astra 刚跑通的任务上。

Grok 030 goal/8 碗放盘失败（20 Hz，约 11 s）：两次唇沿空夹。

<video src="report_assets/vid_a030_bowl_fail.mp4" controls width="512"></video>

### 4.2 深挖：番茄酱（object/4 init 0）

这是最干净的一对。Prompt、预算、init、物体完全相同。

| | Astra 020 | Grok 021 | Grok 022（agentview 轴） | Grok 023（双相机轴） |
|---|---|---|---|---|
| 成功 | **是** | 否 | 否 | 否 |
| `/move` | 21 | 22 | 20 | 23 |
| 闭合次数 | **1**（m10） | 2 | 2 | 2 |
| 闭合后 g | **0.426** | 0.05 / 0.05 | 0.05 / 0.05 | 0.05 / 0.05 |
| 闭合 x | ≈ −0.11 | **≈ −0.018**（偏 +x ~9 cm） | ≈ −0.088 | ≈ +0.01～0.04 |
| 墙钟 | 5.1 min | 19.6 min | 22.6 min | 22.7 min |

Astra 的判据：腕部图 **底边** 用来看前后（世界 x）；瓶颈必须填满两垫缝才写 `close now: yes`。m06 明确写 no（盖太靠近腕部底边），继续降，m10 才闭。

Grok 的判据：腕部图 **左侧垫上的一条红色** 被当成「已经在缝里」，然后在 **y** 上左右找。021 结束时瓶子在闭合爪的左侧，爪已经拍在瓶子前方的地板上：

![Grok 021 结束：爪已闭合（空），番茄酱仍在地面、在爪的 −y 侧](report_assets/fig_a021_ketchup_fail.png)

Grok 021 agentview 全程（20 Hz，约 10 s）：两次空夹，x 停在瓶子前方。

<video src="report_assets/vid_a021_ketchup_fail.mp4" controls width="512"></video>

022 开了世界轴以后，Grok 的 +x 探针与红轴一致（画面底部），说明 **轴向符号已经对了**。失败仍是夹缝几何：薄瓶在 8 cm 张开时看起来像「在两垫之间」，闭合中心却空。

Grok 022 agentview 全程（20 Hz，约 9 s，画面中心有世界轴）：

<video src="report_assets/vid_a022_ketchup_axes.mp4" controls width="512"></video>

### 4.3 深挖：中层抽屉（goal/0 init 0）

| | Astra 024 | Grok 028 |
|---|---|---|
| 成功 | **是** | 否 |
| 取向 | roll 分五步到 **−90°**（手指在杆上下） | yaw 到 **90°**（垫打在杆面上） |
| 闭合 g | **0.228** 并保持 | 0.05 → 0.018（空） |
| 之后 | +y 试拉，抽屉跟着走 | +y 拉的是空爪 |
| 轴 | 关 | 开（双相机） |

世界轴把 +x/+y/+z 画在画面中心，**不编码「这个把手是一根沿 y 的横杆」**。Grok 看到了柜子和中层，选错了旋转轴。Astra 在 note 里写了「pads close along the bar」，并按 20° 一步把 roll 走到 −90。

![Grok 028 结束：世界轴开着，爪在工作区中央空闭，抽屉仍关](report_assets/fig_a028_drawer_fail.png)

Grok 028 agentview 全程（20 Hz，约 17 s）：yaw 转到 90° 后空夹，抽屉未动。

<video src="report_assets/vid_a028_drawer_fail.mp4" controls width="512"></video>

### 4.4 深挖：开灶（goal/7 init 0）——两边都能做的一条

| | Astra 025 | Astra 027 | Grok 029 |
|---|---|---|---|
| 轴 | 关 | **开** | **开** |
| 成功 | 否 | **是** | **是** |
| 闭合 | 3 次空（g=0.05） | 1 次浅 + 1 次真夹 g≈0.32 | 1 次真夹 g≈0.31 |
| 闭合 z | ≈1.00 / 0.97 | **0.955** | **0.963** |
| 转动 | +20° yaw，灶不动 | 正 yaw 无效，改 **负 yaw 到 −44°** | 三次 **−20° yaw 到 −54°** |
| `/move` | 24 | 20 | **15** |

无轴时 Astra 在杠杆尖闭合。开轴后两个模型都把高度降到 ~0.96、咬住柄身、用负世界 yaw 原地转。Grok 029 还读了 027 的 NOTES（nested 会话能看见仓库文件），接近「开卷考试」；即便如此，它把接触数字做对了，是本窗口 Grok 唯一的官方成功。

Astra 025 关轴失败（20 Hz，约 11 s）：

<video src="report_assets/vid_a025_stove_fail.mp4" controls width="512"></video>

Grok 029 开轴成功（20 Hz，约 7 s）：

<video src="report_assets/vid_a029_stove_success.mp4" controls width="512"></video>

### 4.5 行为差异（在本窗口里稳定出现）

| 维度 | Astra | Grok |
|---|---|---|
| 物体识别 | 016/020/024/026/027 都点名正确目标 | 多数正确；013 把 cheese 当牛奶 |
| 闭合纪律 | 更常在腕部缝里才闭；020 全程一次闭合 | 空夹次数多；「垫上一条颜色」就闭 |
| 取向 | 主动用 pitch（碗）和 roll（抽屉） | 抽屉用错 yaw；碗任务会 pitch，接触仍偏 |
| 释放 | 016 未张开 checker 已过；020 单独一步张开 | 008 夹到盘边不张；021–023 空爪就放弃 |
| 速度 | 4–6 min / 局，~5–9 万 token | 15–25 min / 局（029 灶 8 min） |
| 循环 | 014 曾 GET 后退出；015 之后能留在环里 | nested CLI 能跑满 25 步 |

差距主要在 **视-动接触**：同一张腕部图，Astra 把「底边」当前后、把「两垫缝」当闭合条件；Grok 容易把投影重叠当成可闭，并在次要轴（y）上搜索，主误差轴（x 或 roll）不动。

---

## 5. 坐标轴可视化带来的效果

### 5.1 做了什么

从 attempt_022 起可开关。PNG 中心半透明世界 XYZ，双相机（022 先只画 agentview，023 起腕部也画）。Prompt 增加一行说明。MuJoCo 里没有多出任何几何体，规划器仍只看 RGB。

地面番茄酱开轴后的 agentview（红轴指向画面底部 = 世界 +x，篮在 +y / 画面左）：

![Grok 022 开局：地面套件 + 世界轴](report_assets/fig_a022_ketchup_axes.png)

厨房开灶开轴后的 agentview（灶在画面左 = +y）：

![Astra 027 开局：厨房 + 世界轴，灶在 +Y 方向](report_assets/fig_a027_stove_axes.png)

### 5.2 有对照的证据

**A. 轴向符号：有帮助。**  
022 强制 +x 3 cm 探针后，Grok 写明「+x → agentview BOTTOM，与红轴一致」。此前只靠文字速查表，模型有时仍会在中途把腕部「上」当成 +y。开轴后，本窗口 **没有再出现整轴反号** 的给法。

**B. 开灶：有帮助（025 vs 027，再加 029）。**  
同一 init、同一 Astra、同一 BASE_2：

- 关轴：三次空夹，z 停在 1.00 / 0.97，give_up
- 开轴：一次浅夹后降到 0.955，咬住，负 yaw，官方成功

Grok 029 在双相机轴下 15 步成功，闭合高度与 027 只差 ~8 mm。开灶是「找一个细杠杆的高度，再绕世界 z 转」，三轴画在画面中心，和「+z 升高、+y 朝灶、yaw 绕蓝轴」直接对齐。

关轴失败结束帧：爪在灶上方，旋钮未转。

![Astra 025 关轴失败：灶仍关](report_assets/fig_a025_stove_fail.png)

Astra 025 agentview 全程见 §4.4。

**C. 番茄酱夹取：几乎没有帮助。**  
021 关轴 / 022 单相机轴 / 023 双相机轴，Grok 都是两次空夹后放弃。轴让 +x 探针更自信，闭合误差仍是「薄瓶相对夹缝的前后（x）」，腕部图上的红条在左垫上。轴画在画面中心，不画夹爪缝。

**D. 抽屉：没有帮到 Grok。**  
028 双相机轴开着，仍选 yaw 90°。轴不告诉你「横杆沿哪根世界轴、手指该绕哪根轴」。Astra 024 在关轴时已经用 roll 成功，说明这条任务的关键是 affordance，不是轴向符号。

### 5.3 怎么解读

世界轴是 **相机–世界符号的视觉锚**，对「往哪边走、往哪边转 yaw」有效，对「两垫之间有没有物体、该用 roll 还是 pitch」无效。

更适合开轴的任务：绕世界 z 的旋钮、沿世界轴的长距离搬运、需要反复确认左右的桌面。  
更不该指望开轴的任务：薄瓶/碗沿的毫米级夹缝、需要换一只旋转轴才能对上的把手。

实现细节（汇报时若被问到）：投影用 live `cam_xpos` / `cam_xmat`；腕部每帧重读；保存 PNG 的 rot180 要求 OpenCV 投影后再把 u 水平翻转一次，否则红轴会画反。

---

## 6. 方法学边界

1. **单 init，不是套件分。** 官方 LIBERO 是每任务 20 个 init × 600 步。这里每条任务只打了 init 0，有的还打了多次（spatial/0、object/4、goal/7）。数字不能外推到 LIBERO 论文表。
2. **后期对照关掉了 LESSONS 注入**，但仓库里仍有 `LESSONS.md` 和上一局 `NOTES.md`。Grok nested 默认能读工作区，029 读了 027 的灶高度。Astra `codex exec` 同样在该目录下。这是「同机可读文件」设定，不是纯图像策略。
3. **019 说明视觉成功 ≠ 官方成功。** 汇报时成功一律以 `result.json` 为准。
4. **014 / 007 / 011** 分别是会话早退、额度、用户停止，不是接触能力。
5. **030 已结束**：Grok goal/8 官方失败（24 /move，唇沿空夹）。视频见 `report_assets/vid_a030_bowl_fail.mp4`。
6. Prompt 从「可 pitch」到 BASE_2「闭合检查 + 碰撞检查 + 强制探针」，和模型能力缠在一起。005 的成功带着 LESSONS；016 起才比较接近「同一张卷子」。

---

## 7. 结论与下一步

**已经能汇报的事实**

- Direct-EEF 桥在这台机器上稳定：单线程 EGL、夹爪符号、世界系 OSC、rot180 图像、blocked/ok 反馈、可选世界轴。
- Astra（gpt-6-astra medium）在 24 小时内于三个套件都拿到过官方成功：桌面碗、地面番茄酱、抽屉、开灶、goal 碗。
- 同一卷子上 Grok 官方成功 1 次（开灶 + 双相机轴），接触失败集中在空夹和错误旋转轴。
- 世界轴对开灶这种「高度 + yaw」任务有前后对照（025 失败 → 027/029 成功）；对番茄酱夹缝和抽屉 roll 没有把失败翻成成功。

**建议的下一轮（仍是单 init 定性，先把对照补全）**

1. 开灶做一次 **Grok 关轴**（现在只有开轴成功），把轴的贡献从「读了 027 笔记」里拆开。
2. 抽屉：在 prompt 里加一句静态 affordance（横杆 → roll ±90），看 Grok 是否还走 yaw。
3. 番茄酱：保持关 LESSONS，只加一句「腕部底边 = 世界 x，左垫色块不是在缝里」——验证 Grok 的失败是不是这一条几何。
4. 若要报套件数字：每个已成功任务再抽 3 个 init，Astra / Grok 各跑一遍，仍用 BASE_2。

**工件位置**

| 内容 | 路径 |
|---|---|
| 本报告插图与 agentview 视频 | `astra_eval/report_assets/`（`vid_*.mp4` 为 20 Hz `ctrl/*_agentview.png`） |
| 每局 NOTES / 轨迹 / 图像 | `astra_eval/runs/attempt_*/` |
| 索引 | `astra_eval/runs/index.jsonl` |
| 实验流水账 | `astra_eval/EXPERIMENT.md` |
| 累积策略（对照实验未注入） | `astra_eval/LESSONS.md` |
| 回放 UI | `astra_eval/viz/index.html`（`build.py` 打包 runs） |
