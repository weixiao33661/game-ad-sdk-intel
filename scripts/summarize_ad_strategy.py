#!/usr/bin/env python3
"""Create a compact ad strategy triage summary from indicator JSON and field tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


KEYWORDS = {
    "placements/config": ["slot", "posid", "position_id", "placement", "tagid", "dcid", "codeid", "code_id", "appid", "app_id"],
    "waterfall/bidding": ["waterfall", "bidding", "bid", "ecpm", "priority", "floor"],
    "frequency": ["cap", "limit", "interval", "cooldown", "daily", "show_count"],
    "preload/cache": ["preload", "cache", "ttl", "expire", "pool"],
    "experiment": ["ab_", "experiment", "exp_", "bucket", "group", "variant", "layer"],
    "reward": ["reward", "coin", "item", "transaction", "callback"],
    "risk": ["risk", "root", "emulator", "proxy", "debug", "hook", "integrity"],
}


def collect_indicator_terms(indicators):
    terms = []
    for item in indicators.get("xml_ad_strings", [])[:200]:
        terms.append((f"{item.get('name')}={item.get('value')}", 1, "xml_ad_strings"))
    for item in indicators.get("string_constants", [])[:200]:
        terms.append((f"{item.get('name')}={item.get('value')}", 1, "string_constants"))
    for key in ("json_keys", "urls", "domains"):
        for item, count in indicators.get(key, []):
            terms.append((str(item), count, key))
    return terms


def collect_sdk_lines(indicators):
    lines = []
    for sdk, hits in indicators.get("sdk_fingerprints", {}).items():
        sample = ", ".join(f"{term}({count})" for term, count in hits[:6])
        lines.append(f"| {sdk} | {sample} |")
    return lines


def collect_vendor_lines(indicators):
    lines = []
    for profile in indicators.get("vendor_profiles", [])[:8]:
        evidence = ", ".join(
            f"{item.get('term')}({item.get('count')}, {item.get('tier')})"
            for item in profile.get("matched_evidence", [])[:5]
        )
        lines.append(
            "| {vendor} | {role} | {confidence} | {reference} | {evidence} |".format(
                vendor=profile.get("vendor", ""),
                role=profile.get("role", ""),
                confidence=profile.get("confidence", ""),
                reference=profile.get("reference", ""),
                evidence=evidence.replace("|", "\\|") if evidence else "",
            )
        )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", help="indicator JSON and/or Markdown field tables")
    parser.add_argument("-o", "--output", default="-", help="output Markdown path, default stdout")
    args = parser.parse_args()

    buckets = {name: [] for name in KEYWORDS}
    sdk_lines = []
    vendor_lines = []
    evidence_files = []

    for name in args.inputs:
        path = Path(name)
        text = path.read_text(encoding="utf-8", errors="ignore")
        evidence_files.append(str(path))
        if path.suffix.lower() == ".json":
            data = json.loads(text)
            vendor_lines.extend(collect_vendor_lines(data))
            sdk_lines.extend(collect_sdk_lines(data))
            for term, count, source in collect_indicator_terms(data):
                low = term.lower()
                for bucket, words in KEYWORDS.items():
                    if bucket == "risk" and ("root_tag" in low or "view_root" in low):
                        continue
                    if any(word in low for word in words):
                        buckets[bucket].append(f"`{term}` ({source}, {count})")
        else:
            for line in text.splitlines():
                low = line.lower()
                for bucket, words in KEYWORDS.items():
                    if bucket == "risk" and ("root_tag" in low or "view_root" in low):
                        continue
                    if any(word in low for word in words):
                        buckets[bucket].append(line.strip())

    lines = ["# 广告策略初筛摘要", "", "## 输入", ""]
    lines.extend(f"- {item}" for item in evidence_files)
    if vendor_lines:
        lines.extend(
            [
                "",
                "## 厂商 Profile 选择",
                "",
                "| 厂商 | 角色 | 置信度 | 建议参考 | 关键证据 |",
                "|---|---|---|---|---|",
            ]
        )
        lines.extend(dict.fromkeys(vendor_lines))
    if sdk_lines:
        lines.extend(["", "## SDK 指纹", "", "| SDK | 命中证据 |", "|---|---|"])
        lines.extend(dict.fromkeys(sdk_lines))
    lines.extend(["", "## 策略线索", "", "| 主题 | 线索 | 下一步验证 |", "|---|---|---|"])
    for bucket, items in buckets.items():
        unique = []
        seen = set()
        for item in items:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        sample = "<br>".join(item.replace("|", "\\|") for item in unique[:8]) if unique else "未发现明显线索"
        lines.append(f"| {bucket} | {sample} | 回到代码消费者、抓包样本和运行时行为中确认含义 |")

    output = "\n".join(lines) + "\n"
    if args.output == "-":
        print(output)
    else:
        Path(args.output).write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
