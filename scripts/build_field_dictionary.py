#!/usr/bin/env python3
"""Build a normalized field dictionary from static indicators and protocol field tables."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def category_for(name: str) -> str:
    p = name.lower()
    rules = [
        ("risk", ["risk", "root", "emulator", "proxy", "debug", "hook", "integrity", "verify"]),
        ("experiment", ["ab_", "experiment", "exp_", "bucket", "group", "variant", "layer"]),
        ("strategy", ["cap", "limit", "interval", "cooldown", "cache", "ttl", "priority", "ecpm", "bid", "floor", "parallel", "timeout", "closed"]),
        ("ad_unit", ["placement", "adunit", "ad_unit", "slot", "pos", "position", "tagid", "dcid", "codeid", "code_id", "rit", "appid"]),
        ("reward", ["reward", "coin", "item", "transaction", "callback"]),
        ("device", ["device", "model", "brand", "android", "oaid", "gaid", "imei", "screen", "carrier"]),
        ("user", ["uid", "user", "account", "login", "retention", "payer"]),
        ("event", ["event", "show", "click", "close", "impression", "load"]),
        ("network", ["ip", "country", "region", "network", "wifi", "carrier", "host", "url"]),
    ]
    for category, needles in rules:
        if category == "risk" and ("root_tag" in p or "view_root" in p):
            continue
        if any(n in p for n in needles):
            return category
    return "unknown"


def add_row(rows, direction, field, sample, source, evidence, confidence="medium"):
    rows.append(
        {
            "direction": direction,
            "field": field,
            "sample": str(sample)[:180],
            "category": category_for(field),
            "suspected_meaning": "待结合代码消费者/运行行为确认",
            "source": source,
            "evidence": evidence,
            "confidence": confidence,
        }
    )


def load_indicators(path: Path, rows):
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data.get("xml_ad_strings", []):
        add_row(rows, "static", item.get("name", ""), item.get("value", ""), "xml_ad_strings", item.get("file", ""), "high")
    for item in data.get("string_constants", []):
        add_row(rows, "static", item.get("name", ""), item.get("value", ""), "string_constants", item.get("file", ""), "medium")
    for name, count in data.get("json_keys", []):
        add_row(rows, "static", name, f"seen {count}", "json_keys", "decompiled strings", "low")
    for url, count in data.get("urls", []):
        add_row(rows, "static", "url", url, "urls", f"seen {count}", "medium")
    for item in data.get("manifest_meta", []):
        add_row(rows, "static", item.get("name", ""), item.get("value", ""), "manifest_meta", item.get("file", ""), "medium")


def load_markdown_fields(path: Path, rows):
    text = path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 6:
            continue
        field = parts[0].strip("` ")
        sample = parts[2]
        category = parts[3] if parts[3] else category_for(field)
        rows.append(
            {
                "direction": "protocol",
                "field": field,
                "sample": sample,
                "category": category,
                "suspected_meaning": parts[4] or "待结合代码/行为确认",
                "source": str(path),
                "evidence": "cluster_protocol_fields output",
                "confidence": parts[5] or "low",
            }
        )


def write_markdown(rows, output: Path):
    lines = [
        "| 方向 | 字段 | 样例 | 分类 | 疑似含义 | 来源 | 证据 | 置信度 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    seen = set()
    for row in rows:
        key = (row["direction"], row["field"], row["sample"], row["source"])
        if key in seen:
            continue
        seen.add(key)
        vals = [
            row["direction"],
            f"`{row['field']}`",
            row["sample"],
            row["category"],
            row["suspected_meaning"],
            row["source"],
            row["evidence"],
            row["confidence"],
        ]
        vals = [str(v).replace("|", "\\|").replace("\n", " ") for v in vals]
        lines.append("| " + " | ".join(vals) + " |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(rows, output: Path):
    with output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "direction",
                "field",
                "sample",
                "category",
                "suspected_meaning",
                "source",
                "evidence",
                "confidence",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--indicators", nargs="*", default=[], help="extract_ad_indicators JSON outputs")
    parser.add_argument("--fields", nargs="*", default=[], help="cluster_protocol_fields Markdown outputs")
    parser.add_argument("-o", "--output", required=True, help="output .md or .csv")
    args = parser.parse_args()

    rows = []
    for name in args.indicators:
        load_indicators(Path(name), rows)
    for name in args.fields:
        load_markdown_fields(Path(name), rows)

    out = Path(args.output)
    if out.suffix.lower() == ".csv":
        write_csv(rows, out)
    else:
        write_markdown(rows, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
