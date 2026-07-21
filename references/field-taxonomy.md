# Field taxonomy & noise control

## Why this exists

Unbounded string/json-key dumps destroy signal. Agents must classify before publish.

## Closed category enum

Use only these `category` values in bound dictionaries:

| category | Include examples | Exclude examples |
|---|---|---|
| `ad_unit` | rewardSlotId, tagid, placementid, codeId, posId, appid | random UUID without consumer |
| `mediation_strategy` | isBid, weight, dspParallelism, isClosed, getDspLimitTime, style, blacklist, cacheTime | UI "skip" label |
| `dsp_request` | setUpId, setCodeId, ADParams, oaid on ad request body | layout width |
| `creative_asset` | appName, packageName, buttonName, imageUrl, videoUrl, deeplink, landingPageUrl | SDK logo default URL only |
| `event_track` | VIEW, CLICK, CLOSE, REWARDED_CALL, GET_ADS, triggerId, dcid | unrelated analytics |
| `reward_logic` | onReward, reward_verify, showAward, RewardStatus | "reward" in unrelated localization |
| `frequency_cap` | skip_period_limit, daily cap, level interval, timeout used as pacing | anti-addiction playtime copy |
| `risk_signal` | root/frida/maps checks that gate ads; server isClosed under hook | merely reading Build.MODEL |
| `privacy` | TTCustomController flags, personalized ad switch | store listing privacy URL alone |
| `channel_config` | channelId, gameId, CONFIG_URL, DATA_CENTER | |
| `noise` | never in primary bound dict | everything below |

## Primary vs candidate files

| File | Allowed categories | Max guidance |
|---|---|---|
| `field_dictionary_bound.json` | all except `noise` | only bound rows |
| `unbound_field_candidates.json` | any, including noise | cap ~100 high-value suspects; drop chrome |

## Bound row schema

```json
{
  "field": "isBid",
  "category": "mediation_strategy",
  "type": "bool",
  "sample_values": [true],
  "parser": "com.xiaomi.ad.mediation.sdk.qj",
  "consumer": "com.xiaomi.ad.mediation.internal.config.AdRepository.loadAds",
  "runtime_effect": "true → AdParallelLoadTaskGroup; false → AdSerialLoadTaskGroup",
  "evidence": ["jadx/sources/.../AdRepository.java:176"],
  "grade": "B_static_bound",
  "env": null,
  "notes": ""
}
```

## Denylist (auto-noise)

Mark `noise` or drop if matched and no specialized parser proof:

### UI chrome / localization
- `tt_dislike_*`, `tt_appdownloader_*`, `tt_splash_rock_*`, `tt_logo_*`
- `mimo_*_btn_*` pure label resources without strategy reads
- Anti-addiction strings (`anti_addiction_*`) unless code gates ad calls on them

### Layout / animation
- `flexDirection`, `alignItems`, `translationX`, `scaleX`, `constraint*`
- dp buckets: `mdpi`, `xhdpi`, …

### Engine serialization
- `m_AssemblyName`, `m_ClassName`, `m_Script`, `m_ObjectType`
- SayKit GDPR popup copy keys when not ad-frequency related

### Generic single tokens without parser context
- `group`, `layers`, `root`, `data`, `status`, `type`, `id`, `url` (alone)
- Single/double letter obfuscation keys (`ix`, `ty`, `hd`) until deobfuscated with parser

### Foreign mediation leftovers (when channel is OEM)
- `maxsdk_*`, `amazon_aps_*`, `applovin*` keys in assets if runtime path never touches MAX — candidate residual, not active strategy unless bridge proven

## Allowlist boost (always investigate)

If seen in code or traffic, prioritize binding:

- `tagid`, `placement`, `slot`, `codeId`, `posId`, `upId`
- `weight`, `ecpm`, `price`, `bid`, `waterfall`, `parallel`
- `isClosed`, `isBid`, `timeout`, `cacheTime`, `ttl`
- `info`, `parameter`, `dsp`, `adn`, `network`
- `reward`, `callback`, `verify`, `showAward`
- `oaid`, `imei`(legacy), `android_id`, `gaid`
- `comd5`, `md5`, `configVersion`
- `blacklist`, `whitelist`, `floor`
- `deeplink`, `landing`, `market://`, `mimarket://`, `hap://`
- `fake`/`close`/`skip` near download button controllers

## Classification algorithm (agent)

```
for key in discovered_keys:
  if denylist_match(key) and not parser_bound(key):
    drop or candidates[noise]
  elif allowlist_match(key) or parser_bound(key):
    attempt_bind()
    if bound: primary_dict
    else: candidates[suspected_category]
  else:
    only keep if frequency high AND appears near ad packages
```

## Cleaning an existing noisy dictionary

When inheriting `skill_validation_field_dictionary.md`-style tables:

1. Keep rows with path under mediation/ad packages AND strategy-ish names.
2. Drop pure `xml_ad_strings` UI labels wholesale into archive.
3. Re-parse strategy response models from source — do not "guess meaning" for survivors.
4. Emit new bound JSON; leave legacy file untouched or move to `_archive`.

## Confidence vs grade

Do not use floating "high/medium/low" alone. Use evidence **grade** from SKILL.md. Optional `confidence` 0-1 only inside a grade for sorting.
