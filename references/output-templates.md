# Output templates

## One-pager path

`01_reports/ad_strategy_onepager.md`

Must include sections **0–8** (Chinese headings below). Short tables OK; no mega string dumps.

```markdown
# [package] 广告 SDK 策略配置一页纸

## 0. 样本与分析路径
- 包名/版本/渠道：
- jadx-mcp：已完成
- IDA：未做 / so 列表…
- 设备动态：无设备 L1 / clean 最小集已完成（强制若有设备）
- 总体置信度：

## 1. 广告请求结构
（主接口 + 关键字段 5–15 个）

## 2. 广告策略
### 展示
### 点击
### 频控

## 3. 用户行为触发
（操作 → 广告行为）

## 4. 设备画像
（采集字段清单；真伪判决标 hypothesis）

## 5. 数据链路
（一句话时序）

## 6. SDK 防护机制

## 7. 风控机制
（无对照则写 hypothesis）

## 8. 竞品策略参数
（主位表格：激励/Banner/插屏…）

## 9. 动态验证摘要
- 已确认：
- 已否证：
- 未测：

## 10. 未知与下一步
```

## strategy_model.json (minimal)

Required top-level keys:

- `mediation` (or primary direct sdk description object)
- `local_units`
- `placements` (array)
- `load_policy`
- `callbacks`
- `analysis_path`
- `hypotheses`
- `metrics_coverage` (object with keys "1"…"8" values hypothesis|confirmed|mixed|unknown)

```json
{
  "sample": {"package": "", "channel": "", "analyzed_at": ""},
  "analysis_path": {
    "jadx": true,
    "ida_sos": [],
    "device_available": false,
    "clean_min_dynamic_done": false,
    "dynamic_blocker": null
  },
  "mediation": {"name": "", "version": "", "init_endpoint": "", "strategy_endpoint": ""},
  "local_units": {"reward": "", "banner": "", "interstitial": ""},
  "placements": [
    {
      "role": "reward",
      "tagid": "",
      "waterfall": [{"dsp": "", "parameter": "", "weight": 0}],
      "status": "hypothesis"
    }
  ],
  "load_policy": {},
  "callbacks": {},
  "hypotheses": [
    {
      "id": "H001",
      "claim": "",
      "metric": 8,
      "priority": "P0",
      "result": "pending",
      "env": null,
      "evidence": []
    }
  ],
  "metrics_coverage": {
    "1": "hypothesis",
    "2": "hypothesis",
    "3": "hypothesis",
    "4": "hypothesis",
    "5": "hypothesis",
    "6": "hypothesis",
    "7": "unknown",
    "8": "hypothesis"
  }
}
```

### Device rule for hypotheses

If `analysis_path.device_available` is true:

- `clean_min_dynamic_done` must be true **or** `dynamic_blocker` non-empty string
- at least **3** hypotheses with `result` in `confirmed|refuted|inconclusive` (not all pending)

If device_available is false: hypotheses may stay pending; report must say L1.

## field_dictionary_bound.json

Unchanged discipline: parser + consumer + runtime_effect + evidence; no noise category.

## sdk_inventory.json

Unchanged: one primary_mediation or primary_direct_sdk.

## evidence_index.md / unknowns.md

Optional but recommended.

## Writing rules

1. Static-only claims use 状态=hypothesis when device was available but test not done (should be rare — min dynamic is mandatory).
2. `refuted` is valuable: “code can X but runtime did not”.
3. One-pager is for 8 metrics, not SDK logo lists.
4. validate_outputs.py must pass before “done”.
