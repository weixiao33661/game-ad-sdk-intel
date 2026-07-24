# game-ad-sdk-intel

Agent skill for **authorized** reverse-engineering of mobile game **ad SDK strategy configuration** (Android-focused).

**中文说明：[README.zh-CN.md](./README.zh-CN.md)**

Repository: https://github.com/weixiao33661/game-ad-sdk-intel

## What it does

Given a game APK (plus optional device runs), produce an evidence-backed profile of:

1. Ad **request field** structures  
2. **Show / click / frequency** policies  
3. **User-trigger** → ad behavior mapping  
4. **Device profile** fields collected (OAID, ROM, model, …)  
5. **Data pipeline** (build → upload → callbacks)  
6. SDK **protection / anti-RE** signals  
7. **Risk-control** signals (measurement-oriented)  
8. Competitor **strategy parameters** (slots, waterfall/bid, weights, downstream IDs)

Extended checklists (lifecycle, strategy recognition, metadata/events, risk matrix) live in  
`references/competitor-analysis-capability-map.md`.

## Tool path

```text
APK → jadx-mcp (always)
    → (gate) ida-pro-mcp / idalib-mcp for important native code
    → (if device) MANDATORY clean minimum dynamic validation
    → optional Frida L-Obs / proxy (separate env)
    → 8-metric report + structured JSON
    → scripts/validate_outputs.py
```

**Static proposes. Dynamic disposes.**

Stuck? Open `references/playbooks/` (PB-01…PB-07).

## Install

```bash
# Codex
git clone https://github.com/weixiao33661/game-ad-sdk-intel.git ~/.codex/skills/game-ad-sdk-intel

# Claude Code
git clone https://github.com/weixiao33661/game-ad-sdk-intel.git ~/.claude/skills/game-ad-sdk-intel
```

Entry file: `SKILL.md`.

## Layout

```text
game-ad-sdk-intel/
  SKILL.md
  README.md / README.zh-CN.md
  VERSION / CHANGELOG.md / LICENSE
  evals/
  scripts/
  references/          # OEM cards, templates, playbooks, capability map
  agents/
```

## Validate a workspace

```bash
python scripts/validate_outputs.py /path/to/analysis_workspace
python scripts/run_evals.py --workspace /path/to/analysis_workspace --judge
```

```text
workspace/
  01_reports/ad_strategy_onepager.md
  06_extracted/strategy_model.json
  06_extracted/field_dictionary_bound.json
  06_extracted/sdk_inventory.json
```

## Multi-OEM

Xiaomi mediation, OPPO/HeyTap, Huawei Petal, Honor, vivo (+ GDT/Pangle notes).  
Do not copy one vendor’s field model onto another.

## Scope

- Authorized competitive and defensive research.  
- Documents detection points and measurement impact.  
- Frida **observation** is in-scope for config analysis (`instrumentation-policy.md`).  
- Does **not** ship production risk-control bypass or ad-fraud playbooks.

## Version

See `VERSION`.

## License

MIT — see `LICENSE`.
