# Skill 成熟度评分表（Checklist）

## 这张表能带来什么效果

不是装饰性自评，而是把“感觉还行”变成可执行的质量闸门。

| 效果 | 具体收益 |
|---|---|
| **验收标准** | 每次改 skill / 分析一包，用同一套分项打分，避免口头“更专业了” |
| **暴露短板** | 哪一项 < 阈值就知道补文档、补脚本、补 eval，还是补动态样本 |
| **阻止假完成** | agent 若只吐噪声字段表、未选 primary、无转化节，对应项直接 0 分 |
| **版本对比** | v1→v2 可以写“指纹 2→4，字典 1→3”，方便回归 |
| **分工清晰** | 文档分 / 自动化分 / 样本深度分 分开，避免“手册很全但跑不稳”被平均掉 |
| **发布门槛** | 建议：主 skill 总均分 ≥ 3.5 且无单项 0，才称为“可日常使用”；≥ 4.0 且 eval 通过才称“可回归生产” |

### 计分规则

- 每项 **0–4 分**（整数）
- **维度分** = 该维各项平均
- **总分** = 七个维度平均（可加权，默认等权）
- 标注 **当前分 / 目标分 / 证据**（路径或一次 eval 结果）

| 分 | 含义 |
|---:|---|
| 0 | 缺失或会误导 |
| 1 | 有草稿，不可靠 |
| 2 | 能用，缺口明显 |
| 3 | 专业可用，偶发要人工补 |
| 4 | 可回归/可强制验收 |

### 建议门槛

| 用途 | 门槛 |
|---|---|
| 内部试用 | 总分 ≥ 2.5，指纹与合规 ≥ 3 |
| 日常竞品分析 | 总分 ≥ 3.5，无 0 分项，primary 路由冒烟全过 |
| 宣称生产级 | 总分 ≥ 4.0，golden eval pass，结构化产物 schema 校验 pass |

---

## 维度与 checklist

### D1 触发与边界 (Trigger & Safety)

| ID | 检查项 | 0–4 | 当前 | 目标 | 证据/缺口 |
|---|---|---:|---:|---:|---|
| D1.1 | description 能触发广告/mediation/OEM 任务且不总结错 workflow |  | 3 | 4 | SKILL.md frontmatter |
| D1.2 | 授权分析边界、禁止绕过线上风控写清楚 |  | 4 | 4 | Rules 节 |
| D1.3 | 转化技巧记为竞品观察，与合规风险分离 |  | 3 | 4 | conversion 节 |

### D2 多厂商路由 (Multi-OEM Routing)

| ID | 检查项 | 0–4 | 当前 | 目标 | 证据/缺口 |
|---|---|---:|---:|---:|---|
| D2.1 | 五家架构差异可查（聚合 vs 直连） |  | 4 | 4 | oem-architecture-matrix.md |
| D2.2 | 指纹 high/medium/low + 假阳性 denylist |  | 4 | 4 | fingerprints + script |
| D2.3 | 脚本 primary 不在弱 token 上误判 |  | 4 | 4 | 五家 demo + dcxns 冒烟 |
| D2.4 | 下游 DSP 晋级 capability→active |  | 3 | 4 | matrix；报告执行仍靠 agent |
| D2.5 | 禁止跨厂商复制字段模型 |  | 4 | 4 | 多处硬规则 |

### D3 分析流程门禁 (Pipeline Gates)

| ID | 检查项 | 0–4 | 当前 | 目标 | 证据/缺口 |
|---|---|---:|---:|---:|---|
| D3.1 | 分阶段入口/出口产物定义完整 |  | 4 | 4 | analysis-pipeline / SKILL P0–P10 |
| D3.2 | 配置面（local/BFF/mediation/cache）必查 |  | 3 | 4 | 有清单；无自动检查 |
| D3.3 | 生命周期矩阵模板存在 |  | 3 | 4 | report-template |
| D3.4 | 转化 UX 阶段强制存在 |  | 3 | 4 | 文档强制；缺 schema fail |
| D3.5 | clean/root/proxy 动态矩阵 |  | 3 | 4 | dynamic-validation.md |

### D4 字段与证据纪律 (Fields & Evidence)

