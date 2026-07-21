# LLM Judge Rubric (Regression Only)

## Role in the system

**Primary path = analysis planning workflow (P0–P10).**  
**Secondary path = validation + optional LLM judge for regression.**

Never replace phase gates with “ask the model if the report looks good.”

```text
P0–P10 analysis  →  structured outputs  →  validate_outputs.py (required)
                                      →  llm_judge.py (optional regression)
```

## What the judge scores

| Dimension | Weight | Question |
|---|---:|---|
| **Process adherence** | **40%** | Did the submission follow primary-first, vendor field model, bound fields, conversion, env tags? |
| **Structural completeness** | **25%** | Required artifacts present and non-empty in the right roles? |
| **Hint / golden coverage** | **25%** | Expected semantic anchors hit (primary SDK, weights, fake-close, etc.)? |
| **Anti-failure** | **10%** | Avoided known fails (noise dump, wrong primary, cross-vendor field paste)? |

Pass threshold default: **total ≥ 0.75** and **process ≥ 0.60** and **no critical anti-failure**.

## Process adherence checklist (must drive planning)

Judge must look for evidence of:

1. Single primary layer stated with class (`primary_mediation` / `primary_direct_sdk`)
2. Vendor-correct ID vocabulary (no Xiaomi `tagid/info[]` on OPPO-primary samples, etc.)
3. Bound-field discipline (parser/consumer language, not UI string dumps)
4. Lifecycle or trigger mapping (when load/show/reward)
5. Conversion UX section (even if “none found”)
6. Unknowns with probes (not silent gaps)
7. Env tags on dynamic claims when dynamic evidence is used

If the report is only a long keyword dump without primary/routing/placement objects → **process fail** even if some hints match.

## Critical anti-failures (auto fail or heavy penalty)

- Primary = Huawei/vivo/OPPO/Honor from weak tokens only (`SplashView`, bare `open_ad_`, …)
- Main dictionary dominated by `tt_appdownloader_*` / layout flex keys
- AppLovin MAX as primary on Xiaomi `.mi` channel without bridge proof
- Claims server risk changed strategy with no clean vs instrumented comparison
- Cross-vendor field model paste

## Deterministic vs LLM

| Layer | Always on | Needs API |
|---|---|---|
| Hint keyword / regex coverage | yes | no |
| `validate_outputs.py` gate | yes (if workspace) | no |
| Process phrase heuristics | yes | no |
| Nuanced semantic judge | optional | Anthropic or OpenAI key |

LLM judge **refines** scores; it must not invent package facts absent from the submission.

## Judge output schema

```json
{
  "eval_id": "dcxns-full-strategy",
  "pass": true,
  "scores": {
    "process": 0.0,
    "structure": 0.0,
    "hints": 0.0,
    "anti_failure": 0.0,
    "total": 0.0
  },
  "hint_hits": [],
  "hint_misses": [],
  "process_notes": [],
  "critical_failures": [],
  "judge_mode": "deterministic|llm|hybrid",
  "summary": "one paragraph"
}
```

## Usage policy

- Use after changing SKILL/references/scripts to catch regressions.
- Do **not** block day-to-day analysis on LLM judge if API unavailable; still require `validate_outputs.py`.
- For golden `dcxns`, prefer scoring the official `06_extracted` + one-pager as submission baseline.
