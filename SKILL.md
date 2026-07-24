---
name: game-ad-sdk-intel
description: Analyze competitor mobile game advertising strategy from an APK using jadx-mcp first, then conditional IDA (ida-pro-mcp/idalib-mcp) for important native code, and mandatory clean-device dynamic validation of hypotheses when a device is available. Covers request field structures, show/click/frequency policies, user-trigger mapping, device profile fields, data pipelines, SDK protection, risk signals, and competitor strategy parameters (mediation waterfall/bidding, OEM ads: Xiaomi/OPPO/Huawei/Honor/vivo, GDT, Pangle). Use for authorized Android game monetization research; do not use to evade third-party production risk controls, fake users, manipulate ad delivery, or enable ad fraud.
---

# Game Ad SDK Intel

## Rules

Use this skill for authorized competitor analysis of Android game ad monetization. Keep every conclusion evidence-backed:

- **Fact**: directly observed in code, resources, traffic, logs, screenshots, or runtime traces.
- **Strong inference**: multiple independent artifacts.
- **Weak hypothesis**: needs dynamic or multi-source validation.

**Static proposes. Dynamic disposes.** Code capability is not production strategy. When a device is available, the clean minimum dynamic set is **mandatory** before finalizing show/trigger/reward/primary-DSP claims.

**Instrumentation:** Frida **observation hooks (L-Obs)** are in-scope and encouraged for config/callback/field capture. Limited **on-device measurement (L-Meas)** on authorized test devices is allowed when needed to finish extraction; label `env` and do not treat it as clean baseline. Do **not** deliver production bypass or ad-fraud playbooks. See `references/instrumentation-policy.md` and **PB-07** for maps/Frida shell detection.

For risk-control work, identify signals and measurement impact only. Do not provide steps to bypass third-party production risk controls, fake users, defeat anti-fraud, or manipulate ad delivery as a product outcome.

### Priority of mechanisms

1. **Analysis planning (tool path + P0–P10 + 8 metrics)** — the product.
2. **Structured outputs** — inspectable model.
3. **`validate_outputs.py`** — hard gate for done.
4. **`llm_judge` / evals** — optional skill regression only.

### Tool path (mandatory order)

```text
APK → jadx-mcp (always)
    → native gate? → ida-pro-mcp / idalib-mcp on selected .so
    → device available? → MANDATORY clean min dynamic (dispose hypotheses)
    → optional Frida observation / proxy (separate env)
    → 8-metric report + JSON → validate_outputs.py
```

Details: `references/tooling-mcp.md`, `references/dynamic-validation.md`.

### When stuck (open a playbook — do not invent a new process)

| Symptom | Playbook |
|---|---|
| Multi-SDK / who is primary | `references/playbooks/PB-01-pick-primary.md` |
| Shell / `vm_*` / logic in `.so` | `references/playbooks/PB-02-shell-native.md` |
| Encrypted traffic / no field samples | `references/playbooks/PB-03-encrypted-traffic.md` |
| Device but no ads / no-fill | `references/playbooks/PB-04-no-fill.md` |
| Config weights ≠ runtime DSP | `references/playbooks/PB-05-config-vs-runtime.md` |
| Reward / click-grant / fake close | `references/playbooks/PB-06-reward-click-close.md` |
| Frida/maps detection kills process | `references/playbooks/PB-07-frida-maps-detection.md` |

Index: `references/playbooks/README.md`. Playbooks are **subroutines** of P0–P10, not a second workflow.

### Non-negotiable rules

1. **Primary layer first** from init/load evidence; else demand/residual/noise.
2. **No cross-vendor field models** (Xiaomi `tagid/info[]` ≠ OPPO `posId` ≠ Huawei/Honor `slotId`).
3. **Field ≠ finding without consumer** (parser → consumer → effect).
4. **Capability ≠ active** without config/runtime proof.
5. **Env tags** on dynamic claims: `clean` | `root_frida` | `proxy`.
6. **Conversion UX** is strategy (click-reward, fake close, store/hap…).
7. **Device available ⇒ clean min dynamic required** (or record `dynamic_blocker`).
8. **Hypothesis backlog required**; promote to confirmed/refuted with evidence.
9. Script triage is not the final dictionary.

## Eight core metrics (delivery spine)

Every final report must cover:

| # | Metric | Content |
|---|---|---|
| 1 | 广告请求结构 | What fields SDKs/app send on each endpoint |
| 2 | 广告策略 | Show / click / frequency policies |
| 3 | 用户行为触发 | Which UX actions trigger load/show/click/download/reward |
| 4 | 设备画像 | OAID/ROM/model/version… collected vs server “real device” judgment |
| 5 | 数据链路 | How ad data is built and uploaded |
| 6 | SDK 防护 | Anti-RE / integrity (Java + native) |
| 7 | 风控机制 | How abnormal traffic may be detected (client signals + paired envs) |
| 8 | 竞品策略参数 | Slots, waterfall/bid, weights, downstream IDs, switches |

Template: `references/report-template.md`.  
Full business checklist (lifecycle, strategy recognition, metadata/events, risk matrix): `references/competitor-analysis-capability-map.md`.

## Workflow (phase gates)

Details: `references/analysis-pipeline.md`, `references/phase-checklist.md`.

### P0 — Scope, tools, device flag

- Artifact types; static / dynamic / combined.
- **Declare `device_available` true/false.**
- Plan: jadx-mcp always; IDA only if native gate; if device → schedule clean min dynamic.

**Exit:** scope block including tool plan + device flag.

### P1 — Sample inventory

Package, channel, engine, shell, natives list, network security config.

**Exit:** channel/sample summary.

