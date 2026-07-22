# PB-03 密文流量与请求字段

## 0. 何时启用

**触发症状：**

- 抓包 body 不可读 / 自定义加密
- 只知道有 HTTPS，不知道字段
- 怀疑签名字段在 native 组装

**映射指标：** 1 请求结构、5 数据链路、4 设备字段（样例值）

**典型错误写法：**

- 一上来硬解算法、写长篇密码学
- 没有静态字段名就交空白第 1 章
- 把密文当「无请求」

## 1. 先排除（Fail-fast）

1. **是否其实有明文 JSON**（日志、debug、未加固渠道）→ 先用明文。  
2. **是否只是 HTTPS 证书问题** → 换观察点（Frida parser），不必先拆算法。  
3. **字段是否在 URL query / header 已明文** → 先记表。  
4. **是否应用层 BFF 明文、SDK 密文** → 分接口写，勿混。

## 2. 最小下一步

| 项 | 内容 |
|---|---|
| 工具 | **jadx-mcp** |
| 做什么 | 定位 `encrypt`/`sign`/`toByteArray`/`MessageDigest` 前的 **Map/JSONObject/Builder** |
| 否证标准 | 若加密前对象已含 oaid/tagid 等，则第 1 章可先出「字段名表」 |

同步列出 endpoint 与 builder 类名。

## 3. 升级阶梯（禁止跳级）

| 级 | 动作 | 产出 |
|---|---|---|
| L1 | 静态 builder/请求组装 | 字段**名**清单 |
| L2 | hook/日志 **加密前** 对象 | 字段**样例值** |
| L3 | IDA so 内算法/密钥来源 | 仅当 L2 不够且字段对指标关键 |
| L4 | 稳定明文样本写入 bound dict | grade 可 A_runtime |

## 4. 动态实验设计

```text
claim: getmedconfig/init 请求含 oaid 与 comd5
dynamic_test: clean 下 hook 请求组装或 parser 对侧；打印加密前 map
expected_if_true: 键存在且 oaid 非空（或明确空值策略）
expected_if_false: 无该键或永不赋值
if_fail_next: L3 IDA；或记「键静态存在、运行值 unknown」
```

有设备时：优先 L2 观察，仍属「强制 clean 动态」可覆盖的配置/请求类猜想。

## 5. 如何写进报告

| 状态 | 句式 |
|---|---|
| confirmed（名） | 「请求在 `X` 组装，字段含 …（代码路径）」 |
| confirmed（值） | 「clean 运行样例：oaid=…, comd5=…」 |
| hypothesis | 「静态见字段名，无明文样例」 |
| 加密说明 | 「链路上为密文；分析点取加密前」 |

**分开写：** 传输形态（密文）vs 逻辑字段（明文模型）。

## 6. 停止条件

- 指标 1 有「接口 → 字段名 → 消费者」即达专业 L1  
- 样例值允许 unknown，但要写 L2 探针  
- 不要求为每个包完整破解加密

## 7. 关联

- `protocol-field-inference.md`、`field-taxonomy.md`  
- PB-02（算法在 so）  
- 阶段：P3、P6、P9
