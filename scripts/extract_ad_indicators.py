#!/usr/bin/env python3
"""Extract triage indicators from jadx/apktool output for game ad SDK analysis."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

TEXT_EXTS = {
    ".java",
    ".kt",
    ".xml",
    ".json",
    ".smali",
    ".properties",
    ".txt",
    ".cfg",
    ".ini",
}

ARCHIVE_EXTS = {".aar", ".jar", ".apk", ".dex"}
NATIVE_EXTS = {".so"}
URL_RE = re.compile(r"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+")
DOMAIN_RE = re.compile(r"\b(?:[a-z0-9-]+\.)+(?:com|net|org|io|cn|co|me|app|top|xyz)\b", re.I)
JSON_KEY_RE = re.compile(r'["\']([A-Za-z0-9_.-]{2,64})["\']\s*:')
XML_STRING_RE = re.compile(r'<string\s+name="([^"]+)">([^<]{0,300})</string>')
JAVA_STRING_RE = re.compile(r'\b(?:String|final\s+String|static\s+final\s+String)\s+([A-Za-z0-9_]{2,80})\s*=\s*"([^"]{1,300})"')
ID_RE = re.compile(
    r"\b(?:app[_-]?id|appid|placement[_-]?id|ad[_-]?unit[_-]?id|slot[_-]?id|pos[_-]?id|position[_-]?id|code[_-]?id|rit|tagid|dcid|sdk[_-]?key|scene[_-]?id|bannerSlotId|rewardSlotId|instSlotId)\b",
    re.I,
)
AD_WORD_RE = re.compile(
    r"\b(ad|ads|advert|reward|interstitial|splash|banner|native|mediation|waterfall|bidding|ecpm|placement|adunit)\b",
    re.I,
)
RISK_WORD_RE = re.compile(
    r"\b(root|emulator|proxy|vpn|debug|frida|xposed|hook|integrity|risk|verify|signature|pinning)\b",
    re.I,
)

SDK_FINGERPRINTS = {
    "xiaomi_mimo": [
        "com.xiaomi.ad.mediation",
        "com.miui.zeus.mimo",
        "mimo_sdk",
        "libmimo_",
        "config/union/v1/getmedconfig",
        "config/union/v1/initconfig",
        "MiMoNewSdk",
        "MIMOAdSdkConfig",
    ],
    "oppo_heytap": [
        "com.opos.mobad",
        "com.heytap.msp.mobad",
        "MobAdManager",
        "PosConfigManager",
        "mobad_normal",
        "mobad_",
    ],
    "huawei_ads": [
        "com.huawei.hms.ads",
        "com.huawei.openalliance.ad",
        "com.huawei.hms:ads-lite",
        "HwAds",
        "NativeAdLoader",
        "InstreamAdLoader",
    ],
    "honor_ads": [
        "com.hihonor.adsdk",
        "com.hihonor.mcs.lite",
        "com.hihonor.mms.ads",
        "ppskit",
        "honor_ads_lite",
        "HnAds",
        "HnAdConfig",
        "ads-mediation-adapters",
    ],
    "vivo_ads": [
        "com.vivo.mobilead",
        "VivoAdManager",
        "UnifiedVivo",
        "VivoNativeAd",
        "NativeAdParams",
    ],
    "tencent_gdt": ["com.qq.e.ads", "GDTSDK", "gdt_file_path", "GDTDOWNLOAD"],
    "pangle_toutiao": [
        "com.bytedance.sdk.openadsdk",
        "com.ss.android.socialbase",
        "TTAdSdk",
        "TTAdNative",
        "ToutiaoAd",
        "open_ad_sdk",
    ],
    "kuaishou": ["com.kwad.sdk", "kssdk-ad", "KsAdSDK", "KsScene"],
    "applovin_max": ["com.applovin", "MaxUnityPlugin", "AppLovinSdk", "MaxRewardedAd"],
}

# Ambiguous tokens that must not decide primary OEM alone.
WEAK_PRIMARY_TERMS = {
    "SplashView",
    "SplashAd",
    "BannerView",
    "RewardAd",
    "AdSlot",
    "AdSlot.Builder",
    "getToken",
    "com.heytap",
    "com.opos",
    "open_ad_",
    "open_ad_sdk",
    "OneTrack",
    "com.xiaomi.onetrack",
    "ads-consent",
    "ads-omsdk",
    "ads-tools",
    "libmimo_",
}

VENDOR_PROFILES = {
    "xiaomi_mimo": {
        "display_name": "Xiaomi MiMo mediation",
        "reference": "references/oem-xiaomi-mimo.md",
        "role": "oem_mediation",
        "high": [
            "com.xiaomi.ad.mediation",
            "com.miui.zeus.mimo",
            "MiMoNewSdk",
            "MIMOAdSdkConfig",
            "config/union/v1/getmedconfig",
            "config/union/v1/initconfig",
            "mimo_sdk",
        ],
        "medium": ["AdRepository", "MMRewardVideoAd", "MMAdSplash", "MMAdTemplate"],
        "low": ["libmimo_", "com.xiaomi.onetrack", "OneTrack"],
    },
    "oppo_heytap": {
        "display_name": "OPPO / HeyTap MobAd",
        "reference": "references/oem-oppo-heytap.md",
        "role": "oem_ad_sdk",
        "high": ["com.opos.mobad", "com.heytap.msp.mobad", "MobAdManager", "mobad_normal"],
        "medium": ["PosConfigManager", "NativeAdvanceAd", "POS_TYPE"],
        "low": ["com.heytap", "com.opos", "getToken"],
    },
    "huawei_ads": {
        "display_name": "Huawei / Petal Ads",
        "reference": "references/oem-huawei-petal.md",
        "role": "oem_ad_sdk",
        "high": [
            "com.huawei.hms.ads",
            "com.huawei.openalliance.ad",
            "HwAds",
            "com.huawei.hms:ads-lite",
        ],
        "medium": ["NativeAdLoader", "InstreamAdLoader", "RewardAd", "SplashAd"],
        "low": ["ads-consent", "ads-omsdk", "BannerView", "SplashView"],
    },
    "honor_ads": {
        "display_name": "Honor Ads",
        "reference": "references/oem-honor-ads.md",
        "role": "oem_ad_sdk",
        "high": ["com.hihonor.adsdk", "HnAds", "HnAdConfig", "honor_ads_lite", "ppskit"],
        "medium": ["ads-mediation-adapters", "aggregation-access", "com.hihonor.mms.ads"],
        "low": ["com.hihonor.mcs.lite", "ads-tools", "AdSlot.Builder"],
    },
    "vivo_ads": {
        "display_name": "vivo Ads",
        "reference": "references/oem-vivo-ads.md",
        "role": "oem_ad_sdk",
        "high": ["com.vivo.mobilead", "VivoAdManager", "UnifiedVivo"],
        "medium": ["NativeAdParams", "VivoNativeAd", "VivoAdError"],
        "low": ["open_ad_", "open_ad_sdk", "AdParams.Builder"],
    },
}

VENDOR_TERM_WEIGHTS = {"high": 10, "medium": 5, "low": 1}

for _vendor_name, _vendor_cfg in VENDOR_PROFILES.items():
    SDK_FINGERPRINTS.setdefault(_vendor_name, [])
    for _tier in VENDOR_TERM_WEIGHTS:
        for _term in _vendor_cfg.get(_tier, []):
            if _term not in SDK_FINGERPRINTS[_vendor_name]:
                SDK_FINGERPRINTS[_vendor_name].append(_term)

AD_RESOURCE_KEY_RE = re.compile(
    r"(^ad$|_ad_|ad[_-]?id|ads?|slot|posid|pos_id|position_id|placement|appid|app_id|codeid|code_id|rit|tagid|dcid|banner|reward|instslot|inst_|splash|native|interstitial|download|install|deeplink|callback)",
    re.I,
)
STRONG_AD_KEY_RE = re.compile(
    r"(slot|posid|pos_id|position_id|placement|appid|app_id|codeid|code_id|rit|tagid|dcid|banner|reward|splash|native|interstitial|bidding|ecpm|callback|config_url|data_center|download|install)",
    re.I,
)
MANIFEST_COMPONENT_RE = re.compile(
    r"<(activity|service|receiver|provider)\b[^>]*android:name=\"([^\"]+)\"[^>]*>",
    re.I,
)
MANIFEST_PERMISSION_RE = re.compile(r"<uses-permission\b[^>]*android:name=\"([^\"]+)\"", re.I)
MANIFEST_META_RE = re.compile(
    r"<meta-data\b[^>]*android:name=\"([^\"]+)\"[^>]*(?:android:value|android:resource)=\"([^\"]+)\"[^>]*/?>",
    re.I,
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_EXTS:
            yield path


def iter_all_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file():
            yield path


def looks_interesting_component(name: str) -> bool:
    low = name.lower()
    needles = [
        "ad",
        "ads",
        "reward",
        "splash",
        "interstitial",
        "download",
        "webview",
        "deeplink",
        "gdt",
        "mimo",
        "tt",
        "kwad",
        "opos",
        "huawei",
        "hihonor",
        "vivo",
        "xiaomi",
        "applovin",
    ]
    return any(n in low for n in needles)


def noisy_resource_key(key: str, file_name: str) -> bool:
    low_key = key.lower()
    low_file = file_name.lower()
    noisy_prefixes = ("abc_", "androidx_", "nav_", "mtrl_", "material_", "search_menu_")
    noisy_paths = ("sources\\androidx\\", "sources\\android\\support\\", "sources\\kotlin\\", "sources\\kotlinx\\")
    return low_key.startswith(noisy_prefixes) or any(p in low_file for p in noisy_paths)


def interesting_ad_source(file_name: str) -> bool:
    low = file_name.lower()
    needles = [
        "\\com\\xiaomi\\ad\\",
        "\\com\\miui\\zeus\\mimo\\",
        "\\com\\qq\\e\\",
        "\\com\\bytedance\\sdk\\openadsdk\\",
        "\\com\\ss\\android\\socialbase\\",
        "\\com\\kwad\\",
        "\\com\\opos\\",
        "\\com\\huawei\\hms\\ads\\",
        "\\com\\hihonor\\adsdk\\",
        "\\com\\vivo\\mobilead\\",
        "\\com\\applovin\\",
        "\\com\\android\\common\\",
        "\\com\\gamecontrol\\",
    ]
    return any(n in low for n in needles)


def score_vendor_profiles(sdk_hits):
    profiles = []
    for vendor, cfg in VENDOR_PROFILES.items():
        evidence = []
        score = 0
        high_score = 0
        weak_only_score = 0
        strong_high_terms = set()
        hits = sdk_hits.get(vendor, Counter())
        for tier, weight in VENDOR_TERM_WEIGHTS.items():
            for term in cfg.get(tier, []):
                count = hits.get(term, 0)
                if not count:
                    continue
                # Down-weight ambiguous tokens so they cannot win primary selection alone.
                if term in WEAK_PRIMARY_TERMS:
                    effective_weight = 1 if tier == "low" else min(weight, 2)
                else:
                    effective_weight = weight
                weighted = count * effective_weight
                score += weighted
                if tier == "high" and term not in WEAK_PRIMARY_TERMS:
                    high_score += weighted
                    strong_high_terms.add(term)
                if term in WEAK_PRIMARY_TERMS:
                    weak_only_score += weighted
                evidence.append(
                    {
                        "term": term,
                        "count": count,
                        "tier": tier,
                        "weighted_score": weighted,
                        "weak_term": term in WEAK_PRIMARY_TERMS,
                    }
                )
        if not score:
            continue
        # Require real high-tier package/API evidence for high/medium confidence.
        # A single sparse package string hit (e.g. count=2 → score 20) stays medium, not high.
        distinct_high = len(strong_high_terms)
        if high_score >= 50 or (high_score >= 20 and distinct_high >= 2):
            confidence = "high"
        elif high_score >= 10:
            confidence = "medium"
        elif high_score > 0 and score >= 15:
            confidence = "medium"
        else:
            confidence = "low"
        if high_score <= 0 and weak_only_score == score:
            confidence = "low"
        profiles.append(
            {
                "vendor": vendor,
                "display_name": cfg["display_name"],
                "role": cfg["role"],
                "reference": cfg["reference"],
                "score": score,
                "high_tier_score": high_score,
                "distinct_high_terms": distinct_high,
                "confidence": confidence,
                "eligible_primary": high_score >= 10,
                "matched_evidence": sorted(
                    evidence,
                    key=lambda item: (item["weighted_score"], item["count"], item["term"]),
                    reverse=True,
                )[:20],
            }
        )
    profiles.sort(
        key=lambda item: (
            item.get("eligible_primary", False),
            item["high_tier_score"],
            item["score"],
            item["confidence"] == "high",
            item["confidence"] == "medium",
        ),
        reverse=True,
    )
    return profiles


def choose_primary_profile(vendor_profiles):
    """Prefer vendors with high-tier evidence; never primary on weak-only hits."""
    if not vendor_profiles:
        return None
    for profile in vendor_profiles:
        if profile.get("eligible_primary") and profile.get("confidence") in {"high", "medium"}:
            return profile
    for profile in vendor_profiles:
        if profile.get("eligible_primary"):
            return profile
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", help="jadx/apktool output directory")
    parser.add_argument("-o", "--output", default="-", help="output JSON path, default stdout")
    parser.add_argument("--max-files", type=int, default=20000)
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        raise SystemExit(f"input not found: {root}")

    urls = Counter()
    domains = Counter()
    json_keys = Counter()
    xml_strings = []
    string_constants = []
    id_hits = []
    ad_hits = []
    risk_hits = []
    packages = Counter()
    sdk_hits = {name: Counter() for name in SDK_FINGERPRINTS}
    manifest_permissions = Counter()
    manifest_components = []
    manifest_meta = []
    native_libraries = []
    archives = []

    for idx, path in enumerate(iter_files(root)):
        if idx >= args.max_files:
            break
        rel = str(path.relative_to(root))
        text = read_text(path)
        if not text:
            continue

        for url in URL_RE.findall(text):
            urls[url[:300]] += 1
        for domain in DOMAIN_RE.findall(text):
            domains[domain.lower()] += 1
        for key in JSON_KEY_RE.findall(text):
            json_keys[key] += 1
        for key, value in XML_STRING_RE.findall(text):
            if not noisy_resource_key(key, rel) and (AD_RESOURCE_KEY_RE.search(key) or AD_RESOURCE_KEY_RE.search(value)):
                xml_strings.append({"file": rel, "name": key, "value": value})
        for key, value in JAVA_STRING_RE.findall(text):
            strong_hit = STRONG_AD_KEY_RE.search(key) or STRONG_AD_KEY_RE.search(value)
            if not noisy_resource_key(key, rel) and strong_hit and (interesting_ad_source(rel) or STRONG_AD_KEY_RE.search(key)):
                string_constants.append({"file": rel, "name": key, "value": value})
        if ID_RE.search(text):
            id_hits.append(rel)
        if AD_WORD_RE.search(text):
            ad_hits.append(rel)
        if RISK_WORD_RE.search(text):
            risk_hits.append(rel)

        for match in re.finditer(r"\bpackage\s+([A-Za-z0-9_.]+)\s*;", text):
            packages[match.group(1)] += 1
        for sdk_name, needles in SDK_FINGERPRINTS.items():
            for needle in needles:
                if needle in text:
                    sdk_hits[sdk_name][needle] += 1
        if path.name == "AndroidManifest.xml":
            for perm in MANIFEST_PERMISSION_RE.findall(text):
                manifest_permissions[perm] += 1
            for ctype, name in MANIFEST_COMPONENT_RE.findall(text):
                if looks_interesting_component(name):
                    manifest_components.append({"file": rel, "type": ctype, "name": name})
            for name, value in MANIFEST_META_RE.findall(text):
                if AD_RESOURCE_KEY_RE.search(name) or AD_RESOURCE_KEY_RE.search(value):
                    manifest_meta.append({"file": rel, "name": name, "value": value})

    for idx, path in enumerate(iter_all_files(root)):
        if idx >= args.max_files:
            break
        suffix = path.suffix.lower()
        rel = str(path.relative_to(root))
        if suffix in NATIVE_EXTS:
            native_libraries.append(rel)
            low = path.name.lower()
            for sdk_name, needles in SDK_FINGERPRINTS.items():
                for needle in needles:
                    if needle.lower() in low:
                        sdk_hits[sdk_name][path.name] += 1
        elif suffix in ARCHIVE_EXTS:
            archives.append(rel)
            low = path.name.lower()
            for sdk_name, needles in SDK_FINGERPRINTS.items():
                for needle in needles:
                    if needle.lower() in low:
                        sdk_hits[sdk_name][path.name] += 1

    vendor_profiles = score_vendor_profiles(sdk_hits)
    primary_profile = choose_primary_profile(vendor_profiles)

    result = {
        "input": str(root),
        "primary_vendor": primary_profile["vendor"] if primary_profile else None,
        "primary_role": primary_profile["role"] if primary_profile else None,
        "primary_profile_reference": primary_profile["reference"] if primary_profile else None,
        "primary_confidence": primary_profile["confidence"] if primary_profile else None,
        "primary_selection_note": (
            "primary requires high-tier package/API evidence; weak tokens alone are never primary"
        ),
        "vendor_profiles": vendor_profiles,
        "sdk_fingerprints": {
            name: hits.most_common(20) for name, hits in sdk_hits.items() if hits
        },
        "top_packages": packages.most_common(80),
        "urls": urls.most_common(200),
        "domains": domains.most_common(200),
        "json_keys": json_keys.most_common(300),
        "xml_ad_strings": xml_strings[:500],
        "string_constants": string_constants[:500],
        "manifest_permissions": manifest_permissions.most_common(200),
        "manifest_components": manifest_components[:300],
        "manifest_meta": manifest_meta[:200],
        "native_libraries": native_libraries[:300],
        "archives": archives[:300],
        "files_with_ad_terms": ad_hits[:300],
        "files_with_ad_ids": id_hits[:200],
        "files_with_risk_terms": risk_hits[:200],
    }

    data = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(data)
    else:
        Path(args.output).write_text(data, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
