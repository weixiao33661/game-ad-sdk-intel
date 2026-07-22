# PB-04 No-fill / 有设备但不出广告

## 0. 何时启用

**触发症状：**

- 已装包、能进游戏，激励/插屏/Banner 不展示
- load 一直失败或无回调
- 静态看有完整 SDK，动态「什么都没有」

**映射指标：** 2 策略、3 触发、7 风控（环境）、8 参数

**典型错误写法：**

- 直接写「被风控」无对照
- 未区分「没调用」vs「调用失败」
- 无 fill 却编造完整线上 waterfall 定论

## 1. 先排除（Fail-fast）— 断点拆解

按顺序定位断在哪一层：

```text
① 游戏是否调用 show/load？
② SDK 是否 init 成功？
③ 隐私/同意是否挡住？
④ 本地 slot/tag 是否为空或写错？
⑤ load 是否回调失败（错误码）？
⑥ load 成功但 show 失败？
⑦ 仅 hook/root/代理环境失败？
```

任一层用 logcat / 简单观察即可，**先不要上复杂 hook**。

## 2. 最小下一步

| 项 | 内容 |
|---|---|
| 工具 | clean 设备 + logcat（或 SDK debug） |
| 做什么 | 触发一次激励，确认是否出现 load/show/error 日志或回调 |
| 否证标准 | 若完全无 load → 是触发/桥问题（回 P4/PB-01），不是「策略权重」问题 |

同时记录：`device_available=true`，若整段不可测 → 填 `dynamic_blocker`。

## 3. 升级阶梯

| 级 | 动作 |
|---|---|
| L1 | 触发链：按钮/通关是否调到 Java show |
| L2 | init/隐私/权限/测试位/包名渠道 |
| L3 | error code 语义（关位 isClosed、init gate、网络） |
| L4 | clean vs root_frida / proxy 对照（只改一个变量） |
| L5 | Frida 看配置是否空 info[] / isClosed |

## 4. 动态实验设计

```text
claim: 激励位被服务端 isClosed 或空下游
dynamic_test: clean 触发 load；抓 error 或配置解析结果
expected_if_true: 明确 closed/空列表/特定错误码
expected_if_false: load 成功且 show 成功
if_fail_next: 查触发；查 init；再环境对照
```

**强制 clean 最小集**中的激励 3～5 次：即使 no-fill，也要留下「尝试记录」，结果可为 inconclusive。

## 5. 如何写进报告

| 状态 | 句式 |
|---|---|
| confirmed | 「断点在 init 失败 / 错误码 X / 未调用 show（证据…）」 |
| refuted | 「并非风控：clean 下可 fill，仅 root 环境失败」 |
| inconclusive | 「多次无 fill，断点未定位，blocker=…」 |

**禁止：** 无对照时写「平台判定作弊所以无广告」定论。

指标 8：无成功配置/展示时，策略参数保持 hypothesis，并引用本 PB 阶梯已做到哪一级。

## 6. 停止条件

- 断点层级已定位，或  
- `dynamic_blocker` 已写清（无网/闪退/账号限制）且最小尝试已做  
- 不接受「没广告所以没法分析」——至少要完成断点拆解表

## 7. 关联

- `dynamic-validation.md` 最小集  
- PB-01（根本没走到主 SDK）  
- PB-05（有 fill 后再比配置）  
- PB-08 预留（风控对照，二期）  
- 阶段：P9
