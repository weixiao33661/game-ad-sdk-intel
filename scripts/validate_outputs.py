#!/usr/bin/env python3
"""Validate game-ad-sdk-intel structured analysis outputs.

Exit codes:
  0 = pass (no errors; warnings allowed)
  1 = fail (one or more errors)
  2 = usage / path error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ALLOWED_SDK_CLASSES = {
    "primary_mediation",
    "primary_direct_sdk",
    "demand_source",
    "direct_sdk",
    "analytics_attribution",
    "residual",
    "noise_hit",
}

ALLOWED_FIELD_CATEGORIES = {
    "device",
    "user",
    "session",
    "ad_unit",
    "placement",
    "strategy",
    "mediation_strategy",
    "experiment",
    "risk",
    "attribution",
    "event",
    "event_track",
    "reward",
    "reward_logic",
    "network",
    "consent",
    "creative_asset",
    "creative_model",
    "channel_config",
    "dsp_request",
    "dsp_bidding_callback",
    "frequency_cap",
    "privacy",
    "unknown",
}

FORBIDDEN_BOUND_CATEGORIES = {"noise"}

ALLOWED_GRADES = {
    "A_runtime",
    "B_static_bound",
    "C_static_present",
    "D_heuristic",
    "high",
    "medium",
    "low",
}

ALLOWED_HYP_RESULTS = {
    "pending",
    "hypothesis",
    "confirmed",
    "refuted",
    "inconclusive",
    "supported",  # legacy alias → treat like confirmed for dispose count
}

DISPOSED = {"confirmed", "refuted", "inconclusive", "supported"}

NOISE_FIELD_PATTERNS = [
    re.compile(r"^tt_appdownloader_", re.I),
    re.compile(r"^tt_dislike_", re.I),
    re.compile(r"^anti_addiction_", re.I),
    re.compile(r"^m_AssemblyName$", re.I),
    re.compile(r"^m_ClassName$", re.I),
    re.compile(r"^m_Script$", re.I),
    re.compile(r"^flexDirection$", re.I),
    re.compile(r"^alignItems$", re.I),
]

# 8-metric one-pager (Chinese); keep some legacy aliases for older samples
ONEPAGER_REQUIRED_HEADINGS = [
    r"样本与分析路径|分析路径|一句话画像",
    r"广告请求结构|请求结构",
    r"广告策略|展示|SDK 结构",
    r"用户行为触发|行为触发|何时弹出|弹出",
    r"设备画像|设备",
    r"数据链路|链路",
    r"防护|SDK 防护",
    r"风控",
    r"策略参数|竞品策略|广告位",
]


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


def load_json(path: Path, rep: Report) -> Any | None:
    if not path.exists():
        rep.err(f"missing file: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        rep.err(f"invalid JSON {path}: {exc}")
        return None


def require_keys(obj: dict, keys: list[str], where: str, rep: Report) -> None:
    for key in keys:
        if key not in obj:
            rep.err(f"{where}: missing required key '{key}'")


def validate_strategy_model(data: Any, rep: Report) -> None:
    if not isinstance(data, dict):
        rep.err("strategy_model: root must be object")
        return
    require_keys(
        data,
        ["mediation", "local_units", "placements", "load_policy", "callbacks"],
        "strategy_model",
        rep,
    )

    # Preferred v0.3 keys (warn if missing for transition)
    for key in ("analysis_path", "hypotheses", "metrics_coverage"):
        if key not in data:
            rep.warn(f"strategy_model: missing recommended key '{key}' (v0.3+)")

    med = data.get("mediation")
    if isinstance(med, dict):
        if not med.get("name"):
            rep.warn("strategy_model.mediation.name empty")
    elif "mediation" in data:
        rep.err("strategy_model.mediation must be object")

    units = data.get("local_units")
    if isinstance(units, dict):
        for k in ("reward", "interstitial", "banner"):
            if k not in units:
                rep.warn(f"strategy_model.local_units missing optional key '{k}'")
    elif "local_units" in data:
        rep.err("strategy_model.local_units must be object")

    placements = data.get("placements")
    if not isinstance(placements, list):
        if "placements" in data:
            rep.err("strategy_model.placements must be array")
    elif not placements:
        rep.warn("strategy_model.placements is empty")
    else:
        for i, p in enumerate(placements):
            where = f"strategy_model.placements[{i}]"
            if not isinstance(p, dict):
                rep.err(f"{where}: must be object")
                continue
            for key in ("role", "tagid", "waterfall"):
                if key not in p:
                    rep.err(f"{where}: missing '{key}'")
            wf = p.get("waterfall")
            if wf is None:
                continue
            if not isinstance(wf, list):
                rep.err(f"{where}.waterfall must be array")
                continue
            if not wf and p.get("role") in {"reward", "banner", "interstitial"}:
                rep.warn(f"{where}: empty waterfall for role={p.get('role')}")
            for j, node in enumerate(wf):
                nwhere = f"{where}.waterfall[{j}]"
                if not isinstance(node, dict):
                    rep.err(f"{nwhere}: must be object")
                    continue
                for key in ("dsp", "parameter", "weight"):
                    if key not in node:
                        rep.err(f"{nwhere}: missing '{key}'")
                if "weight" in node and not isinstance(node["weight"], (int, float)):
                    rep.err(f"{nwhere}.weight must be number")

    # analysis_path + device mandatory dynamic
    ap = data.get("analysis_path")
    if isinstance(ap, dict):
        if "device_available" not in ap:
            rep.warn("analysis_path.device_available missing")
        device = bool(ap.get("device_available"))
        done = bool(ap.get("clean_min_dynamic_done"))
        blocker = ap.get("dynamic_blocker")
        if device and not done and not blocker:
            rep.err(
                "analysis_path: device_available=true requires clean_min_dynamic_done=true "
                "or non-empty dynamic_blocker"
            )
        if device and not done and blocker:
            rep.warn(f"analysis_path: dynamic blocked: {blocker}")
        if ap.get("jadx") is False:
            rep.err("analysis_path.jadx must be true (jadx-mcp is mandatory first static surface)")
    elif "analysis_path" in data:
        rep.err("analysis_path must be object")

    # hypotheses
    hyps = data.get("hypotheses")
    if isinstance(hyps, list):
        if not hyps:
            rep.warn("hypotheses array is empty")
        disposed = 0
        p0_missing_playbook = 0
        for i, h in enumerate(hyps):
            where = f"hypotheses[{i}]"
            if not isinstance(h, dict):
                rep.err(f"{where}: must be object")
                continue
            for key in ("id", "claim", "result"):
                if key not in h or h[key] in ("", None):
                    rep.err(f"{where}: missing/empty '{key}'")
            res = h.get("result")
            if res and res not in ALLOWED_HYP_RESULTS:
                rep.warn(f"{where}: uncommon result '{res}'")
            if res in DISPOSED:
                disposed += 1
            # v0.3.1 playbook fields: warn only (do not fail)
            prio = str(h.get("priority") or "").upper()
            if prio in {"P0", "0", "HIGH"} or h.get("priority") == 0:
                if not h.get("playbook"):
                    p0_missing_playbook += 1
                    rep.warn(
                        f"{where}: P0 hypothesis missing recommended 'playbook' "
                        "(e.g. PB-01…PB-06)"
                    )
                if not h.get("dynamic_test") and res in {"pending", "hypothesis", None, ""}:
                    rep.warn(
                        f"{where}: pending/hypothesis missing recommended 'dynamic_test'"
                    )
            if h.get("playbook") and not re.match(
                r"^PB-0[1-6]([_-].*)?$", str(h.get("playbook")), re.I
            ):
                # allow free text that contains PB-0x
                if not re.search(r"PB-0[1-6]", str(h.get("playbook")), re.I):
                    rep.warn(
                        f"{where}: playbook '{h.get('playbook')}' not in PB-01…PB-06 "
                        "(ok if custom; preferred standard ids)"
                    )
        if p0_missing_playbook:
            rep.warn(
                f"hypotheses: {p0_missing_playbook} P0 item(s) without playbook "
                "(warn only; see references/playbooks/)"
            )
        ap = data.get("analysis_path") if isinstance(data.get("analysis_path"), dict) else {}
        if ap.get("device_available") and ap.get("clean_min_dynamic_done") and disposed < 3:
            rep.err(
                f"hypotheses: device dynamic done but only {disposed} disposed "
                "(need ≥3 confirmed|refuted|inconclusive)"
            )
    elif "hypotheses" in data:
        rep.err("hypotheses must be array")

    mc = data.get("metrics_coverage")
    if isinstance(mc, dict):
        for k in [str(i) for i in range(1, 9)]:
            if k not in mc:
                rep.warn(f"metrics_coverage missing key '{k}'")
    elif "metrics_coverage" in data:
        rep.err("metrics_coverage must be object")


def validate_field_dictionary(data: Any, rep: Report) -> None:
    if not isinstance(data, dict):
        rep.err("field_dictionary_bound: root must be object")
        return
    require_keys(data, ["sample", "rows"], "field_dictionary_bound", rep)
    rows = data.get("rows")
    if not isinstance(rows, list):
        if "rows" in data:
            rep.err("field_dictionary_bound.rows must be array")
        return
    if not rows:
        rep.err("field_dictionary_bound.rows must not be empty")
        return

    for i, row in enumerate(rows):
        where = f"field_dictionary_bound.rows[{i}]"
        if not isinstance(row, dict):
            rep.err(f"{where}: must be object")
            continue
        for key in ("field", "category", "parser", "consumer", "runtime_effect", "evidence", "grade"):
            if key not in row or row[key] in ("", None, []):
                rep.err(f"{where}: missing/empty '{key}'")
        cat = row.get("category")
        if cat in FORBIDDEN_BOUND_CATEGORIES:
            rep.err(f"{where}: category 'noise' not allowed in bound dictionary")
        elif cat and cat not in ALLOWED_FIELD_CATEGORIES:
            rep.warn(f"{where}: uncommon category '{cat}'")
        grade = row.get("grade")
        if grade and grade not in ALLOWED_GRADES:
            rep.warn(f"{where}: uncommon grade '{grade}'")
        field = str(row.get("field") or "")
        for pat in NOISE_FIELD_PATTERNS:
            if pat.search(field):
                rep.err(f"{where}: field '{field}' matches noise denylist")
                break
        ev = row.get("evidence")
        if ev is not None and not isinstance(ev, list):
            rep.err(f"{where}.evidence must be array")
        elif isinstance(ev, list) and not ev:
            rep.err(f"{where}.evidence must be non-empty")


def validate_sdk_inventory(data: Any, rep: Report) -> None:
    if not isinstance(data, dict):
        rep.err("sdk_inventory: root must be object")
        return
    require_keys(data, ["sample", "sdks"], "sdk_inventory", rep)
    sdks = data.get("sdks")
    if not isinstance(sdks, list):
        if "sdks" in data:
            rep.err("sdk_inventory.sdks must be array")
        return
    if not sdks:
        rep.err("sdk_inventory.sdks must not be empty")
        return

    primaries = []
    for i, sdk in enumerate(sdks):
        where = f"sdk_inventory.sdks[{i}]"
        if not isinstance(sdk, dict):
            rep.err(f"{where}: must be object")
            continue
        for key in ("id", "class", "grade", "evidence"):
            if key not in sdk or sdk[key] in ("", None, []):
                rep.err(f"{where}: missing/empty '{key}'")
        cls = sdk.get("class")
        if cls and cls not in ALLOWED_SDK_CLASSES:
            rep.err(f"{where}: invalid class '{cls}'")
        if cls in {"primary_mediation", "primary_direct_sdk"}:
            primaries.append(sdk.get("id"))
        if cls == "noise_hit":
            rep.warn(f"{where}: noise_hit present — ensure it is not treated as active strategy")

    if not primaries:
        rep.err("sdk_inventory: no primary_mediation/primary_direct_sdk entry")
    elif len(primaries) > 1:
        rep.warn(f"sdk_inventory: multiple primaries {primaries} — report must justify conflict")


def validate_onepager(path: Path, rep: Report) -> None:
    if not path.exists():
        rep.err(f"missing one-pager: {path}")
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    if len(text.strip()) < 200:
        rep.err("one-pager: content too short")
    for pat in ONEPAGER_REQUIRED_HEADINGS:
        if not re.search(pat, text):
            rep.err(f"one-pager: missing required section matching /{pat}/")
    if text.count("|") > 400:
        rep.warn("one-pager: very large table content — consider moving detail to JSON")
    if "tt_appdownloader_" in text:
        rep.err("one-pager: contains noise key tt_appdownloader_*")


def validate_workspace(root: Path, rep: Report) -> None:
    extracted = root / "06_extracted"
    reports = root / "01_reports"
    base_ext = extracted if extracted.is_dir() else root
    base_rep = reports if reports.is_dir() else root

    strategy_path = base_ext / "strategy_model.json"
    fields_path = base_ext / "field_dictionary_bound.json"
    sdk_path = base_ext / "sdk_inventory.json"
    one_pager = base_rep / "ad_strategy_onepager.md"

    strategy = load_json(strategy_path, rep)
    if strategy is not None:
        validate_strategy_model(strategy, rep)

    fields = load_json(fields_path, rep)
    if fields is not None:
        validate_field_dictionary(fields, rep)

    sdks = load_json(sdk_path, rep)
    if sdks is not None:
        validate_sdk_inventory(sdks, rep)

    validate_onepager(one_pager, rep)

    if isinstance(strategy, dict) and isinstance(sdks, dict):
        prim = [
            s.get("id")
            for s in sdks.get("sdks", [])
            if isinstance(s, dict) and s.get("class") in {"primary_mediation", "primary_direct_sdk"}
        ]
        med_name = (strategy.get("mediation") or {}).get("name", "")
        if prim and med_name and not any(
            str(p).lower() in str(med_name).lower() or str(med_name).lower() in str(p).lower()
            for p in prim
        ):
            rep.warn(
                f"cross: mediation.name '{med_name}' does not obviously match primary sdk ids {prim}"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate game-ad-sdk-intel analysis outputs")
    parser.add_argument(
        "workspace",
        nargs="?",
        default=".",
        help="analysis workspace root (contains 06_extracted/ and 01_reports/)",
    )
    parser.add_argument("--json", action="store_true", help="print machine-readable result")
    args = parser.parse_args(argv)

    root = Path(args.workspace).resolve()
    if not root.exists():
        print(f"workspace not found: {root}", file=sys.stderr)
        return 2

    rep = Report()
    validate_workspace(root, rep)

    if args.json:
        print(
            json.dumps(
                {
                    "workspace": str(root),
                    "ok": rep.ok,
                    "errors": rep.errors,
                    "warnings": rep.warnings,
                    "error_count": len(rep.errors),
                    "warning_count": len(rep.warnings),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"workspace: {root}")
        if rep.errors:
            print(f"ERRORS ({len(rep.errors)}):")
            for e in rep.errors:
                print(f"  - {e}")
        else:
            print("ERRORS: 0")
        if rep.warnings:
            print(f"WARNINGS ({len(rep.warnings)}):")
            for w in rep.warnings:
                print(f"  - {w}")
        else:
            print("WARNINGS: 0")
        print("PASS" if rep.ok else "FAIL")

    return 0 if rep.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
