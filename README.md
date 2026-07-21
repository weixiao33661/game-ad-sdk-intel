# game-ad-sdk-intel

Agent skill for **authorized** reverse-engineering of mobile game **ad SDK strategy configuration** (Android-focused).

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

## Tool path

```text
APK → jadx-mcp (always)
    → (gate) ida-pro-mcp / idalib-mcp for important native code
    → (if device) MANDATORY clean minimum dynamic validation
    → 8-metric report + structured JSON
    → scripts/validate_outputs.py
```

**Static proposes. Dynamic disposes.**

## Install (Claude / Codex skills)

Copy or clone into your skills directory:

```bash
# Codex
git clone <your-repo-url> ~/.codex/skills/game-ad-sdk-intel

# Claude Code
git clone <your-repo-url> ~/.claude/skills/game-ad-sdk-intel
```

Or submodule / sparse checkout as you prefer. Entry file: `SKILL.md`.

## Layout

```text
game-ad-sdk-intel/
  SKILL.md                 # main instructions
  VERSION / CHANGELOG.md
  evals/evals.json
  scripts/                 # triage + validate + judge
  references/              # OEM depth cards, templates, tooling
  agents/openai.yaml       # optional agent metadata
```

## Quick validation

```bash
python scripts/validate_outputs.py /path/to/analysis_workspace
python scripts/run_evals.py --workspace /path/to/analysis_workspace --judge
```

Expected workspace shape:

```text
workspace/
  01_reports/ad_strategy_onepager.md
  06_extracted/strategy_model.json
  06_extracted/field_dictionary_bound.json
  06_extracted/sdk_inventory.json
```

## Multi-OEM

Profiles/depth cards for Xiaomi mediation, OPPO/HeyTap, Huawei Petal, Honor, vivo (+ GDT/Pangle notes). Do not copy one vendor’s field model onto another.

## Ethics / scope

- Authorized competitive and defensive research only.  
- Documents detection and measurement impact.  
- Does **not** provide playbooks to bypass third-party production risk controls, fake users, or commit ad fraud.

## Version

See `VERSION` (currently **0.3.0**).

## License

Add your preferred license when publishing (e.g. MIT). Until then: all rights reserved by the repository owner.
