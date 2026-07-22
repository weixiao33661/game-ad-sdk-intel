# PB-01 主链路裁决（谁是 primary）

## 0. 何时启用

**触发症状：**

- 包内同时出现多个广告 SDK（MiMo / GDT / Pangle / MAX / OEM…）
- 不知道报告里「主聚合 / 主 SDK」写谁
- 渠道包（如 `.mi`）里还有 AppLovin MAX / Unity 插件

**映射指标：** 5 数据链路、8 策略参数（以及 SDK 库存）

**典型错误写法：**

- 按 AAR 数量或字符串命中次数选 primary
- 把 MAX Unity 插件直接写成主聚合
- 多个 primary 并列且不说明冲突

## 1. 先排除（Fail-fast）

1. **仅资源/AAR/布局命中** → 标 `residual` 或 `noise_hit`，不能当 primary。  
2. **无 init 调用证据**（代码路径到不了 `init`）→ 非 primary。  
3. **无 load/show 路径** → 最多 capability，不是 active 主链路。  
4. **弱指纹**（`SplashView`、裸 `open_ad_`、裸 `com.heytap`）→ 见指纹 denylist，禁止单独定 OEM primary。  
5. **分析类 SDK**（OneTrack 等）→ `analytics_attribution`，不是 demand/primary。

## 2. 最小下一步

| 项 | 内容 |
|---|---|
| 工具 | **jadx-mcp** |
| 做什么 | 从游戏侧 `showRewarded` / `showAd` / `post_show_video` **向下追调用**（建议 ≥5 层），直到 OEM/mediation API 或壳入口 |
| 否证标准 | 若最终只进 A 而从未进 B 的 init/show，则 B 不能写 primary |

同时做一张表：`SDK | init 是否调用 | show 是否调用 | 配置是否引用 | 动态 Activity`。

## 3. 升级阶梯

| 级 | 动作 | 何时升级 |
|---|---|---|
| L1 | jadx 调用图 + adapter 注册表 | 默认 |
| L2 | 读远程配置/解析类：谁出现在 waterfall/info[] | 静态仍多主 |
| L3 | clean 动态：激励/插屏前台 Activity 包名 | 有设备（强制最小动态的一部分） |
| L4 | Frida：loadAds/adapter 实际创建 | L3 仍模糊 |

**禁止：** 只凭 `libs/` 目录写「瀑布合作方」。

## 4. 动态实验设计

```text
claim: 主链路是 <X> 而非 <Y>
dynamic_test: clean 下触发激励 3～5 次，记录每次前台 Activity / 进程日志中的 SDK tag
expected_if_true: Activity/日志稳定落在 X 体系
expected_if_false: 稳定落在 Y，或两者交替且无单一协调层
if_fail_next: 回 L2 查配置；查是否 bridge（MAX→GameManager→X）
```

## 5. 如何写进报告

| 状态 | 句式 |
|---|---|
| confirmed | 「Primary = X（init+show+动态/配置一致）」 |
| refuted | 「包内有 Y SDK，但 init/show 未走到，标 residual」 |
| hypothesis | 「静态疑似 X，未动态验证」——**有设备时不应停在此步** |

**硬规则：** `sdk_inventory` 只允许一个 `primary_mediation` 或 `primary_direct_sdk`；多主必须写 conflict 说明。

## 6. 停止条件

- 已唯一 primary + 证据链（调用或动态其一足够强，两者更佳）
- 或明确 multi-primary conflict + 各 role 证据  
- 禁止用「都集成了」结束

## 7. 关联

- 指纹：`china-oem-ad-sdk-fingerprints.md`、`oem-architecture-matrix.md`
- 阶段：P2  
- 后续：定 primary 后读对应 `oem-*-depth.md`；配置≠运行 → PB-05
