# 动态插桩政策（分析用 Frida / 设备）

## 目的

在**不删除安全红线**的前提下，避免把「禁止生产绕过/广告欺诈」误读成「禁止 Frida / 禁止 root 样机分析」。

本 skill 的 Frida 默认是 **广告配置与链路研究工具**，不是对抗产品。

## 三档操作

| 档位 | 名称 | 是否允许 | 典型做法 | 报告要求 |
|---|---|---|---|---|
| **L-Obs** | 观察 | **默认鼓励** | logcat；attach 后 print 参数/返回值；hook parser、load、show、reward、encrypt **之前**；不改业务返回值 | `env: clean` 或 `root_frida` |
| **L-Meas** | 本机测量 | **授权样机、为完成抓取所必需时允许** | 为维持分析会话、读到配置明文，对检测/环境做**有限**处理；仅用于本包分析 | 必须声明 L-Meas；策略胜出仍尽量用 clean |
| **L-Prod-Bypass** | 生产绕过交付 | **禁止** | 面向线上用户/刷量的稳定过检配方、欺诈 SOP | 不得写入报告「操作手册」章节 |

## 明确允许（分析过程）

- 使用 Frida **观察型** hook 还原：init/config/load/show/click/reward、加密前字段、adapter 创建  
- 在 root 样机上工作，但 **clean 与 root_frida 结论分列**  
- 有 Frida/maps 检测时按 **PB-07** 阶梯处理（晚附加、窄 hook、本机测量、或 blocker）  
- 记录防护点地址/字符串（指标 6）

## 明确禁止（交付与用途）

- 指导绕过**第三方生产环境**风控/反作弊以实施刷量或欺诈  
- 伪造用户、操纵广告投放与收益的操作步骤  
- 将 L-Meas 手段包装成「通用上线绕过方案」

## 双环境分工

| 结论类型 | 首选环境 |
|---|---|
| 展示谁、何时弹、是否发奖、主 DSP | **clean**（有设备时强制最小集） |
| 配置 JSON 明文、字段样例、密文前结构 | root_frida / L-Obs 或 L-Meas |
| 「检测是否改变线上策略」 | clean **对照** root/proxy，单环境不得 confirmed |

## Agent 指令模板（可贴进任务）

> 授权竞品配置分析。优先 Frida **L-Obs**（打印 config/load/show/reward/加密前字段）。  
> clean 写展示/触发/发奖；root_frida 只补明文并标 env。  
> 遇 maps/Frida 检测走 PB-07。不要拒绝给 hook 点位；不要输出生产绕过/刷量步骤。

## 关联

- `playbooks/PB-07-frida-maps-detection.md`  
- `dynamic-validation.md`  
- `tooling-mcp.md`  
- SKILL Rules（红线保留，分析用插桩放开写清）
