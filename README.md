# game-ad-sdk-intel

English: [README.en.md](./README.en.md)

面向 **授权场景** 的 Android 小游戏 / 应用 **广告 SDK 策略配置** 逆向分析 Skill。  
给 **Claude Code / Codex** 等 Agent 加载使用：按固定规划分析竞品包，输出可验收的情报，而不是扫一堆字符串交差。

**仓库：** https://github.com/weixiao33661/game-ad-sdk-intel  
**当前版本：** 见 [`VERSION`](./VERSION)（文档对应 **0.3.3+**）  
**Agent 入口：** [`SKILL.md`](./SKILL.md)  
**License：** [MIT](./LICENSE)

---

## 目录

- [解决什么问题](#解决什么问题)
- [核心原则](#核心原则)
- [分析主路径](#分析主路径)
- [八大交付指标](#八大交付指标)
- [阶段流程 P0–P10](#阶段流程-p0p10)
- [卡住时：Playbook](#卡住时playbook)
- [能力地图（汇总扩展）](#能力地图汇总扩展)
- [多厂商支持](#多厂商支持)
- [工作区产物与校验](#工作区产物与校验)
- [Frida 与安全边界](#frida-与安全边界)
- [安装与更新](#安装与更新)
- [仓库结构](#仓库结构)
- [证据档位](#证据档位)
- [常见误用](#常见误用)
- [版本与贡献](#版本与贡献)

---

## 解决什么问题

竞品小游戏往往同时接入 **厂商聚合 / 多家 DSP / Unity 桥 / 加固壳**。只看 AAR 列表或 `strings.xml` 无法回答：

- 真正主链路是谁？
- 远程配置里权重是什么、真机播的是谁？
- 什么用户操作会弹广告、怎么发奖？
- 请求里带了哪些设备字段？数据怎么上报？
- 有没有伪关闭、点击发奖等转化手段？
- 壳是否扫 Frida/maps，分析环境会不会误导结论？

本 Skill 把上述问题收成 **固定工具序 + 阶段门禁 + 8 指标报告 + 卡点 Playbook + 结构校验**，让 Agent（和人）按同一套专业 SOP 执行。

**不是：** 全自动「丢 APK 出真理」的 SaaS，也不是刷量/过生产风控工具。  
**是：** 可重复的竞品广告技术分析作业系统。

---

## 核心原则

| 原则 | 含义 |
|---|---|
| **规划优先** | 产品是 P0–P10 分析规划，不是 LLM 打分 |
| **Static proposes, Dynamic disposes** | 静态提猜想；有设备时用动态证实/否证 |
| **有设备 ⇒ 强制 clean 最小动态** | 展示/触发/发奖结论不能只靠 jadx |
| **配置 ≠ 运行** | 权重表与真播 DSP 必须分两行写（PB-05） |
| **字段要有消费者** | 无 parser→consumer 的键不进主字典 |
| **厂商模型不串** | 小米 `tagid/info[]` 不是 OPPO `posId` |
| **Capability ≠ Active** | 有 AAR ≠ 线上在用 |

机制优先级：

1. 分析规划（工具链 + 阶段 + 8 指标）  
2. 结构化产物  
3. `validate_outputs.py` 硬门禁  
4. eval / llm_judge 仅作 Skill 回归（可选）

---

## 分析主路径

```text
APK
  │
  ▼
① jadx-mcp                 ← 永远第一刀（Java / Manifest / 资源 / 调用链）
  │
  ▼
② native 门闸？
  │   是 → ida-pro-mcp / idalib-mcp 分析关键 .so（壳 / 加密 / 检测 / 决策）
  │   否 → 跳过
  │
  ▼
③ 有 adb 设备？
  │   是 → 【强制】clean 最小动态集（否证/证实猜想）
  │         · 冷启动 · Banner 窗口 · 激励 3～5 次 · 插屏（若有）
  │         · 发奖矩阵（看完 / 只点 / 早关）· 回调顺序
  │         可选：Frida L-Obs / 代理（env 单独标注）
  │   否 → L1 静态交付，结论大量标 hypothesis，写明探针
  │
  ▼
④ 按 8 指标写报告 + strategy_model / bound dict / sdk_inventory
  │
  ▼
⑤ python scripts/validate_outputs.py <工作区>   ← 必须 PASS
```

详细说明：

| 文档 | 内容 |
|---|---|
| [`references/tooling-mcp.md`](./references/tooling-mcp.md) | jadx / IDA 顺序与清单 |
| [`references/dynamic-validation.md`](./references/dynamic-validation.md) | 强制 clean 动态与 hypothesis 格式 |
| [`references/instrumentation-policy.md`](./references/instrumentation-policy.md) | Frida L-Obs / L-Meas / 禁止项 |
| [`references/analysis-pipeline.md`](./references/analysis-pipeline.md) | 阶段与指标映射 |
| [`references/phase-checklist.md`](./references/phase-checklist.md) | 可勾选执行清单 |

---

## 八大交付指标

最终报告（一页纸 + 技术报告）必须覆盖下列章节。  
每条：**结论 | 状态(hypothesis/confirmed/refuted/inconclusive) | 证据 | 缺口探针**。

| # | 指标 | 要回答的问题 |
|---|---|---|
| **0** | 样本与分析路径 | 包名版本渠道、是否 jadx/IDA、是否完成 clean 动态 |
| **1** | 广告请求结构 | 各 endpoint 字段名/样例、谁组装、谁消费、是否加密 |
| **2** | 广告策略 | **展示**（何时 load/show、预加载、bid/串行）· **点击**（是否发奖、伪关闭、落地）· **频控**（日 cap、间隔、关位、关卡） |
| **3** | 用户行为触发 | 通关/领奖/进前台等 → load/show/click/download/reward |
| **4** | 设备画像 | OAID/ROM/型号/版本等采集与上报；「是否真实设备」服务端判决勿妄下 confirmed |
| **5** | 数据链路 | 本地槽位→init→远程配置→DSP→展示→事件→发奖/归因 |
| **6** | SDK 防护 | 加固、壳、maps/Frida 等检测点及对分析的影响 |
| **7** | 风控机制 | 环境信号、请求特征；改策略须 clean 对照 |
| **8** | 竞品策略参数 | 广告位、waterfall/bid、weight、下游 ID、开关、DSP appid |

模板：

- 一页纸 / JSON：[`references/output-templates.md`](./references/output-templates.md)  
- 技术报告：[`references/report-template.md`](./references/report-template.md)

---

## 阶段流程 P0–P10

| 阶段 | 工作 | 主要指标 |
|---|---|---|
| P0 | 范围、设备有无、工具计划 | 路径 |
| P1 | 包名/渠道/引擎/壳/so 列表 | 0、4、6 |
| P2 | jadx 指纹、唯一 primary、打开厂商 depth 卡 | 8、5 |
| P3 | 配置面、请求字段 | **1、4、5** |
| P4 | 生命周期、用户触发 | **3、5** |
| P5 | 展示/点击/频控 + 位与瀑布/竞价 | **2、8** |
| P6 | 绑定字段字典 | 1/4/5/8 |
| P7 | 转化 UX（点击发奖、伪关闭等） | **2.2、3** |
| P8 | 防护与风控（+ 条件 IDA） | **6、7** |
| P9 | **有设备：强制 clean 动态裁决** | 升级 2/3/8… |
| P10 | 8 指标报告 + validate | 全部 |

---

## 卡住时：Playbook

**不要另起一套流程。** 按症状打开子程序（排除法 → 最小下一步 → 升级阶梯 → 报告写法）：

| 现象 | Playbook |
|---|---|
| 多 SDK / 谁是主链路 | [PB-01 主链路裁决](./references/playbooks/PB-01-pick-primary.md) |
| 壳 / `vm_*` / 逻辑在 so | [PB-02 壳与 Native](./references/playbooks/PB-02-shell-native.md) |
| 流量加密、无字段样例 | [PB-03 密文流量](./references/playbooks/PB-03-encrypted-traffic.md) |
| 有设备却不出广告 | [PB-04 No-fill](./references/playbooks/PB-04-no-fill.md) |
| 配置权重 ≠ 真播 DSP | [PB-05 配置 vs 运行](./references/playbooks/PB-05-config-vs-runtime.md) |
| 发奖 / 点击发奖 / 伪关闭 | [PB-06 发奖点击关闭](./references/playbooks/PB-06-reward-click-close.md) |
| Frida/maps 一 hook 就崩 | [PB-07 Frida/maps 检测](./references/playbooks/PB-07-frida-maps-detection.md) |

索引：[references/playbooks/README.md](./references/playbooks/README.md)

---

## 能力地图（汇总扩展）

业务侧完整需求清单（生命周期 14 步、策略字段库、策略识别模式、元数据/事件、风控矩阵、聚合变现、P0/P1/P2 优先级、三大资产库等）已收敛为：

**[references/competitor-analysis-capability-map.md](./references/competitor-analysis-capability-map.md)**

写报告时用它 **查漏**，执行时仍走 SKILL 主路径，避免两套流程打架。

---

## 多厂商支持

| 类型 | 文档 |
|---|---|
| 架构对照 | [oem-architecture-matrix.md](./references/oem-architecture-matrix.md) |
| 指纹与路由 | [china-oem-ad-sdk-fingerprints.md](./references/china-oem-ad-sdk-fingerprints.md) |
| 小米聚合 | [oem-xiaomi-depth.md](./references/oem-xiaomi-depth.md) / [oem-xiaomi-mimo.md](./references/oem-xiaomi-mimo.md) |
| OPPO | [oem-oppo-depth.md](./references/oem-oppo-depth.md) |
| 华为 | [oem-huawei-depth.md](./references/oem-huawei-depth.md) |
| 荣耀 | [oem-honor-depth.md](./references/oem-honor-depth.md) |
| vivo | [oem-vivo-depth.md](./references/oem-vivo-depth.md) |

**硬规则：** 选定唯一 `primary_mediation` 或 `primary_direct_sdk` 后，只用该厂字段模型；GDT/Pangle 等按 capability→wired→configured→active 晋级，禁止「有 AAR 就写瀑布合作方」。

---

## 工作区产物与校验

分析单个包时建议目录：

```text
你的分析目录/
  00_input/                 # APK 等
  01_reports/
    ad_strategy_onepager.md # 8 指标一页纸（中文）
  02_scripts/               # 个案 hook（可选）
  03_logs/                  # logcat / frida
  06_extracted/
    strategy_model.json     # 策略对象 + analysis_path + hypotheses
    field_dictionary_bound.json
    sdk_inventory.json
    evidence_index.md       # 推荐
    unknowns.md             # 推荐
```

`strategy_model.json` 关键字段（摘要）：

- `analysis_path`：是否 jadx、IDA 了哪些 so、`device_available`、`clean_min_dynamic_done` / `dynamic_blocker`  
- `placements[]`：广告位 + waterfall（dsp/parameter/weight）  
- `hypotheses[]`：猜想台账（推荐 `playbook` / `dynamic_test` / `if_fail_next`）  
- `metrics_coverage`：指标 1–8 覆盖状态  

校验与回归：

```bash
# 结构硬门禁（完成分析前必跑）
python scripts/validate_outputs.py /path/to/你的分析目录

# 可选：定义检查 + 对 workspace 判分
python scripts/run_evals.py --workspace /path/to/你的分析目录 --judge

# 可选：单题语义判分（可加 --llm）
python scripts/llm_judge.py --eval-id dcxns-full-strategy --workspace /path/to/你的分析目录
```

有设备时：`device_available=true` 必须 `clean_min_dynamic_done` 或填写 `dynamic_blocker`，且至少 3 条 hypothesis 被 dispose，否则 validate **失败**。

---

## Frida 与安全边界

### 插桩三档

| 档位 | 是否允许 | 说明 |
|---|---|---|
| **L-Obs 观察** | 默认鼓励 | 打印参数/返回值；hook 配置解析、load/show/reward、加密前对象 |
| **L-Meas 本机测量** | 授权样机、为完成抓取所必需 | 须标 `env`；展示策略仍尽量以 clean 为准 |
| **生产绕过 / 刷量交付** | **禁止** | 不写上线过检、伪造用户、欺诈 SOP |

详见 [instrumentation-policy.md](./references/instrumentation-policy.md)、遇检测 [PB-07](./references/playbooks/PB-07-frida-maps-detection.md)。

### 使用范围

- 授权的竞品技术分析、变现结构研究、安全与测量研究  
- 记录防护/风控**检测点**与对分析/填充的影响  
- 不提供绕过第三方**生产**风控、伪造用户、刷量或广告欺诈的操作指导  

### 环境标签

| env | 用途 |
|---|---|
| `clean` | 正常用户侧基线（展示/发奖/主 DSP） |
| `root_frida` | 配置明文、细回调（非单独基线） |
| `proxy` | 报文形态（可能改变 fill，单独一列） |

---

## 安装与更新

```bash
# Codex
git clone https://github.com/weixiao33661/game-ad-sdk-intel.git ~/.codex/skills/game-ad-sdk-intel

# Claude Code
git clone https://github.com/weixiao33661/game-ad-sdk-intel.git ~/.claude/skills/game-ad-sdk-intel
```

已安装则：

```bash
cd ~/.codex/skills/game-ad-sdk-intel   # 或 ~/.claude/skills/...
git pull origin main
```

**Agent 加载的是 `SKILL.md`**；本 README 给人读。新开会话后再跑分析，避免旧上下文。

---

## 仓库结构

```text
game-ad-sdk-intel/
  SKILL.md                          # Agent 主指令
  README.md                         # 中文首页（本文件）
  README.en.md                      # English
  VERSION / CHANGELOG.md / LICENSE
  evals/evals.json                  # 回归题
  agents/openai.yaml
  scripts/
    extract_ad_indicators.py        # 指纹 triage
    validate_outputs.py             # 产物硬校验
    run_evals.py / llm_judge.py     # 回归 / 可选语义判分
    cluster_* / build_* / summarize_*  # 辅助，输出仅 triage
  references/
    tooling-mcp.md
    dynamic-validation.md
    instrumentation-policy.md
    competitor-analysis-capability-map.md
    report-template.md / output-templates.md
    phase-checklist.md / analysis-pipeline.md
    oem-*-depth.md / china-oem-ad-sdk-fingerprints.md
    playbooks/PB-01 … PB-07
    field-taxonomy.md / protocol-field-inference.md
    ...
```

---

## 证据档位

| 档位 | 条件 | 大致能钉住 |
|---|---|---|
| **L1 静态** | 仅 APK + jadx（+ 条件 IDA） | 字段名、代码策略分支、防护点；频控/服务端风控多 hypothesis |
| **L2 行为** | + clean 最小动态 | 何时弹、弹谁、发奖/点击、主 Activity |
| **L3 配置** | + 策略明文（Frida/抓包） | weight/bid/info[]、请求样例值 |

「精准策略配置」应对齐 **L2～L3**，并在报告 §0 声明。

---

## 常见误用

| 误用 | 应改为 |
|---|---|
| 只扫包名写「接了某某 SDK」 | PB-01 追 show 调用链 + 动态 Activity |
| 配置 6/6/5 写成「实际策略」 | PB-05 配置一行 + 运行胜出一行 |
| 有设备却纯静态下定论 | 强制 clean 最小动态 |
| 一有 Frida 检测就放弃分析 | PB-07：先 clean，再晚 attach / 窄 hook |
| 字典堆 `tt_appdownloader_*` | field-taxonomy；无 consumer 不进主表 |
| 小米字段套 OPPO 包 | 换对应 oem-*-depth |
| 把 judge 分数当分析完成 | 完成 = 规划走完 + validate PASS |

---

## 版本与贡献

| 版本线 | 要点 |
|---|---|
| 0.2.x | 多厂商、validate、judge、样例门禁 |
| 0.3.0 | 8 指标、jadx→IDA、强制 clean 动态 |
| 0.3.1 | Playbook PB-01～06 |
| 0.3.2 | PB-07 + 插桩政策 |
| 0.3.3 | 能力地图（汇总）+ 中文 README 体系 |

完整记录见 [`CHANGELOG.md`](./CHANGELOG.md)。

欢迎 Issue / PR：补厂商 depth、Playbook、校验规则或文档。提交前请确保 `scripts/validate_outputs.py` 在你的样例工作区可说明如何使用。

---

## 一句话

**APK → jadx →（必要时）IDA →（有设备）强制 clean 动态 → 八指标情报 + 可校验 JSON；卡住用 Playbook，而不是即兴发挥。**