| ID | 检查项 | 0–4 | 当前 | 目标 | 证据/缺口 |
|---|---|---:|---:|---:|---|
| D4.1 | bound = parser+consumer+effect |  | 3 | 4 | protocol-field-inference；执行靠人 |
| D4.2 | 噪声 denylist（UI/布局/引擎键） |  | 3 | 4 | 文档有；旧大表已删除 |
| D4.3 | 证据分级 / env 标签 |  | 3 | 4 | 模板有列 |
| D4.4 | 主字典禁止 unbound 充数 |  | 2 | 4 | 规则有；无 CI 校验器 |
| D4.5 | 脚本输出标明 triage-only |  | 4 | 4 | SKILL Notes |

### D5 厂商深度对称 (OEM Depth Parity)

| ID | 检查项 | 0–4 | 当前 | 目标 | 证据/缺口 |
|---|---|---:|---:|---:|---|
| D5.1 | 五家 profile 同构章节 |  | 4 | 4 | oem-*-depth 对齐 |
| D5.2 | 每家：指纹/ID/生命周期/格式矩阵/绑定字段/动态探针/勿做清单 |  | 4 | 4 | depth cards |
| D5.3 | Demo 路径与 applicationId 可定位 |  | 4 | 4 | 各 depth 卡 |
| D5.4 | 竞品 APK 额外壳层注意（Unity/假关闭）不独厚一家 |  | 3 | 4 | matrix + strategy-reverse |
| D5.5 | 动态样本深度（vivo 有较多 frida；他厂偏静态） |  | 2 | 4 | 非 vivo 动态仍薄 |

### D6 自动化与回归 (Automation & Eval)

| ID | 检查项 | 0–4 | 当前 | 目标 | 证据/缺口 |
|---|---|---:|---:|---:|---|
| D6.1 | indicators 脚本可用 |  | 4 | 4 | extract_ad_indicators.py |
| D6.2 | fields/strategy 辅助脚本可用 |  | 3 | 4 | 另 3 脚本；噪声仍可能 |
| D6.3 | golden case 文档存在 |  | 4 | 4 | golden-case-dcxns.md + workspace sample outputs |
| D6.4 | eval 题目可跑且有 pass 标准 |  | 3 | 4 | run_evals.py 结构/golden/workspace；仍无 LLM 判分 |
| D6.5 | 结构化产物 schema 校验 |  | 4 | 4 | validate_outputs.py PASS on dcxns |

### D7 产出与协作 (Outputs & Ops)

| ID | 检查项 | 0–4 | 当前 | 目标 | 证据/缺口 |
|---|---|---:|---:|---:|---|
| D7.1 | 中文报告模板完整 |  | 4 | 4 | report-template.md |
| D7.2 | 一页纸业务摘要可选 |  | 3 | 4 | template 可选节 |
| D7.3 | 主 skill 与 companion 关系无歧义 |  | 4 | 4 | relationship + README |
| D7.4 | 旧噪声产物不在默认路径误导 |  | 4 | 4 | 已删除/归档 validation 大表 |
| D7.5 | Demo 报告与 skill 交叉链接 |  | 3 | 4 | depth 卡指向 demo/reports |

---

## 当前基线分（2026-07-20，升级后自评）

| 维度 | 均分 | 一句话 |
|---|---:|---|
| D1 触发与边界 | **3.3** | 边界清楚，触发可再压测 |
| D2 多厂商路由 | **3.8** | 最强项；脚本冒烟已过 |
| D3 流程门禁 | **3.2** | 手册级门禁，缺硬校验 |
| D4 字段证据 | **3.0** | 规则到位，执行未自动化 |
| D5 厂商深度 | **3.4** | 文档对称已拉齐；动态样本不对称 |
| D6 自动化回归 | **3.6** | validator + run_evals + dcxns golden 已通；缺 LLM eval |
| D7 产出协作 | **3.6** | 模板与去噪路径清晰 |
| **总分** | **≈ 3.5** | **达到日常可用门槛；生产级仍差 LLM eval / 非小米 golden** |

### 如何使用

1. 改 skill 后重打本表，只改有证据的格子。  
2. 每次竞品分析结束，用 D3/D4/D7 相关项给**当次报告**打副分（报告质量 ≠ skill 质量，但可反馈 skill）。  
3. 优先补 **得分最低且阻塞发布** 的项：当前是 D6.4/D6.5、D4.4、D5.5。

### 不该用这张表做什么

- 不拿总分对外吹“已完全自动化还原高转化策略”  
- 不把 Demo 静态深度 4 分当成线上 waterfall 已还原  
- 不把单一 dcxns 高分泛化成五家线上同等深度  
