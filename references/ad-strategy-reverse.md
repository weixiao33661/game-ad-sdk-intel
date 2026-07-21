# Ad Strategy Reverse Reference

Use this reference to reconstruct how a game controls ad monetization through SDK code, mediation adapters, remote configs, and client conversion UX.

For OEM architecture differences see `oem-architecture-matrix.md`.

## Identify SDKs and mediation

Search for:

- SDK package prefixes and adapter names: `ad`, `ads`, `mediation`, `adapter`, `reward`, `interstitial`, `splash`, `banner`, `native`, `bidding`, `waterfall`
- Commercial identifiers: `app_id`, `appid`, `placement_id`, `ad_unit_id`, `slot_id`, `pos_id`, `scene_id`, `channel`, `sdk_key`, `tagid`, `codeId`
- Initialization calls: `init`, `initialize`, `setUserId`, `setChannel`, `setConsent`, `setCOPPA`, `setGDPR`, `setPersonalized`, `setAgreePrivacyStrategy`
- Remote config keys: `ad_config`, `strategy`, `waterfall`, `bidding`, `ecpm`, `priority`, `ab`, `experiment`, `group`, `segment`

Record package/class/method and whether evidence is static code, runtime trace, or network config.

Classify roles: primary mediation / primary direct SDK / demand / analytics / residual / noise.

## Reconstruct lifecycle

Map each ad placement through:

1. App/game scene enters an ad-eligible state
2. Client requests or refreshes ad strategy
3. SDK or mediation layer preloads candidates
4. Client checks show conditions: cooldown, daily cap, scene, segment, network, consent, risk flags
5. Ad shows, fails, or falls back
6. Client emits impression/click/close/reward/report events
7. Server updates counters, rewards, attribution, or experiment metrics

Build a table: placement, trigger scene, SDK/network, load method, show method, callback, reward path, evidence.

### Unity bridge pattern

Common path:

`MaxUnityPlugin / Unity sendMessage → GameManager.post_show_* → SDKUtils → OEM/mediation SDK (sometimes via native shell)`

Trace until the final load/show. Do not stop at the first familiar mediation brand in the binary.

## Strategy fields to look for

Common strategy semantics:

- OEM/China IDs: `posId`, `slotId`, `POSITION_ID`, `adPositionId`, `tagid`, `dcid`, `codeId`, `rit`, `bannerSlotId`, `rewardSlotId`, `instSlotId`, `*_unit_id`
- Waterfall/priority: `priority`, `order`, `rank`, `level`, `weight`, `network`, `adapter`, `timeout`
- Bidding/price: `bid`, `ecpm`, `price`, `floor`, `revenue`, `currency`, `precision`, `isBid`, `dspParallelism`
- Frequency: `cap`, `limit`, `daily`, `interval`, `cooldown`, `show_count`, `last_show`, `max`
- Cache/preload: `preload`, `cache`, `ttl`, `expire`, `valid_time`, `pool_size`, `parallel`
- Segmentation: `country`, `region`, `channel`, `version`, `os`, `device_level`, `payer`, `new_user`, `retention_day`
- Experimentation: `ab`, `exp`, `bucket`, `group`, `variant`, `layer`, `tag`
- Reward: `reward`, `coin`, `item`, `callback`, `verify`, `transaction`, `server_side`, `showAward`

Do not assume meaning from the name alone. Correlate with value ranges, code consumers, request/response changes, and event timing.

### Vendor-specific recovery focus

| Primary | Recover |
|---|---|
| Xiaomi mediation | `poslist[].tagid` vs `info[].parameter`; `isBid`/`weight`/`isClosed`; style timeouts |
| OPPO | format×`posId` matrix; native must `onAdShow/onAdClick`; token/bid only with traffic |
| Huawei | test vs prod ids; native template bind fields; consent/RequestOptions |
| Honor | slotId + width/height; express vs self-render; bid loss notify |
| vivo | Unified APIs; privacy before init; banner interval; float-icon frequency notes |

For Xiaomi mediation specifically, treat `tagid` as mediation request key and `info[].parameter` as downstream DSP placement/code ID until proven otherwise.

## Conversion & UX mechanisms (app shell)

High-ARPU games may combine mediation with client-side conversion enhancers. Always scan:

| Mechanism | Static clues | Runtime clues |
|---|---|---|
| Click-also-rewards | click callback sets same flag as reward | showAward/success on click |
| Fake close | rewrite download/CTA text to 关闭; hide skip | view tree; click → market/download |
| Forced store/hap/deeplink | market URI builders; handler chains | startActivity targets |
| Endcard traps | delayed close, secondary offers | timing + click path |
| Sticky banner | delayed showBanner after onCreate | screenshot + timer |
| Preload on close | load called from dismiss | callback order |

Document as competitor behavior with compliance risk notes. Do not provide playbooks to ship deceptive UX.

## Evidence quality

Prefer evidence in this order:

1. Code reads the field and uses it in a clear branch or calculation
2. Multiple traffic samples show the field changing with behavior
3. Runtime traces show the field reaching a specific SDK call
4. Name and surrounding fields suggest a meaning but no consumer is found

Mark confidence as high, medium, or low.

## Strategy questions checklist

Answer in the report:

- Which SDK is the top-level coordinator?
- Which downstream DSPs are integrated but not necessarily active?
- Which placements are actually called by game code?
- Which placements only exist in bundled SDK resources?
- Which IDs are local mediation tags and which are downstream DSP placement/code IDs?
- Which fields control enable/disable, priority, weight, bidding, parallelism, timeout, frequency, cache, and fallback?
- Which callbacks grant game rewards and which only report ad lifecycle events?
- What conversion UX mechanisms exist?
- Which risk signals may bias strategy responses or ad fill?
