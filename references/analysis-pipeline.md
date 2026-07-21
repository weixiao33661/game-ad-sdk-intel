# Analysis pipeline

Default order for authorized competitor ad-SDK analysis.

## Phase map → 8 metrics

| Phase | Work | Metrics |
|---|---|---|
| P0 | Scope, device flag, tool plan | 0 |
| P1 | Sample/channel/engine/shell/so list | 0, 4, 6 |
| P2 | jadx-mcp inventory + primary OEM | 8, 5 |
| P3 | Config surface + request fields | **1, 4, 5** |
| P4 | Lifecycle + user triggers | **3, 5, 2.1** |
| P5 | Strategy objects show/click/freq + params | **2, 8** |
| P6 | Bound dictionaries | **1, 4, 5, 8** |
| P7 | Conversion / click UX | **2.2, 3** |
| P8 | Protection + risk (+ IDA if gated) | **6, 7** |
| P9 | **Dynamic dispose (mandatory if device)** | upgrades 2,3,8,1… |
| P10 | 8-metric report + validate | all |

## Tool chain

1. **jadx-mcp** always (`tooling-mcp.md`)
2. **ida-pro-mcp / idalib-mcp** if native gate
3. **Device clean min dynamic** if `device_available` (`dynamic-validation.md`)
4. Optional Frida/proxy with env tags

## Hypothesis loop

```text
jadx/IDA claim → hypotheses[]
  → (device) run test → confirmed | refuted | inconclusive
  → report language follows status
```

Without device: deliver L1; keep hypothesis labels; list probes.

## Static triage output

- SDK inventory with classes
- Primary profile + depth card
- Placement inventory
- Request field candidates
- Hypothesis backlog (P0 items for show/trigger/reward/config)

## Dynamic output

- Disposed hypotheses
- Env comparison table when multi-env
- Promoted grades on strategy parameters

## Reporting

Use `report-template.md` (8 metrics). One-pager from `output-templates.md`.

## Xiaomi channel reminder

For packs like `com.wjly.dcxns.mi`: expect mediation `initconfig`/`getmedconfig`, local slots as tagids, possible MAX bridge residual, conversion tricks in app shell — still dispose with clean dynamic when device exists.
