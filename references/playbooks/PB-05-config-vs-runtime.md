# PB-05 配置策略 vs 运行胜出

## 0. 何时启用

**触发症状：**

- 远程配置里多 DSP + 权重，真机却总是同一家
- `isBid=true` 但观感像串行固定源
- 历史抓包与本次运行不一致

**映射指标：** 2 展示策略、8 策略参数

**典型错误写法：**

- 只贴 config 权重当「实际策略」
- 只看一次展示就写死「只用 MiMo」
- 把 init 失败当成「配置没配这家」

## 1. 先排除（Fail-fast）

1. **配置是否来自本次进程**（缓存/comd5/旧文件）→ 先确认配置新鲜度。  
2. **该次是否真的 load 了配置中的 tag** → 对一下 tagId。  
3. **是否 no-fill 误判为「单 DSP 策略」** → 先 PB-04。  
4. **Activity 是否看错**（WebView/商店页）→ 用包名/类名确认 DSP。

## 2. 最小下一步

| 项 | 内容 |
|---|---|
| 工具 | clean 动态 + 已有配置提取（或 Frida 观察配置） |
| 做什么 | **同一逻辑位**连续触发 **≥5 次**展示，记录胜出 DSP（Activity/日志） |
| 否证标准 | 若 5 次中出现 ≥2 家 → 「永远一家」假说不成立 |

同步保留一行配置原文：`info[] name/parameter/weight`。

## 3. 升级阶梯

| 级 | 检查 |
|---|---|
| L1 | 配置 info[] / isBid / parallelism（静态或明文） |
| L2 | 运行胜出分布（5+ 次） |
| L3 | DSP init gate（未 init 被拦截） |
| L4 | 超时、缓存 tie-break、并行度 |
| L5 | 渠道填充差异（仅 MiMo 有量） |

## 4. 动态实验设计

```text
claim: 激励配置为腾讯/穿山甲/MiMo 6/6/5 竞价，运行以权重竞争而非单写死
dynamic_test: clean 同 tag 激励 5 次；可选打印 task 创建
expected_if_true: 胜出不完全单一，或配置+gate 解释得通
expected_if_false: 配置仅一家，或三家配置但两家永不 create task
if_fail_next: L3 init gate；L4 超时/缓存
```

## 5. 如何写进报告（强制两行）

专业写法必须拆开：

| 行 | 示例 |
|---|---|
| **配置策略** | 「getmedconfig：tencent w6, bytedance w6, mimo w5, isBid=true」（confirmed/hypothesis） |
| **运行胜出** | 「clean 5 次：MiMo 4 / GDT 1」（confirmed） |

| 状态 | 句式 |
|---|---|
| 配置 confirmed + 运行单一 | 「配置多渠；运行受 gate/填充/缓存影响偏 X」 |
| 仅配置 | hypothesis（无设备或未做 5 次） |

**禁止**合并成一句：「策略就是只用 X」。

## 6. 停止条件

- 两行都有证据或明确 unknown  
- 已排除「看错 tag / 旧缓存」  
- 原因可用 L3–L5 解释到「可能原因」级别即可，不必一次证死填充侧

## 7. 关联

- 小米：`oem-xiaomi-depth.md`、`xiaomi-mediation-notes.md`  
- PB-01、PB-04  
- 阶段：P5、P9  
- 指标 8 主战场
