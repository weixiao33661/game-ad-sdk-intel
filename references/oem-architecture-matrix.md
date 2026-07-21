# OEM Architecture Matrix (Demo-Grounded)

Use this when classifying China OEM / channel packs. Evidence comes from authorized vendor demos under a local demo corpus (Xiaomi mediation, OPPO MobAd, Huawei Petal, Honor 商推, vivo open ad). **Do not copy one vendor's field model onto another.**

## 1. Five architectures at a glance

| Vendor | Demo role | Coordination model | Local ID name | Where strategy lives | Downstream DSP signs |
|---|---|---|---|---|---|
| **Xiaomi MiMo mediation** | True mediation sample | App → MiMo mediation → MiMo/GDT/Pangle adapters | mediation `tagid` / demo `AdType` IDs | Mostly **server** `initconfig` + `getmedconfig` | GDT/TT providers, `info[].name/parameter/weight`, `BudgetSource` |
| **OPPO / HeyTap MobAd** | Direct OEM ad SDK | App → MobAd (`posId`) | `posId` (+ `posType`) | Mostly **server**; local holds many format-specific posIds | Bidding helpers/`getToken` are **not** full waterfall proof |
| **Huawei / Petal Ads** | Direct HMS ads SDK | App → `HwAds` + format APIs | `adId` / `slotId` (often `test*` in demo) | Server fill; local strings + templates | Consent/OM SDK; bidding splash example only |
| **Honor 商推** | Direct Honor ads (+ optional adapters) | App → `HnAds` + `AdSlot(slotId,w,h)` | `*_unit_id` / `slotId` | Server fill; **size/orientation-heavy** local units | `ads-mediation-adapters`, bundled Pangle AAR = capability until runtime |
| **vivo Ads** | Direct vivo SDK (+ bundled AARs) | App → `VivoAdManager` + Unified APIs | `POSITION_ID` / `posId` | Server fill; local constants + banner interval notes | Bundled GDT/KS/Pangle AARs = residual until load/domain proof |

## 2. What “high conversion strategy” looks like per architecture

| Vendor | Static strategy you can recover | Dynamic-only strategy |
|---|---|---|
| Xiaomi mediation | Adapter matrix, tagid→parameter mapping model, bid vs serial, weights, closed switch, style | Actual `poslist`, fill winner, creative URLs, clean vs instrumented diffs |
| OPPO | Full format matrix (banner/hot splash/interstitial/reward/native/advance/template/native-reward/mix), self-render impression binding | Token/bidding semantics, material URLs, caps/TTL |
| Huawei | Format matrix, native template binding fields, consent/personalization gates, reward listener order | Bid/floor, frequency, production slot strategy |
| Honor | Size-spec unit matrix, template vs self-render feed, reward bundle ids, bid loss notify samples | Real unit fill, adapter routing, prices |
| vivo | Unified vs legacy APIs, native express mix note, float-icon frequency comment, privacy-before-init | Actual downstream mediation order, caps, creatives |

## 3. ID vocabulary (do not mix)

| Term | Typical owner | Meaning |
|---|---|---|
| `tagid` | Xiaomi mediation | Logical placement the game requests |
| `info[].parameter` | Xiaomi mediation → DSP | Real MiMo upId / GDT posId / Pangle codeId |
| `info[].weight` | Xiaomi mediation | Priority / eCPM-like sort key |
| `isBid` / `dspParallelism` | Xiaomi mediation | Parallel bid group vs serial waterfall controls |
| `posId` | OPPO, vivo, GDT, KS | Placement id for that SDK |
| `posType` | OPPO | Placement type for token/request construction |
| `slotId` / `adId` | Huawei, Honor | Placement id; Honor often pairs with width/height |
| `codeId` / `rit` | Pangle/CSJ | Downstream placement |
| `*_unit_id` | Honor demo resources | Per format/size unit placeholders |

## 4. Lifecycle anchors (demo-proven)

### Xiaomi mediation
- Init: `MiMoNewSdk.init(context, appId, appName, MIMOAdSdkConfig, listener)`
- Config: `initconfig` then `getmedconfig` (production games; demo may hide bodies)
- Load/show: `MMAd*` / `AdRepository.loadAds` / `showAd`
- Demo extras: `BudgetSource`, `AdIdSet` release/test/budget maps, parallel/personalized switches

