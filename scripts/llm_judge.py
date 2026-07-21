#!/usr/bin/env python3
"""Score an analysis submission against game-ad-sdk-intel evals.

Planning workflow remains primary. This script is a regression layer:
  deterministic scoring always; optional LLM refinement if API keys exist.

Examples:
  # Score current dcxns golden outputs (deterministic)
  python llm_judge.py --eval-id dcxns-full-strategy --workspace /path/to/dcxns

  # Score a free-form report file
  python llm_judge.py --eval-id oem-false-positive-guard --submission report.md

  # Hybrid LLM judge (needs ANTHROPIC_API_KEY or OPENAI_API_KEY)
  python llm_judge.py --eval-id dcxns-full-strategy --workspace /path/to/dcxns --llm
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[1]
EVALS_PATH = SKILL_ROOT / "evals" / "evals.json"
VALIDATE = SKILL_ROOT / "scripts" / "validate_outputs.py"
RUBRIC = SKILL_ROOT / "references" / "llm-judge-rubric.md"

WEIGHTS = {
    "process": 0.40,
    "structure": 0.25,
    "hints": 0.25,
    "anti_failure": 0.10,
}

PROCESS_PATTERNS = [
    (r"primary[_ ]?(mediation|direct|layer|vendor)|主聚合|主链路|primary_mediation|primary_direct", "primary_stated"),
    (r"waterfall|isBid|bid|posId|tagid|slotId|权重|竞价|瀑布", "strategy_objects"),
    (r"parser|consumer|runtime_effect|绑定|consumer", "bound_field_language"),
    (r"trigger|lifecycle|loadAd|showAd|何时|回调|onReward", "lifecycle_or_trigger"),
    (r"fake.?close|伪关闭|click.*reward|点击.*发奖|转化|conversion", "conversion_section"),
    (r"unknown|待验证|下一步|probe|未知", "unknowns_present"),
    (r"clean|root_frida|proxy|env", "env_awareness"),
]

# Critical failure patterns → anti_failure score collapse
CRITICAL_PATTERNS = [
    (r"primary[^\n]{0,40}(huawei|honor|vivo|oppo).{0,40}(splashview|open_ad_|com\.heytap\b)", "weak_token_primary"),
    (r"tt_appdownloader_", "noise_ui_dump"),
    (r"primary[^\n]{0,30}(applovin|max).{0,40}(xiaomi|\.mi\b|mediation)", "max_as_primary_on_mi"),
]


def load_evals() -> dict[str, Any]:
    return json.loads(EVALS_PATH.read_text(encoding="utf-8"))


def get_eval(eval_id: str) -> dict[str, Any]:
    data = load_evals()
    for item in data.get("evals", []):
        if item.get("id") == eval_id:
            return item
    raise SystemExit(f"unknown eval id: {eval_id}")


def read_submission_text(workspace: Path | None, submission: Path | None) -> str:
    chunks: list[str] = []
    if submission and submission.exists():
        chunks.append(submission.read_text(encoding="utf-8", errors="ignore"))
    if workspace:
        candidates = [
            workspace / "01_reports" / "ad_strategy_onepager.md",
            workspace / "01_reports" / "ad_strategy_technical.md",
            workspace / "06_extracted" / "strategy_model.json",
            workspace / "06_extracted" / "sdk_inventory.json",
            workspace / "06_extracted" / "field_dictionary_bound.json",
            workspace / "06_extracted" / "unknowns.md",
            workspace / "06_extracted" / "evidence_index.md",
        ]
        for path in candidates:
            if path.exists():
                chunks.append(f"\n\n===== FILE {path.name} =====\n")
                chunks.append(path.read_text(encoding="utf-8", errors="ignore")[:200000])
    text = "\n".join(chunks).strip()
    if not text:
        raise SystemExit("no submission text found (pass --workspace and/or --submission)")
    return text


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower())


def hint_hit(text_norm: str, hint: str) -> bool:
    """Loose semantic hit: all alphanumeric tokens of hint appear nearby-ish.

    Negation-style hints like 'bound fields not tt_appdownloader dump' also pass when
    the forbidden artifact is absent from a structured/bound submission.
    """
    hint_n = normalize(hint)
    if hint_n in text_norm:
        return True
    # Negation hints: "not X" / "no X" / "不要 X"
    if re.search(r"\bnot\b|\bno\b|不要|并非|禁止", hint_n):
        banned_tokens = [
            t
            for t in re.split(r"[^a-z0-9_一-鿿]+", hint_n)
            if len(t) >= 4 and t not in {"not", "fields", "bound", "dump", "weak", "active"}
        ]
        # if banned distinctive tokens (e.g. tt_appdownloader) are absent → hit
        distinctive = [t for t in banned_tokens if t.startswith("tt_") or t in {"splashview", "open_ad"}]
        if distinctive and not any(t in text_norm for t in distinctive):
            return True
    tokens = [t for t in re.split(r"[^a-z0-9_一-鿿]+", hint_n) if len(t) >= 3]
    if not tokens:
        return hint_n in text_norm
    return all(t in text_norm for t in tokens)


def score_hints(text: str, hints: list[str]) -> tuple[float, list[str], list[str]]:
    norm = normalize(text)
    hits, misses = [], []
    for h in hints:
        if hint_hit(norm, h):
            hits.append(h)
        else:
            misses.append(h)
    score = len(hits) / len(hints) if hints else 1.0
    return score, hits, misses


def score_process(text: str) -> tuple[float, list[str]]:
    norm = normalize(text)
    notes = []
    hit = 0
    for pat, name in PROCESS_PATTERNS:
        if re.search(pat, norm, re.I):
            hit += 1
            notes.append(f"process_hit:{name}")
        else:
            notes.append(f"process_miss:{name}")
    return hit / len(PROCESS_PATTERNS), notes


def score_structure(workspace: Path | None) -> tuple[float, list[str]]:
    if not workspace:
        return 0.5, ["structure:no_workspace_partial_credit"]
    notes = []
    required = [
        workspace / "06_extracted" / "strategy_model.json",
        workspace / "06_extracted" / "field_dictionary_bound.json",
        workspace / "06_extracted" / "sdk_inventory.json",
        workspace / "01_reports" / "ad_strategy_onepager.md",
    ]
    present = sum(1 for p in required if p.exists())
    notes.append(f"structure_files:{present}/{len(required)}")
    score = present / len(required)
    # bump if validate_outputs passes
    if VALIDATE.exists() and present == len(required):
        proc = subprocess.run(
            [sys.executable, str(VALIDATE), str(workspace), "--json"],
            capture_output=True,
            text=True,
        )
        try:
            payload = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            payload = {"ok": False}
        if payload.get("ok"):
            score = 1.0
            notes.append("validate_outputs:PASS")
        else:
            score = min(score, 0.6)
            notes.append("validate_outputs:FAIL")
            for e in (payload.get("errors") or [])[:5]:
                notes.append(f"validate_err:{e}")
    return score, notes


def score_anti_failure(text: str) -> tuple[float, list[str]]:
    norm = normalize(text)
    critical: list[str] = []
    for pat, name in CRITICAL_PATTERNS:
        if re.search(pat, norm, re.I):
            critical.append(name)
    # noise density
    if norm.count("tt_appdownloader_") >= 3:
        critical.append("noise_ui_dump_dense")
    if critical:
        return 0.0, critical
    return 1.0, []


def deterministic_judge(eval_item: dict[str, Any], text: str, workspace: Path | None) -> dict[str, Any]:
    hints = eval_item.get("expected_hints") or []
    process_score, process_notes = score_process(text)
    structure_score, structure_notes = score_structure(workspace)
    hints_score, hits, misses = score_hints(text, hints)
    anti_score, critical = score_anti_failure(text)

    total = (
        WEIGHTS["process"] * process_score
        + WEIGHTS["structure"] * structure_score
        + WEIGHTS["hints"] * hints_score
        + WEIGHTS["anti_failure"] * anti_score
    )
    # gates
    passed = total >= 0.75 and process_score >= 0.60 and anti_score >= 1.0
    if critical:
        passed = False

    return {
        "eval_id": eval_item.get("id"),
        "pass": passed,
        "scores": {
            "process": round(process_score, 4),
            "structure": round(structure_score, 4),
            "hints": round(hints_score, 4),
            "anti_failure": round(anti_score, 4),
            "total": round(total, 4),
        },
        "hint_hits": hits,
        "hint_misses": misses,
        "process_notes": process_notes + structure_notes,
        "critical_failures": critical,
        "judge_mode": "deterministic",
        "summary": (
            f"deterministic total={total:.2f} process={process_score:.2f} "
            f"structure={structure_score:.2f} hints={hints_score:.2f} "
            f"critical={critical or 'none'}"
        ),
    }


def call_anthropic(prompt: str, model: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    body = {
        "model": model,
        "max_tokens": 1200,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    parts = []
    for block in data.get("content", []):
        if block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(parts)


def call_openai(prompt: str, model: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a strict rubric grader for ad-SDK reverse-engineering reports. Output JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError("no JSON object in LLM response")
    return json.loads(m.group(0))


def llm_refine(
    eval_item: dict[str, Any],
    submission: str,
    det: dict[str, Any],
    provider: str,
    model: str,
) -> dict[str, Any]:
    rubric_txt = RUBRIC.read_text(encoding="utf-8") if RUBRIC.exists() else ""
    prompt = f"""You grade an ad-SDK strategy analysis submission.

