# Playbooks 索引（卡点解题）

主流程仍是 `SKILL.md` 的 **P0–P10 + 8 指标**。  
**只有卡住时**才打开对应 playbook，不要每个分析把 6 个全跑一遍。

## 症状 → Playbook

| 你卡住的现象 | 打开 |
|---|---|
| 多个广告 SDK / MAX+OEM，不知道谁是主链路 | [PB-01](PB-01-pick-primary.md) |
| Java 是空壳、`vm_*`、逻辑像在 so 里 | [PB-02](PB-02-shell-native.md) |
| 抓包密文、字段样例拿不到 | [PB-03](PB-03-encrypted-traffic.md) |
| 有设备但一直不出广告 / no-fill | [PB-04](PB-04-no-fill.md) |
| 配置里三方权重，运行却总是一家 | [PB-05](PB-05-config-vs-runtime.md) |
| 发奖条件、点击是否发奖、伪关闭、关闭链路不清 | [PB-06](PB-06-reward-click-close.md) |
| 壳扫 maps/Frida，一 hook 就崩或分析环境无填充 | [PB-07](PB-07-frida-maps-detection.md) |

## 与主流程关系

```text
P0–P10 规划  →  卡点  →  Playbook  →  更新 hypotheses[] / 报告状态
```

- Playbook **不替代** jadx→IDA→强制 clean 动态。
- 有设备时：P0 猜想尽量挂 `playbook` + `dynamic_test`，用动态 **dispose**。
- `validate_outputs`：对 `playbook` / `if_fail_next` 等字段 **仅 warn**（首期不 fail）。

## 统一骨架

每个 PB 含：何时启用 → 先排除 → 最小下一步 → 升级阶梯 → 动态实验 → 报告写法 → 停止条件。

新 PB 复制 [`_template.md`](_template.md)。

## 编号

| ID | 文件 |
|---|---|
| PB-01 | `PB-01-pick-primary.md` |
| PB-02 | `PB-02-shell-native.md` |
| PB-03 | `PB-03-encrypted-traffic.md` |
| PB-04 | `PB-04-no-fill.md` |
| PB-05 | `PB-05-config-vs-runtime.md` |
| PB-06 | `PB-06-reward-click-close.md` |
| PB-07 | `PB-07-frida-maps-detection.md` |
