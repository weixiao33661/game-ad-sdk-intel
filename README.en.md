# game-ad-sdk-intel

**中文文档（仓库首页）：[README.md](./README.md)**

Agent skill for **authorized** reverse-engineering of mobile game **ad SDK strategy configuration** (Android-focused).

Repository: https://github.com/weixiao33661/game-ad-sdk-intel  
Version: see [`VERSION`](./VERSION) · Agent entry: [`SKILL.md`](./SKILL.md) · License: [MIT](./LICENSE)

## What it does

Turn a game **APK** (+ optional device runs) into an **auditable** competitor ad-intel package:

| # | Metric |
|---|---|
| 1 | Request field structures |
| 2 | Show / click / frequency policies |
| 3 | User-trigger → ad behavior |
| 4 | Device profile fields collected |
| 5 | Data pipeline (init → config → load → show → events) |
| 6 | SDK protection / anti-RE signals |
| 7 | Risk-control signals (measurement-oriented) |
| 8 | Strategy parameters (slots, waterfall/bid, weights, downstream IDs) |

Extended business checklists: [`references/competitor-analysis-capability-map.md`](./references/competitor-analysis-capability-map.md).

## Tool path

```text
APK → jadx-mcp (always)
    → (gate) ida-pro-mcp / idalib-mcp
    → (if device) MANDATORY clean min dynamic
    → optional Frida L-Obs / proxy (tagged env)
    → 8-metric report + JSON
    → python scripts/validate_outputs.py <workspace>
```

**Static proposes. Dynamic disposes.**  
Stuck? [`references/playbooks/`](./references/playbooks/) (PB-01…PB-07).

## Principles (short)

- Planning (P0–P10) is the product; judge/evals are optional regression  
- Device available ⇒ clean baseline required for show/trigger/reward claims  
- Config ≠ runtime winner (write both lines)  
- Field needs consumer; capability ≠ active; no cross-vendor field models  
- Frida observation in-scope; production bypass / ad-fraud playbooks out of scope  

## Install

```bash
git clone https://github.com/weixiao33661/game-ad-sdk-intel.git ~/.codex/skills/game-ad-sdk-intel
# or ~/.claude/skills/game-ad-sdk-intel
```

```bash
cd ~/.codex/skills/game-ad-sdk-intel && git pull origin main
```

## Workspace outputs

```text
workspace/
  01_reports/ad_strategy_onepager.md
  06_extracted/strategy_model.json
  06_extracted/field_dictionary_bound.json
  06_extracted/sdk_inventory.json
```

```bash
python scripts/validate_outputs.py /path/to/workspace
python scripts/run_evals.py --workspace /path/to/workspace --judge
```

## Multi-OEM

Xiaomi mediation, OPPO/HeyTap, Huawei, Honor, vivo (+ GDT/Pangle notes).  
See `references/oem-*-depth.md` and `oem-architecture-matrix.md`.

## Scope

Authorized competitive / defensive research. Documents detection and measurement impact.  
Does **not** ship production risk-control bypass or ad-fraud instructions.

## Layout

```text
SKILL.md, README.md (中文), README.en.md (this file)
scripts/  references/  evals/  agents/
```

## Version

See `VERSION` and `CHANGELOG.md`.
