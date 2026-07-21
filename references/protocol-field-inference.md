# Protocol Field Inference Reference

Use this reference to build field dictionaries from HAR, JSON, logs, configs, and jadx/apktool output.

## Field dictionary schema

For each request or response field, capture:

- Field path: JSON path or query/header/body key
- Direction: request, response, or event report
- Samples: 2–5 representative values
- Type and range: string, int, float, bool, object, array, enum, timestamp, ID-like, base64-like, hash-like
- Category: see closed set below
- Source: endpoint, packet ID, file/class/method, SharedPreferences key, log tag, or config file
- Producer / consumer logic: where created, transformed, read, or branched on
- Runtime effect: one line
- Suspected meaning, confidence, and env tag if dynamic

### Bound vs candidate

| File / section | Rule |
|---|---|
| Primary request/response dictionary | Row must have consumer **or** multi-sample behavior correlation |
| Candidate list | Unbound but allowlisted / high-frequency near ad packages; cap size |
| Drop | Denylist noise with no parser proof |

A field name alone is never enough.

## Closed category set

Prefer:

`device | user | session | ad_unit | placement | strategy | experiment | risk | attribution | event | reward | network | consent | creative_asset | channel_config | noise | unknown`

| category | Include | Exclude |
|---|---|---|
| `ad_unit` / `placement` | posId, slotId, tagid, codeId, rewardSlotId | random UUID without consumer |
| `strategy` | isBid, weight, floor, cap, timeout, parallelism, isClosed | UI "skip" label |
| `creative_asset` | title, imageUrl, videoUrl, deeplink, packageName, buttonName | default SDK logo asset URLs only |
| `reward` | onReward, reward_verify, showAward, transaction id | unrelated localization containing "reward" |
| `risk` | root/frida/proxy flags that gate ads; server close under hook | merely sending Build.MODEL |
| `noise` | never in primary dict | denylist below |

## Denylist (auto-noise)

Mark noise or drop if matched and not parser-bound:

- UI chrome: `tt_dislike_*`, `tt_appdownloader_*`, `tt_splash_rock_*`, pure button label resources
- Anti-addiction copy (`anti_addiction_*`) unless code gates ad calls on it
- Layout/animation: `flexDirection`, `alignItems`, `translationX`, `scaleX`, density buckets
- Engine serialization: `m_AssemblyName`, `m_ClassName`, `m_Script`
- Generic tokens without parser context: bare `group`, `layers`, `root`, `data`, `status`, `type`, `id`, `url`
- Single/double-letter obfuscation keys until deobfuscated with a parser
- Foreign mediation leftovers on OEM channel packs (`maxsdk_*`, `amazon_aps_*`) unless bridge proven live

## Allowlist boost

Prioritize binding when seen in code or traffic:

- `tagid`, `placement`, `slot`, `posId`, `codeId`, `rit`, `upId`, `unit_id`
- `weight`, `ecpm`, `price`, `bid`, `floor`, `waterfall`, `parallel`, `dspParallelism`
- `isClosed`, `isBid`, `timeout`, `cacheTime`, `ttl`
- `info`, `parameter`, `dsp`, `adn`, `network`
- `reward`, `callback`, `verify`, `showAward`
- `oaid`, `gaid`, `android_id` (legacy caution)
- `comd5`, `configVersion`
- `blacklist`, `whitelist`
- `deeplink`, `landing`, `market://`, `mimarket://`, `hap://`
- close/skip near download button controllers

## Inference techniques

Use multiple samples whenever possible:

- Devices: emulator vs physical, Android versions, locales, networks
- Accounts: guest, new, retained, payer/non-payer if authorized
- Time: first launch, after gameplay, after ad show, after cooldown, next day
- Placements: rewarded, interstitial, splash, banner, native
- Outcomes: fill, no-fill, show, click, close, reward success/failure
- Environments: clean vs root_frida vs proxy (one variable at a time)

Look for:

- Stable identifiers vs session identifiers vs counters vs timestamps
- Booleans/enums aligned with branches
- Encoded blobs: nested JSON, base64, gzip, protobuf-like, encrypted payloads

## Correlation rules

Prefer:

1. Field value read by code and passed to an SDK/API or branch
2. Request field mirrored/transformed in response/event
3. Response field changes behavior after controlled modification in an owned test env
4. Field appears near known placement/strategy/reward keys **and** has a consumer

When evidence is weak, write "疑似" and list missing validation.

## OEM / mediation ID special cases

| Term | Typical owner | Notes |
|---|---|---|
| `posId` | OPPO, vivo, GDT, KS | Identify owner from nearby package imports |
| `slotId` / `adId` | Huawei, Honor | Honor often pairs with width/height |
| `codeId` / `rit` | Pangle/Toutiao | Downstream placement |
| `tagid` | Xiaomi mediation | Logical ad tag |
| `dcid` | Xiaomi mediation | Placement/config group id |
| `parameter` in `info[]` | Xiaomi mediation | Usually downstream DSP slot/code id |
| `isBid` | Xiaomi mediation | Bidding/parallel ranking switch |
| `isClosed` | Xiaomi mediation | Server disabled tag |
| `dspParallelism` | Xiaomi mediation | Parallel DSP load count |
| `style` / `extraParameters` | Xiaomi mediation | Template/creative style hints |
| `getToken(posId,posType)` | OPPO | Suspected bid/verify token until traffic proves |

Do not assign Xiaomi semantics to OPPO/vivo/Huawei/Honor fields.

## Cleaning noisy automated dictionaries

When inheriting large `field_dictionary` dumps:

1. Keep rows under ad/mediation packages with strategy-ish names
2. Drop pure UI string tables into archive
3. Re-parse strategy response models from source
4. Emit bound JSON/MD; leave legacy dumps untouched or archive

## Confidence

Use high / medium / low, and optionally map to:

- high ≈ code consumer + runtime or multi-sample proof
- medium ≈ strong code consumer OR strong multi-sample traffic
- low ≈ name + neighborhood only