### P2 — jadx-mcp static model + SDK inventory

Run jadx-mcp checklist in `tooling-mcp.md`. Classify SDKs; choose one primary; open matching `oem-*-depth.md`.

**Exit:** `sdk_inventory.json` + draft hypotheses.

### P3 — Config surface & request structure (metric 1, 4, 5)

Local IDs, BFF, mediation/OEM endpoints, parsers, device fields in requests.

**Exit:** config surface + bound field rows for request assembly.

### P4 — Lifecycle & user triggers (metric 3, 5)

init → config → load → show → click/close/reward → upload. Unity: follow bridge to final SDK.

**Exit:** lifecycle/trigger table (status hypothesis until dynamic).

### P5 — Strategy objects (metric 2, 8)

Placements: show/click/frequency + waterfall/bid parameters. Vendor-correct IDs.

**Exit:** `strategy_model.json` placements + load_policy.

### P6 — Bound field dictionaries

Only consumer-bound rows. Noise denylist enforced.

**Exit:** `field_dictionary_bound.json`.

### P7 — Conversion / click strategy

Click-also-reward, fake close, store/hap/deeplink, sticky banner, preload-on-close.

**Exit:** metric 2.2 section + hypotheses.

### P8 — Protection & risk (metric 6, 7)

Java + native detection points; request fingerprints; **no confirmed server risk without clean contrast**.

**Exit:** protection/risk tables; IDA if gate fired.

### P9 — Dynamic dispose (MANDATORY if device_available)

Execute clean minimum set from `dynamic-validation.md`. Update `hypotheses[]` results. Optional Frida/proxy afterward.

**Exit:** logs + updated statuses; `clean_min_dynamic_done=true` or `dynamic_blocker`.

### P10 — Eight-metric report + validate

Write one-pager + technical report per template. Run `validate_outputs.py`.

## Vendor routing

Use `china-oem-ad-sdk-fingerprints.md` + `oem-architecture-matrix.md`, then the matching `oem-*-depth.md`.

## Resource guide

| Reference | When |
|---|---|
| `references/tooling-mcp.md` | jadx / IDA order and checklists |
| `references/dynamic-validation.md` | mandatory clean dynamic + hypothesis schema |
| `references/playbooks/README.md` | stuck-point playbooks (PB-01…07) |
| `references/instrumentation-policy.md` | Frida L-Obs/L-Meas vs forbidden production bypass |
| `references/report-template.md` | 8-metric Chinese report |
| `references/competitor-analysis-capability-map.md` | 汇总能力地图：生命周期/策略识别/元数据/风控矩阵 |
| `references/output-templates.md` | one-pager + JSON schemas |
| `references/phase-checklist.md` | execution checkboxes |
| `references/analysis-pipeline.md` | phase order |
| `references/oem-architecture-matrix.md` | multi-OEM architecture |
| `references/china-oem-ad-sdk-fingerprints.md` | fingerprint routing |
| `references/oem-*-depth.md` | per-vendor depth (same layout) |
| `references/field-taxonomy.md` | bound fields / denylist |
| `references/protocol-field-inference.md` | field inference |
| `references/ad-strategy-reverse.md` | strategy reverse notes |
| `references/risk-signal-analysis.md` | risk signals |
| `references/maturity-scorecard.md` | skill quality score |
| `references/llm-judge-rubric.md` | optional regression judge |
| `references/golden-case-dcxns.md` | Xiaomi channel golden |

### Scripts

```text
scripts/extract_ad_indicators.py <jadx_dir> -o indicators.json
scripts/validate_outputs.py <workspace>
scripts/validate_outputs.py <workspace> --json
scripts/run_evals.py --workspace <workspace> [--judge] [--llm]
scripts/llm_judge.py --eval-id dcxns-full-strategy --workspace <workspace> [--llm]
```

Final deliverables must pass `validate_outputs.py`. Planning first; judge optional.

## Output contract

Chinese report with metrics **0–8** (path + eight cores). Structured:

- `06_extracted/strategy_model.json` (includes `analysis_path`, `hypotheses`, `metrics_coverage`)
- `06_extracted/field_dictionary_bound.json`
- `06_extracted/sdk_inventory.json`
- `01_reports/ad_strategy_onepager.md`
- recommended: `evidence_index.md`, `unknowns.md`

## Done criteria

- [ ] jadx-mcp checklist completed
- [ ] IDA run only if native gate; so list recorded if used
- [ ] Single primary argued
- [ ] All 8 metrics present (unknown allowed with probe)
- [ ] `hypotheses[]` present
- [ ] If device_available: clean min dynamic done **or** dynamic_blocker set; ≥3 hypotheses disposed
- [ ] Stuck points resolved via playbooks (or explicit unknown after ladder); P0 hyps prefer `playbook` + `dynamic_test`
- [ ] No pure-static “production strategy” wording for undisposed P0 show/trigger/reward claims when device existed
- [ ] Bound dict without UI noise dumps
- [ ] `validate_outputs.py` exit 0

## Common failures

| Failure | Fix |
|---|---|
| Static-only final report despite adb device | Run mandatory clean min dynamic |
| Stuck improvising without playbook | Open PB-01…06 index |
| Config weights pasted as runtime truth | PB-05 two-line config vs winner |
| IDA-first on all so | jadx first; native gate; PB-02 |
| Weak token OEM primary | package-path rules |
| Xiaomi fields on OPPO primary | correct depth card |
| Adapter AAR = live waterfall | config/runtime dispose |
| Root session as baseline strategy | clean env |
| Strategy = weights only | show/click/frequency + triggers |
| Judge score without P0–P10 | planning is primary |
