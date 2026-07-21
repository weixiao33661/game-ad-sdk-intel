#!/usr/bin/env python3
"""Lightweight eval harness for game-ad-sdk-intel.

Layers (in order of importance):
1) Analysis planning workflow lives in SKILL.md P0–P10 (human/agent execution)
2) Structural validate_outputs.py (required for "done")
3) This harness: eval definitions + golden anchors + optional workspace validate
4) Optional semantic scoring via llm_judge.py (deterministic always; --llm if keys exist)

Usage:
  python run_evals.py
  python run_evals.py --workspace /path/to/dcxns
  python run_evals.py --workspace /path/to/dcxns --judge
  python run_evals.py --workspace /path/to/dcxns --judge --llm
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
EVALS = SKILL_ROOT / "evals" / "evals.json"
GOLDEN = SKILL_ROOT / "references" / "golden-case-dcxns.md"
VALIDATE = SKILL_ROOT / "scripts" / "validate_outputs.py"
JUDGE = SKILL_ROOT / "scripts" / "llm_judge.py"

REQUIRED_GOLDEN_NEEDLES = [
    "0e3d75824d784b418cb13ccc1ce22fc8",
    "xiaomi",
    "fake close",
    "click",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workspace",
        default="",
        help="optional analysis workspace to validate/score (e.g. dcxns root)",
    )
    parser.add_argument(
        "--judge",
        action="store_true",
        help="run llm_judge deterministic scoring on all evals (uses workspace as submission)",
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="with --judge, also try LLM refinement if API keys exist",
    )
    parser.add_argument(
        "--eval-id",
        default="",
        help="with --judge, only score this eval id",
    )
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    if not EVALS.exists():
        errors.append(f"missing {EVALS}")
        evals_list = []
    else:
        data = json.loads(EVALS.read_text(encoding="utf-8"))
        if data.get("skill_name") != "game-ad-sdk-intel":
            errors.append(
                f"evals.skill_name expected game-ad-sdk-intel, got {data.get('skill_name')}"
            )
        evals_list = data.get("evals") or []
        if len(evals_list) < 3:
            warnings.append(f"only {len(evals_list)} evals defined")
        for e in evals_list:
            if not e.get("id") or not e.get("prompt"):
                errors.append(f"eval missing id/prompt: {e}")
            if not e.get("expected_hints"):
                warnings.append(f"eval {e.get('id')} has no expected_hints")

    if not GOLDEN.exists():
        errors.append(f"missing golden case {GOLDEN}")
    else:
        text = GOLDEN.read_text(encoding="utf-8", errors="ignore").lower()
        for needle in REQUIRED_GOLDEN_NEEDLES:
            if needle.lower() not in text:
                errors.append(f"golden-case missing anchor: {needle}")

    if not VALIDATE.exists():
        errors.append(f"missing validator {VALIDATE}")

    if args.workspace:
        ws = Path(args.workspace)
        if not ws.exists():
            errors.append(f"workspace not found: {ws}")
        else:
            proc = subprocess.run(
                [sys.executable, str(VALIDATE), str(ws), "--json"],
                capture_output=True,
                text=True,
            )
            try:
                payload = json.loads(proc.stdout or "{}")
            except json.JSONDecodeError:
                payload = {"ok": False, "errors": [proc.stdout, proc.stderr]}
            if proc.returncode != 0 or not payload.get("ok", False):
                errors.append("validate_outputs failed on workspace")
                for e in payload.get("errors") or []:
                    errors.append(f"  validate: {e}")
            for w in payload.get("warnings") or []:
                warnings.append(f"validate: {w}")
            print("workspace validation:", "PASS" if payload.get("ok") else "FAIL")
    else:
        warnings.append("no --workspace given; skipped output validation")

    print(f"evals file: {EVALS}")
    print("eval count check: done")
    print("golden anchors: done")
    print("NOTE: analysis planning workflow (SKILL P0-P10) is the primary path;")
    print("      judge/validate are regression gates, not substitutes for planning.")

    judge_failures = 0
    if args.judge:
        if not JUDGE.exists():
            errors.append(f"missing judge {JUDGE}")
        elif not args.workspace:
            errors.append("--judge requires --workspace (or use llm_judge.py --submission)")
        else:
            targets = (
                [e for e in evals_list if e.get("id") == args.eval_id]
                if args.eval_id
                else [e for e in evals_list if e.get("uses_workspace", True)]
            )
            if args.eval_id and not targets:
                errors.append(f"eval-id not found: {args.eval_id}")
            if not args.eval_id:
                skipped = [e.get("id") for e in evals_list if not e.get("uses_workspace", True)]
                if skipped:
                    warnings.append(
                        "judge skipped non-workspace evals (pass --eval-id to score): "
                        + ", ".join(skipped)
                    )
            for e in targets:
                cmd = [
                    sys.executable,
                    str(JUDGE),
                    "--eval-id",
                    e["id"],
                    "--workspace",
                    str(Path(args.workspace).resolve()),
                    "--json",
                ]
                if args.llm:
                    cmd.append("--llm")
                proc = subprocess.run(cmd, capture_output=True, text=True)
                try:
                    result = json.loads(proc.stdout or "{}")
                except json.JSONDecodeError:
                    result = {
                        "pass": False,
                        "summary": proc.stdout or proc.stderr,
                        "eval_id": e["id"],
                    }
                status = "PASS" if result.get("pass") else "FAIL"
                if not result.get("pass"):
                    judge_failures += 1
                print(
                    f"judge[{e['id']}]: {status} "
                    f"total={((result.get('scores') or {}).get('total'))} "
                    f"mode={result.get('judge_mode')}"
                )
                if result.get("hint_misses"):
                    print(f"  miss_hints: {result.get('hint_misses')}")
                if result.get("critical_failures"):
                    print(f"  critical: {result.get('critical_failures')}")

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(" -", w)
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(" -", e)
        print("FAIL")
        return 1
    if judge_failures:
        print(f"JUDGE_FAILURES: {judge_failures}")
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
