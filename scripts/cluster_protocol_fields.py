#!/usr/bin/env python3
"""Cluster JSON/HAR/text protocol fields into a Markdown field dictionary."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def add_value(fields, path, value):
    if isinstance(value, (dict, list)):
        kind = type(value).__name__
        sample = json.dumps(value, ensure_ascii=False)[:160]
    else:
        kind = type(value).__name__
        sample = str(value)[:160]
    fields[path]["types"][kind] += 1
    fields[path]["samples"][sample] += 1


def walk_json(fields, prefix, obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key
            add_value(fields, path, value)
            walk_json(fields, path, value)
    elif isinstance(obj, list):
        for item in obj[:20]:
            walk_json(fields, f"{prefix}[]", item)


def load_json_objects(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    try:
        return [json.loads(text)]
    except json.JSONDecodeError:
        objects = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                objects.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return objects


def parse_har(fields, obj):
    entries = obj.get("log", {}).get("entries", [])
    for idx, entry in enumerate(entries):
        req = entry.get("request", {})
        res = entry.get("response", {})
        url = req.get("url", "")
        parsed = urlparse(url)
        endpoint = f"{req.get('method', 'GET')} {parsed.netloc}{parsed.path}"
        add_value(fields, "endpoint", endpoint)
        for key, values in parse_qs(parsed.query).items():
            for value in values:
                add_value(fields, f"request.query.{key}", value)
        for header in req.get("headers", []):
            add_value(fields, f"request.header.{header.get('name', '').lower()}", header.get("value", ""))
        post = req.get("postData", {}).get("text")
        if post:
            try:
                walk_json(fields, "request.body", json.loads(post))
            except json.JSONDecodeError:
                add_value(fields, "request.body.raw", post[:300])
        content = res.get("content", {}).get("text")
        if content:
            try:
                walk_json(fields, "response.body", json.loads(content))
            except json.JSONDecodeError:
                add_value(fields, "response.body.raw", content[:300])


def parse_text_fields(fields, text: str):
    for url in re.findall(r"https?://\S+", text):
        parsed = urlparse(url.rstrip(".,;)\"'"))
        add_value(fields, "endpoint", f"{parsed.netloc}{parsed.path}")
        for key, values in parse_qs(parsed.query).items():
            for value in values:
                add_value(fields, f"text.query.{key}", value)
    for key, value in re.findall(r"\b([A-Za-z0-9_.-]{2,64})=([A-Za-z0-9_.:@/-]{1,160})", text):
        add_value(fields, f"text.kv.{key}", value)
    for key in re.findall(r'["\']([A-Za-z0-9_.-]{2,64})["\']\s*:', text):
        add_value(fields, f"text.json_key.{key}", "present")


def category_for(path: str) -> str:
    p = path.lower()
    rules = [
        ("risk", ["risk", "root", "emulator", "proxy", "debug", "hook", "integrity", "verify"]),
        ("experiment", ["ab_", "experiment", "exp_", "bucket", "group", "variant", "layer"]),
        ("strategy", ["cap", "limit", "interval", "cooldown", "cache", "ttl", "priority", "ecpm", "bid", "floor"]),
        ("ad_unit", ["placement", "adunit", "ad_unit", "slot", "pos", "position", "tagid", "dcid", "codeid", "code_id", "rit", "scene"]),
        ("reward", ["reward", "coin", "item", "transaction"]),
        ("device", ["device", "model", "brand", "android", "oaid", "gaid", "imei", "screen", "carrier"]),
        ("user", ["uid", "user", "account", "login", "retention", "payer"]),
        ("event", ["event", "show", "click", "close", "impression", "load"]),
        ("network", ["ip", "country", "region", "network", "wifi", "carrier"]),
    ]
    for category, needles in rules:
        if category == "risk" and ("root_tag" in p or "view_root" in p):
            continue
        if any(n in p for n in needles):
            return category
    return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", help="HAR, JSON, JSONL, or text files")
    parser.add_argument("-o", "--output", default="-", help="output Markdown path, default stdout")
    args = parser.parse_args()

    fields = defaultdict(lambda: {"types": Counter(), "samples": Counter()})

    for name in args.inputs:
        path = Path(name)
        objects = load_json_objects(path)
        if not objects:
            parse_text_fields(fields, path.read_text(encoding="utf-8", errors="ignore"))
            continue
        for obj in objects:
            if isinstance(obj, dict) and "log" in obj and "entries" in obj.get("log", {}):
                parse_har(fields, obj)
            else:
                walk_json(fields, "", obj)

    lines = [
        "| 字段 | 类型 | 样例 | 分类 | 疑似含义 | 置信度 |",
        "|---|---|---|---|---|---|",
    ]
    for path in sorted(fields):
        item = fields[path]
        types = ", ".join(f"{k}:{v}" for k, v in item["types"].most_common(3))
        samples = "; ".join(k.replace("|", "\\|") for k, _ in item["samples"].most_common(3))
        category = category_for(path)
        lines.append(f"| `{path}` | {types} | {samples} | {category} | 待结合代码/行为确认 | low |")

    output = "\n".join(lines) + "\n"
    if args.output == "-":
        print(output)
    else:
        Path(args.output).write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