### OPPO MobAd
- Init: `MobAdManager` after privacy/permissions
- Load: format objects with `context + posId + listener`
- Native: must call exposure/click registration on bound views
- Extras: `PosConfigManager` editable posIds, `getToken(posId,posType)`, hot-splash module, bidding result notify helpers

### Huawei Petal
- Init: `HwAds.init(application)`
- Banner/Native/Reward/Splash/Instream/Interstitial dedicated Activities
- Native: `NativeAdLoader` → bind title/media/CTA/source to `NativeView`
- Extras: Consent + RequestOptions personalization; OM SDK; bidding splash sample

### Honor
- Init: `HnAds.init` + lifecycle + `HnAdConfig` (image loader, global reward listener)
- Request: `AdSlot.Builder.setSlotId.setWidth.setHeight`
- Feed: express view **or** self-render + interaction registration
- Extras: bidding loss notification samples; mediation-adapter modules in repo

### vivo
- Privacy: `setAgreePrivacyStrategy(true)` **before** `VivoAdManager.init`
- Load: `AdParams.Builder(posId)` / `NativeAdParams.Builder(posId)` then `loadAd`
- Show: `showAd` or attach returned `View`
- Extras: banner interval; float icon frequency caveat; bidding exchange dialog (demo)

## 5. Downstream DSP classification rules

| Observation | Label |
|---|---|
| AAR/provider only | `capability` / `residual` |
| Mediation adapter registered | `wired_demand` |
| Strategy config lists DSP name + parameter | `configured_demand` |
| Runtime load/show/Activity/domain | `active_demand` |

Never promote bundled GDT/Pangle/KS on vivo/Honor/OPPO demos to “active waterfall” without runtime or explicit adapter load evidence.

## 6. False-positive traps (from real mis-routes)

| Weak hit | Wrong conclusion | Correct handling |
|---|---|---|
| `SplashView` | Huawei | Require `com.huawei.hms.ads` / `HwAds` |
| `AdSlot.Builder` | Honor or Pangle | Disambiguate by package (`hihonor` vs `bytedance`) |
| `open_ad_` / `open_ad_sdk` | vivo primary | Prefer `com.vivo.mobilead` / `VivoAdManager`; Pangle also ships `open_ad_sdk` AARs |
| `getToken` alone | OPPO bidding strategy | Medium at best until request usage |
| bare `com.heytap` | OPPO ads active | Need `mobad` / `MobAdManager` |
| `OneTrack` | Xiaomi ads | Analytics only |
| MAX / AppLovin plugin on `.mi` pack | primary mediation | Often Unity bridge into OEM path |

## 7. Competitor APK routing checklist

1. Score OEM profiles with **high-tier package evidence**.
2. Pick **one primary_layer** (mediation or direct OEM). Others stay candidates.
3. Load only that OEM profile for field semantics.
4. Separately inventory GDT/Pangle/KS/MAX as demand or residual.
5. If Xiaomi mediation primary: recover `tagid` matrix + `info[]` model.
6. If OPPO/vivo/Huawei/Honor primary: recover local pos/slot matrix + format lifecycle; mark server waterfall unknown until traffic.
7. Always run conversion-mechanism scan (click-reward, fake close, store/deeplink) on **game shell**, not only OEM demo patterns.
8. Always env-tag dynamic claims (`clean` / `root_frida` / `proxy`).

## 8. Demo corpus map (local)

| Vendor | Typical folder name markers | Depth card (parity layout) |
|---|---|---|
| Xiaomi | `MediationSDK-open-client`, `mimo-mediation-sample`, `聚合SDK2.5.0` | `oem-xiaomi-depth.md` |
| OPPO | `mob_demo`, `mobad_*`, `AccessGuide` | `oem-oppo-depth.md` |
| Huawei | `hms-ads-demo-java` | `oem-huawei-depth.md` |
| Honor | `商推sdk`, `adsdemo`, `honor_ads_lite` | `oem-honor-depth.md` |
| vivo | `6240-adsdk-open-demo`, `adsdk-open-demo` | `oem-vivo-depth.md` |

When the user points at a demo root, mine Gradle/AAR/Proguard/Constants/strings **before** web docs.

After primary is chosen, load that vendor’s depth card so all five OEMs are analyzed with the **same section depth** (identity, fingerprints, ID model, format matrix, lifecycle, bound fields, probes, do-not, status). Quality gates: `maturity-scorecard.md`.