IMPORTANT:
- Analysis planning workflow (primary routing, bound fields, lifecycle, conversion) matters MORE than prose quality.
- Do not invent facts not present in the submission.
- Return a single JSON object matching the schema in the rubric.

Eval id: {eval_item.get('id')}
Eval prompt: {eval_item.get('prompt')}
Expected hints: {json.dumps(eval_item.get('expected_hints') or [], ensure_ascii=False)}

Deterministic pre-score (for reference, you may adjust with justification):
{json.dumps(det, ensure_ascii=False, indent=2)}

Rubric:
{rubric_txt[:6000]}

Submission (truncated):
{submission[:24000]}

Return JSON with keys: eval_id, pass, scores(process,structure,hints,anti_failure,total),
hint_hits, hint_misses, process_notes, critical_failures, judge_mode, summary.
judge_mode must be "llm".
pass requires total>=0.75 and process>=0.60 and no critical_failures.
"""
    if provider == "anthropic":
        raw = call_anthropic(prompt, model=model)
    elif provider == "openai":
        raw = call_openai(prompt, model=model)
    else:
        raise SystemExit(f"unsupported provider: {provider}")

    llm = extract_json_object(raw)
    # hybrid: never let LLM hide critical deterministic failures
    if det.get("critical_failures"):
        llm["critical_failures"] = list(
            dict.fromkeys((llm.get("critical_failures") or []) + det["critical_failures"])
        )
        llm["pass"] = False
        scores = llm.get("scores") or {}
        scores["anti_failure"] = 0.0
        # recompute total if possible
        try:
            total = (
                WEIGHTS["process"] * float(scores.get("process", 0))
                + WEIGHTS["structure"] * float(scores.get("structure", 0))
                + WEIGHTS["hints"] * float(scores.get("hints", 0))
                + WEIGHTS["anti_failure"] * 0.0
            )
            scores["total"] = round(total, 4)
        except (TypeError, ValueError):
            pass
        llm["scores"] = scores
    llm["judge_mode"] = "hybrid" if det else "llm"
    llm["deterministic_baseline"] = det.get("scores")
    return llm


def main() -> int:
    parser = argparse.ArgumentParser(description="LLM/deterministic judge for game-ad-sdk-intel evals")
    parser.add_argument("--eval-id", required=True, help="id from evals/evals.json")
    parser.add_argument("--workspace", default="", help="analysis workspace with 06_extracted/01_reports")
    parser.add_argument("--submission", default="", help="optional free-form report path")
    parser.add_argument("--llm", action="store_true", help="enable LLM refinement if API key present")
    parser.add_argument(
        "--provider",
        default="anthropic",
        choices=["anthropic", "openai"],
        help="LLM provider when --llm",
    )
    parser.add_argument(
        "--model",
        default="",
        help="model id override (default: claude-sonnet-4-6 / gpt-4.1-mini)",
    )
    parser.add_argument("--json", action="store_true", help="print JSON only")
    args = parser.parse_args()

    eval_item = get_eval(args.eval_id)
    workspace = Path(args.workspace).resolve() if args.workspace else None
    submission_path = Path(args.submission).resolve() if args.submission else None
    text = read_submission_text(workspace, submission_path)

    det = deterministic_judge(eval_item, text, workspace)
    result = det

    if args.llm:
        model = args.model or (
            "claude-sonnet-4-6" if args.provider == "anthropic" else "gpt-4.1-mini"
        )
        try:
            result = llm_refine(eval_item, text, det, provider=args.provider, model=model)
        except Exception as exc:  # noqa: BLE001
            result = dict(det)
            result["judge_mode"] = "deterministic_fallback"
            result["summary"] = f"{det['summary']} | LLM unavailable: {exc}"
            result["llm_error"] = str(exc)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"eval_id: {result.get('eval_id')}")
        print(f"mode: {result.get('judge_mode')}")
        print(f"pass: {result.get('pass')}")
        print(f"scores: {json.dumps(result.get('scores'), ensure_ascii=False)}")
        print(f"hint_hits: {result.get('hint_hits')}")
        print(f"hint_misses: {result.get('hint_misses')}")
        if result.get("critical_failures"):
            print(f"critical_failures: {result.get('critical_failures')}")
        print(f"summary: {result.get('summary')}")

    return 0 if result.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
