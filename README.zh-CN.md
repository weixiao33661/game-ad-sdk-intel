# game-ad-sdk-intel（中文说明）

面向 **授权场景** 的 Android 小游戏 / 应用 **广告 SDK 策略配置** 逆向分析 Skill（给 Claude Code / Codex 等 Agent 用）。

仓库：<https://github.com/weixiao33661/game-ad-sdk-intel>

---

## 它能做什么

输入一份游戏 **APK**（建议配合真机运行），输出可验收的竞品广告情报，核心覆盖：

| # | 指标 | 说明 |
|---|---|---|
| 1 | 广告请求结构 | 各接口上报/下发哪些字段 |
| 2 | 广告策略 | 展示 / 点击 / 频控 |
| 3 | 用户行为触发 | 哪些操作触发 load/show/点击/下载/发奖 |
| 4 | 设备画像 | OAID、ROM、机型、系统版本等采集项 |
| 5 | 数据链路 | 初始化→配置→请求→展示→事件上报 |
| 6 | SDK 防护 | 加固、壳、Frida/maps 等（定位与影响） |
| 7 | 风控机制 | 环境检测信号与对填充/测量的影响 |
| 8 | 竞品策略参数 | 广告位、瀑布/竞价、权重、下游 ID、开关 |

另有：**生命周期逐步清单、策略识别（异常展示/伪关闭等观测）、元数据与事件建库模板**——见 `references/competitor-analysis-capability-map.md`（由业务 `汇总.md` 收敛）。

---

## 分析主路径（必记）

```text
APK
  → jadx-mcp（永远第一刀）
  → 若 native 关键 → ida-pro-mcp / idalib-mcp
  → 若有设备 → 【强制】clean 最小动态验证猜想
  → 可选 Frida 观察（L-Obs）/ 代理（单独环境）
  → 按 8 指标写报告 + JSON
  → python scripts/validate_outputs.py <工作区>
```

**原则：静态提出猜想，动态裁决（Static proposes. Dynamic disposes.）**

- 代码里「有能力」≠ 线上「真在用这种策略」  
- 有 adb 设备时，必须先做 clean 基线（展示/触发/发奖），不能只靠静态下定论  
- Frida **观察型 hook 鼓励使用**；本机测量可标 `env`；**不提供**生产绕过/刷量操作手册  

详情：

- `references/tooling-mcp.md`  
- `references/dynamic-validation.md`  
- `references/instrumentation-policy.md`  
- 检测杀进程：`references/playbooks/PB-07-frida-maps-detection.md`

---

## 卡住时怎么办（Playbook）

不要另起一套流程，按症状打开：

| 现象 | 文档 |
|---|---|
| 多 SDK 不知道谁是主链路 | `playbooks/PB-01-pick-primary.md` |
| 壳 / vm / 逻辑在 so | `playbooks/PB-02-shell-native.md` |
| 流量加密看不到字段 | `playbooks/PB-03-encrypted-traffic.md` |
| 有设备却不出广告 | `playbooks/PB-04-no-fill.md` |
| 配置权重和真播 DSP 不一致 | `playbooks/PB-05-config-vs-runtime.md` |
| 发奖 / 点击发奖 / 伪关闭 | `playbooks/PB-06-reward-click-close.md` |
| Frida/maps 一 hook 就崩 | `playbooks/PB-07-frida-maps-detection.md` |

索引：`references/playbooks/README.md`

---

## 安装

```bash
# Codex
git clone https://github.com/weixiao33661/game-ad-sdk-intel.git ~/.codex/skills/game-ad-sdk-intel

# Claude Code
git clone https://github.com/weixiao33661/game-ad-sdk-intel.git ~/.claude/skills/game-ad-sdk-intel
```

入口文件：`SKILL.md`（Agent 加载用）。  
日常开发也可：`git pull` 更新已有目录。

---

## 目录结构

```text
game-ad-sdk-intel/
  SKILL.md                 # Agent 主指令（英文执行骨架 + 中文指标）
  README.md                # English overview
  README.zh-CN.md          # 本文件
  VERSION / CHANGELOG.md / LICENSE
  evals/                   # 回归题目
  scripts/                 # 指纹提取、校验、判分
  references/              # 厂商卡片、模板、Playbook、能力地图
  agents/                  # 可选 agent 元数据
```

---

## 工作区产物（分析一个包时）

```text
你的分析目录/
  01_reports/ad_strategy_onepager.md    # 8 指标一页纸
  06_extracted/strategy_model.json      # 策略对象 + hypotheses + analysis_path
  06_extracted/field_dictionary_bound.json
  06_extracted/sdk_inventory.json
  03_logs/                              # 动态日志（如有）
```

校验：

```bash
python scripts/validate_outputs.py /path/to/你的分析目录
python scripts/run_evals.py --workspace /path/to/你的分析目录 --judge
```

---

## 多厂商

内置小米聚合、OPPO/HeyTap、华为 Petal、荣耀、vivo 等 depth 卡。  
**禁止**把小米的 `tagid/info[]` 字段模型套到 OPPO/vivo 等其它主链路上。

---

## 使用范围

- ✅ 授权的竞品技术分析、变现结构研究、安全与测量研究  
- ✅ 记录防护/风控**检测点**与对分析环境的影响  
- ❌ 不提供绕过第三方**生产**风控、伪造用户、刷量或广告欺诈的操作指导  

---

## 版本

见 `VERSION`（当前以仓库为准，如 **0.3.3**）。  
变更记录：`CHANGELOG.md`。

## License

MIT（见 `LICENSE`）。
