# PB-02 壳与 Native（Java 空壳 / so）

## 0. 何时启用

**触发症状：**

- `show*` / `init` 进入 `vm_*`、加固壳、单一 native 跳板
- `System.loadLibrary` 后 Java 无业务
- 频控/设备指纹/签名怀疑在 so
- jadx 看不到关键字符串，但 so 名可疑

**映射指标：** 2 策略、5 链路、6 防护（常影响 1 请求）

**典型错误写法：**

- 一上来对所有 so 开 IDA
- 宣称「完全无法分析」而不做边界观测
- 无地址/JNI 映射就写防护细节

## 1. 先排除（Fail-fast）

1. **so 仅为解码/加载器、广告在另一可见 SDK** → 主分析仍跟可见 SDK，so 降级。  
2. **Java 层已有完整 mediation/OEM 源码**（如小米聚合源码可见）→ 先吃透 Java，壳只挡游戏侧编排。  
3. **仅 mono/unity 游戏逻辑** → 广告若在 Java SDK，先 Java；关卡频控再标 Unity 探针。  
4. **无广告相关 JNI/字符串线索** → 可暂缓深挖，记 hypothesis。

## 2. 最小下一步

| 项 | 内容 |
|---|---|
| 工具 | **jadx-mcp**（边界）→ 必要时 **ida-pro-mcp / idalib-mcp** |
| 做什么 | ① 表：`so名 | 疑似角色(壳/广告/检测/加密)` ② 定位「进壳前参数、出壳后回调」 |
| 否证标准 | 若回调已在 Java mediation 层完整可见，则不必先脱壳 |

**优先观察型动态：** hook/日志打印壳边界，**不改返回值**。

## 3. 升级阶梯

| 级 | 动作 |
|---|---|
| L1 | jadx：loadLibrary、jni、vm 入口、哪些 API 进壳 |
| L2 | 动态：参数/回调边界（tagId、listener） |
| L3 | IDA：导出/JNI 名、字符串（config/risk/slot）、交叉引用 |
| L4 | IDA：加密/检测函数逻辑摘要（地址+行为），服务指标 1/6/7 |

**禁止跳级：** 未做 L1/L2 边界就全 so 硬反。

## 4. 动态实验设计

```text
claim: 激励展示决策在壳内 / 或仅在 mediation Java
dynamic_test: clean 触发激励；看进壳前是否已有 tagId；show 前后 Java 回调是否完整
expected_if_true: 关键决策参数只在进壳后出现
expected_if_false: AdRepository/adapter 在 Java 全可见
if_fail_next: IDA 跟 so 内字符串与 JNI；频控仍无 → 标 Unity/壳 unknown
```

## 5. 如何写进报告

| 状态 | 句式 |
|---|---|
| confirmed | 「`libX.so!func` 负责 …；Java 仅跳板」 |
| refuted | 「存在壳，但广告策略在 `com.xxx` Java 层完整可还原」 |
| hypothesis | 「壳内可能含频控，未 IDA/动态证实」 |

防护章写**检测点与对分析影响**，不写生产环境绕过步骤。

## 6. 停止条件

- 广告主路径（load/show/上报）已在 Java 或 so 一侧还原清楚  
- 壳内关卡频控可 unknown，但必须写探针（IL2CPP / 长测 / 继续 IDA）  
- `analysis_path.ida_sos` 记录实际打开过的 so

## 7. 关联

- `tooling-mcp.md` native 门闸  
- PB-03（加密在 so）  
- PB-06（发奖回调若在壳边界）  
- 阶段：P2/P8/P9
