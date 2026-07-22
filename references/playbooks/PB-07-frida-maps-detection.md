# PB-07 壳内 Frida / maps 特征检测（研究向）

## 0. 定位与边界

**用途：** 授权样机上完成广告配置/回调分析时，进程被壳的 Frida、`/proc/self/maps` 等完整性检测打断。  
**目标：** 尽量拿到 **配置明文、load/show/reward 链路、字段样例**，并正确标注 `env`。  
**不是目标：** 产出可上线、可扩散的「稳定过生产风控」配方或欺诈用绕过手册。

三档操作（与 instrumentation 政策一致）：

| 档 | 含义 | 本 PB |
|---|---|---|
| **L-Obs** | 纯观察 hook、logcat、晚附加 | 默认优先 |
| **L-Meas** | 授权样机上为让分析进程活着完成抓取的有限手段 | 仅本机、须写报告 |
| **L-Bypass 生产交付** | 面向线上刷量/伪装的稳定对抗包 | **禁止作为 skill 交付** |

---

## 1. 何时启用

**触发症状：**

- 一 attach/spawn Frida 就闪退、冻住、空进程
- 仅开 frida-server 未 hook 也退（maps 扫 frida/gadget/linjector 等）
- root/Magisk 后 fill 异常，clean 正常
- so 字符串或逻辑出现 `/proc/self/maps`、`frida`、`gum-js`、`LIBFRIDA`、线程名检测等

**映射指标：** 6 防护、7 风控（环境）、1/5/8（常被打断导致拿不到）

**典型错误：**

- 一检测就放弃全部动态，连 clean 最小集都不做
- 未区分「检测杀进程」vs「业务 no-fill」
- 把 root 会话策略当成 clean 用户策略
- 报告写成绕过教程而非「检测点 + 对测量影响」

---

## 2. 先排除（Fail-fast）

按序否定廉价假设：

1. **是否其实是业务 no-fill？**  
   不挂 Frida，**clean** 走 PB-04 最小操作，是否能出广告？  
   - clean 也不出 → 先 PB-04，不是本 PB 主战场。  
   - clean 出、仅 hook 环境不出/崩 → 进入本 PB。

2. **是否 spawn 时机问题？**  
   冷启动壳在 `Application.onCreate` 就扫 maps；spawn 过早必撞。  
   先试：**手动启动到大厅再 attach**（L-Obs）。

3. **是否 hook 面太大？**  
   全量 `Java.perform` + 大量类名扫可能拖死或二次触发。  
   先只 hook **1～2 个业务点**（配置 parser / loadAds）。

4. **是否多进程？**  
   广告在 `:ads` / 独立进程；hook 错进程会像「检测」或「没数据」。  
   `ps` / `frida-ps` 确认目标进程。

5. **是否非 maps 的其它检测？**  
   调试器、tracerpid、端口 27042、已知 su 路径、模拟器指纹。  
   分开记，避免全算成 maps。

---

## 3. 检测常见形态（便于 jadx/IDA 定位）

只作识别清单，不写利用细节：

| 类型 | 常见行为 | 分析含义 |
|---|---|---|
| maps 扫描 | 读 `/proc/self/maps`（或 task maps），匹配 frida/gadget/linjector/substrate 等 | hook 后易崩或自杀 |
| 线程/模块名 | 枚举线程名、已加载 so 名 | 同上 |
| 端口/管道 | 探测 frida-server 默认端口或 unix socket | 未 hook 也可能异常 |
| 时序 | 启动后延迟再检、或周期检 | 晚 attach 仍可能中招 |
| 与广告联动 | 检到后 `exit`、拒绝 init、空配置、只降级广告 | 对应 PB-04 / 指标 7 |

**静态定位（jadx → 门闸 IDA）：**

1. jadx 搜 `maps`、`frida`、`TracerPid`、`27042`、`inotify`（若有）  
2. 跟 `loadLibrary` 的壳 so  
3. IDA：字符串 xref → 检测函数 → 谁在 init/定时器调用  
4. 记录：`so!地址或符号` + 「失败时 exit / 返回错误 / 清配置」

---

## 4. 解题阶梯（研究向，禁止跳级）

### L0 — 先保住 clean 基线（有设备则强制）

与是否 Frida **无关**，先完成：

- 冷启动 / Banner 窗口 / 激励 / 发奖矩阵（见 `dynamic-validation.md`）  
- 结论标 `env: clean`  

**没有 L0，不要用 root 会话写「线上展示策略」。**

### L1 — 无 Frida 的观测（能省则省）

- logcat 过滤 SDK/mediation tag  
- `dumpsys activity` 看广告 Activity  
- 若 SDK 有 debug 开关且授权包可用 → 打开  

能完成指标 2/3/部分 8 就先写 confirmed（clean）。

### L2 — 晚附加 + 窄 hook（L-Obs 默认）

**思路：** 避开启动瞬间的 maps 大扫，或减少触发面。

