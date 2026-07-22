# Phase checklist

Execute in order. Do not mark complete without exit artifact.

## P0 Scope & tools

- [ ] Package/version/channel recorded
- [ ] `device_available` true/false declared
- [ ] Plan: jadx-mcp always
- [ ] Native gate assessed (list candidate so)
- [ ] If device: clean min dynamic scheduled (mandatory)
- [ ] **Exit:** scope note in report §0

## P1 Sample inventory

- [ ] Engine / shell / ABI
- [ ] Workspace dirs `01_reports` `06_extracted` `03_logs`…
- [ ] **Exit:** sample summary

## P2 jadx-mcp + SDK inventory

- [ ] jadx-mcp must-do checklist done (`tooling-mcp.md`)
- [ ] Primary classified with package-path evidence
- [ ] If multi-SDK conflict → **PB-01**
- [ ] False OEM positives rejected
- [ ] Matching `oem-*-depth.md` opened
- [ ] **Exit:** `06_extracted/sdk_inventory.json`
- [ ] **Exit:** draft `hypotheses[]` (P0; prefer `playbook` + `dynamic_test`)

## P3 Config & request structure

- [ ] Local units / config URLs
- [ ] Init + strategy endpoints + parsers
- [ ] Device fields in requests listed
- [ ] **Exit:** metric 1 draft + bound field rows

## P4 Lifecycle & triggers

- [ ] Game → SDK bridge traced
- [ ] load/show/click/reward/close mapped
- [ ] **Exit:** metric 3 table (hypothesis until dynamic)

## P5 Strategy model

- [ ] Placements with waterfall/bid fields
- [ ] Show / click / frequency subsections drafted
- [ ] **Exit:** `strategy_model.json` core

## P6 Bound dictionaries

- [ ] parser → consumer → effect on each row
- [ ] Noise excluded
- [ ] **Exit:** `field_dictionary_bound.json`

## P7 Conversion

- [ ] Click-also-reward / fake close / store path checked
- [ ] If unclear → **PB-06** (E1/E2/E3 matrix)
- [ ] **Exit:** metric 2.2

## P8 Protection & risk

- [ ] Java protection points
- [ ] If native gate: IDA on selected so; addresses recorded
- [ ] Risk without clean contrast kept hypothesis
- [ ] **Exit:** metrics 6–7

## P9 Dynamic (MANDATORY if device_available)

- [ ] Env=`clean` baseline run
- [ ] Cold start / banner window / reward×3–5 / interstitial if any
- [ ] Reward outcome matrix (complete / click / early close) — **PB-06**
- [ ] Callback order observed
- [ ] No-fill? → **PB-04** ladder before blaming risk
- [ ] Config vs Activity winner → **PB-05** two-line writeup
- [ ] Hypotheses updated confirmed|refuted|inconclusive
- [ ] `clean_min_dynamic_done=true` OR `dynamic_blocker` set
- [ ] Optional: Frida config bodies (L-Obs); if maps/Frida kill → **PB-07**
- [ ] Optional: proxy separate env
- [ ] **Exit:** logs + disposed hypotheses

## P10 Synthesize & validate

- [ ] One-pager metrics 0–8
- [ ] Technical report per template
- [ ] `metrics_coverage` filled
- [ ] `python scripts/validate_outputs.py <workspace>` PASS
