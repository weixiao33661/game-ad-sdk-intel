# PB-06 发奖 / 点击 / 关闭 / 伪关闭

## 0. 何时启用

**触发症状：**

- 不清楚何时 `showAward` / 发奖成功
- 怀疑「点击也发奖」
- 关闭按钮异常、像下载、文案是「关闭」却跳商店
- 早退是否发奖不一致

**映射指标：** 2.2 点击策略、2.1 展示收尾、3 用户行为触发（转化相关）

**典型错误写法：**

- 只写「看完广告有奖励」不测点击/早关
- 把伪关闭写成「SDK 正常关闭」
- 无静态+动态交叉就定论

## 1. 先排除（Fail-fast）

1. **发奖是否游戏自己点按钮就发**（与广告无关）→ 先分清游戏逻辑 vs 广告回调。  
2. **是否仅测试包/调试开关直接发奖** → 标测试行为。  
3. **关闭回调是否被当成发奖** → 看 `onClose` 是否调 success。  
4. **是否多次 listener 重复发奖** → 日志次数。

## 2. 最小下一步

分两条并行（都短）：

**A. 静态（jadx-mcp）**

- 追 `onReward` / `onAdClick` / `onAdClose` / `onRewardClicked` → 游戏 `showAward`/`RewardStatus`
- 搜文案改写：`关闭`、`setText`、DownloadButton、skip 隐藏

**B. 动态（有设备则强制最小集内完成）**

三次对照（同一激励位）：

| 实验 | 操作 | 记录 |
|---|---|---|
| E1 | 完整观看至发奖回调 | 是否成功发奖 |
| E2 | 广告内点击主 CTA/素材 | 是否发奖 + 是否跳转 |
| E3 | 尽早点关闭/跳过 | 是否发奖 |

## 3. 升级阶梯

| 级 | 动作 |
|---|---|
| L1 | Java 回调 → 发奖函数参数（0/1） |
| L2 | 三矩阵 E1/E2/E3 动态结果 |
| L3 | UI 树：skip 隐藏？关闭键类名是否 Download* |
| L4 | startActivity：market/hap/deeplink/H5 |
| L5 | 壳内改写（进 PB-02） |

## 4. 动态实验设计

```text
claim: 点击广告与完整观看同样发奖成功
dynamic_test: E1 vs E2；看游戏发奖日志/资产变化
expected_if_true: E2 也 success
expected_if_false: 仅 E1 success
if_fail_next: 静态对 onClick 是否 set RewardStatus

claim: 「关闭」实为下载/商店导流（伪关闭）
dynamic_test: E3 点关闭，看是否离开游戏进商店/下载
expected_if_true: market/hap/下载器；真 skip 不可用
expected_if_false: 正常关闭回游戏且无下载链
if_fail_next: L3 UI 类名；L4 Intent
```

## 5. 如何写进报告（强制分条）

指标 2.2 / 3 建议固定三条，状态可不同：

| 条 | 内容 |
|---|---|
| 发奖条件 | 完整观看 / 服务端 verify / 其它 |
| 点击与发奖 | 是否 click-also-reward |
| 关闭语义 | 正常关闭 vs 伪关闭/强导流；落地类型 |

| 状态 | 句式 |
|---|---|
| confirmed | 「E2 动态 + `onRewardClicked→showAward(0)` 静态一致」 |
| refuted | 「代码无 click 发奖；动态 E2 不发奖」 |
| hypothesis | 「静态见 Download 改文案，未动态点证」——**有设备应尽量 L2** |

合规：伪关闭/误导点击标 **竞品观察 + 合规风险**，不写「如何用于上线」。

## 6. 停止条件

- E1/E2/E3 至少做完（有设备时），或 `dynamic_blocker`  
- 静态回调链已画清  
- 伪关闭：静态或动态至少一方 confirmed，另一方可 hypothesis  

## 7. 关联

- `ad-strategy-reverse.md` conversion  
- PB-02（改写在壳）  
- PB-04（根本无广告时先别做本 PB）  
- 阶段：P4、P7、P9  
- 指标 2、3 主战场