1. clean 手动进到**已过开屏/登录的大厅**  
2. `frida -U -n <进程名>` 或 pid **attach**（非 spawn）  
3. 只 hook **广告配置解析 / load / reward 回调** 等少量方法  
4. 立刻触发一次激励，抓完就卸  

**否证：** 若晚 attach 仍秒退 → 存在周期检测或端口检测，升 L3。

**报告：** `env: root_frida`，数据用于字段/配置结构，展示策略仍引用 L0。

### L3 — 边界观测（Java 侧加密前 / 回调后）

**思路：** 少碰最敏感的 libc 读 maps，改抓业务语义。

优先点位（按包裁剪）：

- 配置：`initconfig`/`getmedconfig` 的 **parse(String/byte[])**  
- 聚合：`loadAds`、`info[]` 任务创建  
- 发奖：`onReward` / `onRewardClicked` / 游戏 `showAward`  
- 加密：**encrypt 前的 Map/JSON**（PB-03）

**原则：** 能在 Java 业务层拿到明文，就不必先补丁 so。

### L4 — 本机测量（L-Meas，授权样机 only）

当 L2/L3 均因检测无法维持进程、且配置明文对指标 1/8 关键时：

**允许的表述与做法（交付边界）：**

- 在**自有/授权分析机**上，为完成本次抓取采用有限手段降低检测对**分析会话**的干扰（例如：已知开源研究实践中的 maps 路径干扰、替换检测结果仅用于本机、使用社区常用的反检测 frida 变体等）。  
- 报告必须写明：  
  - 使用了 L-Meas  
  - `env: root_frida`（或更具体）  
  - **目的 = 提取配置/链路，非用户基线**  
  - 若与 clean 展示结果冲突，**以 clean 为准写策略胜出**

**禁止写入 skill 交付的：**

- 逐步、可复制、面向生产包的「通用过检脚本合集」当作产品功能  
- 教人在真实用户设备上隐藏刷量  

具体补丁字节级步骤因样本而异，应在**个案分析笔记**中记录，而不是做成通用「过生产风控」章节。

### L5 — 静态补全 + blocker

若动态始终被杀：

1. IDA/jadx 固定检测点与后果（exit / 拒 init / 空配置）  
2. 指标 1：字段**名**仍从 builder 出；样例值 unknown  
3. `dynamic_blocker: frida_maps_detection`  
4. 指标 6 confirmed（有检测）；指标 7 对「是否改策略」保持 hypothesis，除非 clean 对照能说话  

---

## 5. 推荐决策树（一张图）

```text
clean 能出广告？
  ├─ 否 → PB-04（先别怪 Frida）
  └─ 是 → 完成强制最小动态（L0）
           还需要配置明文/细回调？
           ├─ 否 → 结束，不必硬刚检测
           └─ 是 → 晚 attach + 窄 hook（L2）
                    仍死？
                    ├─ 业务层 parser hook（L3）
                    └─ 仍死 → L-Meas 本机测量（L4）或 IDA+blocker（L5）
```

---

## 6. 报告怎么写（专业且不越界）

### 指标 6 防护

```text
confirmed: libX 在启动/周期路径读取 maps 并匹配 Frida 相关特征；
失败行为: 进程退出 / 拒绝广告 init（选实据）。
对分析影响: spawn 即崩；晚 attach 可维持 N 分钟 / 仍被周期检杀。
证据: so!addr / jadx 字符串 xref / 复现步骤（attach 时机）。
```

### 指标 1 / 8

```text
配置字段结构: 来自 root_frida 下 parser hook（env 已标）。
线上展示胜出: 以 clean 最小集为准。
```

### 指标 7

```text
hypothesis: 检测可能导致分析环境 fill 下降；
未做 clean 对照前，不写「生产对所有 root 用户关广告」。
```

---

## 7. 与双环境分工（再强调）

| 问题 | 环境 |
|---|---|
| 何时弹、弹谁、是否发奖 | **clean**（强制） |
| tag/weight/info[] 明文、加密前字段 | root_frida / L-Meas 可 |
| 检测是否改变策略 | 必须 clean 对照，单环境不准 confirmed |

---

## 8. 停止条件

可以停且仍专业：

- L0 clean 最小集完成，且配置侧已用 L2–L4 或静态字段名补齐到可交付  
- 或 `dynamic_blocker` 写清 + 检测点 IDA/jadx 定位 + 指标 6 写实  

不要停在：

- 「有 Frida 检测所以整个包无法分析」

---

## 9. 关联

- `tooling-mcp.md`、`dynamic-validation.md`  
- 建议同时读 instrumentation 政策（L-Obs / L-Meas）  
- PB-02 壳总体、PB-03 密文、PB-04 no-fill  
- 阶段：P8、P9  

---

## 10. 一句话

**先 clean 保策略真相 → 晚附加窄 hook 抢业务明文 → 仍不行再本机测量或静态 blocker；检测点要写进防护章，绕过细节不进生产向交付。**
