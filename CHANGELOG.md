## 2026-07-22 — v0.3.2 Frida/maps playbook + instrumentation policy

### Added
- `references/playbooks/PB-07-frida-maps-detection.md` — research ladder for shell Frida/maps checks
- `references/instrumentation-policy.md` — L-Obs / L-Meas / forbidden production-bypass delivery

### Clarified
- Frida observation is in-scope for config analysis; safety boundary remains no fraud/production bypass playbooks
- Clean baseline vs root_frida split unchanged

## 2026-07-22 — v0.3.1 playbooks (stuck-point solvers)

### Added
- `references/playbooks/` PB-01…PB-06 (Chinese): primary, shell/native, encrypted traffic, no-fill, config vs runtime, reward/click/fake-close
- SKILL "When stuck" index
- hypothesis recommended fields `playbook` / `dynamic_test` / `if_fail_next` (validate **warn** only)

### Policy
- Playbooks are subroutines of P0–P10, not a second main flow
- Device mandatory clean dynamic unchanged

# Changelog

## 2026-07-20 — LLM judge (secondary) + planning-first emphasis

### Added
- `scripts/llm_judge.py` — deterministic semantic scoring always; optional `--llm` (Anthropic/OpenAI)
- `references/llm-judge-rubric.md` — process weight 40%, anti-failure gates
- `run_evals.py --judge` / `--llm` wiring

### Policy
- Analysis planning workflow (SKILL P0–P10) remains the primary product path
- Judge/evals are regression gates only; day-to-day “done” = P0–P10 + `validate_outputs.py`

## 2026-07-20 — merge + enforcement bootstrap

### Added
- Multi-OEM architecture matrix and five equal-layout depth cards (Xiaomi/OPPO/Huawei/Honor/vivo)
- Maturity scorecard
- Merged companion assets: phase-checklist, field-taxonomy, output-templates, golden-case-dcxns, xiaomi-mediation-notes
- `scripts/validate_outputs.py` — hard validation for strategy_model / bound dict / sdk_inventory / one-pager
- `scripts/run_evals.py` — lightweight eval/golden/workspace harness (no LLM)
- Fingerprint primary-selection anti-false-positive logic in `extract_ad_indicators.py`
- `evals/evals.json` updated for unified skill

### Changed
- Single canonical skill path: `~/.codex/skills/game-ad-sdk-intel`
- Workspace companion `ad-sdk-strategy-reverse` deprecated to pointer
- Noisy `skill_validation_*` dumps archived away from default skill root

### Golden sample (dcxns workspace)
- Generated and validator-passed:
  - `06_extracted/strategy_model.json`
  - `06_extracted/field_dictionary_bound.json`
  - `06_extracted/sdk_inventory.json`
  - `06_extracted/evidence_index.md`
  - `06_extracted/unknowns.md`
  - `01_reports/ad_strategy_onepager.md`

### Still open
- LLM-judged eval runner
- Non-Xiaomi golden cases
- Script denoise alignment for cluster/build_field_dictionary
- Dynamic corpus parity across OEMs
- Mirror install to `~/.claude/skills` (optional)

## 2026-07-20 v0.3.0
 
- jadx-mcp first; conditional IDA MCP
- 8-metric report spine
- mandatory clean dynamic when device_available (static proposes / dynamic disposes)
- validate_outputs enforces analysis_path + hypotheses dispose
