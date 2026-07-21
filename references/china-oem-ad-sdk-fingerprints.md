# China OEM Ad SDK Fingerprints

Use this reference before generic analysis when the sample is a China-market game or includes OPPO, Xiaomi, Huawei, Honor, vivo, or their mediation adapters.

Also read `oem-architecture-matrix.md` for architecture differences and false-positive traps.

## Profile routing

First identify the primary ad layer, then read the matching profile:

| Primary evidence | Load profile | Depth card (same layout all five) |
|---|---|---|
| `com.xiaomi.ad.mediation`, `com.miui.zeus.mimo`, `MiMoNewSdk`, `MIMOAdSdkConfig`, `config/union/v1/getmedconfig` | `oem-xiaomi-mimo.md` | `oem-xiaomi-depth.md` |
| `com.opos.mobad`, `com.heytap.msp.mobad`, `MobAdManager`, `mobad_normal`, `PosConfigManager` | `oem-oppo-heytap.md` | `oem-oppo-depth.md` |
| `com.huawei.hms.ads`, `HwAds`, `ads-lite` (HMS coordinate), `NativeAdLoader`, `com.huawei.openalliance.ad` | `oem-huawei-petal.md` | `oem-huawei-depth.md` |
| `com.hihonor.adsdk`, `HnAds`, `HnAdConfig`, `honor_ads_lite`, `ppskit` | `oem-honor-ads.md` | `oem-honor-depth.md` |
| `com.vivo.mobilead`, `VivoAdManager`, `UnifiedVivo*Ad`, `open_ad_*.aar` **with** vivo packages | `oem-vivo-ads.md` | `oem-vivo-depth.md` |

Use evidence scoring, not device brand alone. If an OEM SDK and GDT/Pangle/Kuaishou/AppLovin are both present, treat the OEM or mediation layer as primary only when it has initialization/load evidence; otherwise report multiple candidates.

Keep downstream DSP evidence separate from the primary layer:

- GDT/Pangle/Kuaishou providers or AARs can mean "adapter capability exists".
- Runtime adapter load calls, network domains, or callbacks are required before saying that downstream network is active.
- Xiaomi `tagid/info[].parameter/isBid/dspParallelism` is specific to Xiaomi mediation and must not be copied into OPPO/vivo/Huawei/Honor reports unless the sample actually contains Xiaomi mediation.

## Evidence tiers

| Tier | Counts as | Examples |
|---|---|---|
| high | package path, init API, mediation endpoint, OEM aar name | `com.miui.zeus.mimo`, `HwAds`, `MobAdManager`, `VivoAdManager`, `HnAds` |
| medium | format API clearly under OEM package | `MMRewardVideoAd`, `NativeAdLoader` under hms.ads, `UnifiedVivoBannerAd` |
| low | ambiguous token | bare `com.heytap`, `SplashView`, `AdSlot.Builder`, `open_ad_`, `OneTrack` |

**Rule:** low-tier hits alone must not set `primary_vendor` or mark an OEM `active`.

## Quick fingerprints

| Platform | Static fingerprints | Placement/config terms | Notes |
|---|---|---|---|
| Xiaomi MiMo / Xiaomi mediation | `com.xiaomi.ad.mediation`, `com.miui.zeus.mimo`, `mimo_sdk.aar`, `libmimo_*.so`, `MiMoNewSdk` | `adPositionId`, `tagid`, `dcid`, `poslist`, `info[].parameter`, `isBid`, `isClosed`, `dspParallelism`, `getmedconfig`, `initconfig` | Often mediates MiMo, Tencent/GDT, Pangle/Toutiao. Check `config/union/v1/initconfig` and `getmedconfig`. |
| OPPO / HeyTap ads | `com.opos.mobad`, `com.heytap.msp.mobad`, `MobAdManager`, `PosConfigManager`, `mobad_*.aar` | `posId`, `KEY_BANNER`, `KEY_HOT_SPLASH`, `KEY_INTERSTITIAL_*`, `KEY_NATIVE_*`, `getToken(posId, posType)` | Demo uses module-specific samples; `posId` via `PosConfigManager`. |
| Huawei / Petal Ads | `com.huawei.hms.ads`, `com.huawei.openalliance.ad`, Gradle `com.huawei.hms:ads-lite`, `HwAds` | `slotId`, `banner_ad_id`, `ad_id_reward`, `ad_id_splash`, `AdParam`, `BannerView`, `RewardAd` | Official sample: banner, native, rewarded, interstitial, splash, instream, consent. Prefer package hits over bare `SplashView`. |
| Honor ads | `com.hihonor.adsdk`, `com.hihonor.mcs.lite`, `ppskit`, `honor_ads_lite`, `HnAds`, `HnAdConfig` | `slotId`, `*_unit_id`, width/height, feed template/self-render | Proguard keeps are strong. Size-spec heavy. `AdSlot.Builder` only counts under hihonor packages. |
| vivo ad network | `com.vivo.mobilead`, `VivoAdManager`, `UnifiedVivo*`, `open_ad_*.aar` beside vivo demo | `POSITION_ID`, `SPLASH_POSITION_ID`, `BANNER_POSITION_ID`, `VIDEO_POSITION_ID`, `AdParams.Builder(posId)` | Bundled GDT/KS/Pangle AARs common; residual until runtime. `open_ad_sdk` alone can be Pangle. |
| Tencent GDT / Youlianghui | `com.qq.e.ads`, `GDTSDK.unionNormal`, `gdt_file_path.xml` | `posId`, `placementId`, `UnifiedBanner`, `Rewardvideo` | Often mediation DSP under Xiaomi/vivo aggregators. |
| Pangle / CSJ / Toutiao | `com.bytedance.sdk.openadsdk`, `com.ss.android.socialbase`, `TTAdSdk`, `TTAdNative` | `codeId`, `setCodeId`, `rit`, `TTRewardVideoAd` | Xiaomi adapters may be `ToutiaoAd*Adapter`. AAR name `open_ad_sdk_*` is Pangle, not vivo. |
| Kuaishou | `com.kwad.sdk`, `kssdk-ad-*.aar`, `KsAdSDK` | `posId`, `KsScene.Builder` | Often bundled DSP adapter. |
| AppLovin MAX | `com.applovin`, `MaxUnityPlugin`, `MaxRewardedAd` | MAX ad unit ids | On China OEM channel packs may only bridge into local `GameManager` — verify before calling primary. |

## False-positive denylist

| Weak hit | Do not map alone to |
|---|---|
| `SplashView` | huawei_ads |
| `SplashAd` | huawei_ads without HMS package |
| `BannerView` | any OEM |
| `RewardAd` | huawei_ads without package |
| `AdSlot` / `AdSlot.Builder` | honor_ads or pangle without package path |
| `open_ad_` / `open_ad_sdk` | vivo_ads without `com.vivo.mobilead` |
| `getToken` | oppo bidding strategy |
| bare `com.heytap` low count | oppo ads active |
| `OneTrack` / `com.xiaomi.onetrack` | ad mediation primary |
| layout `tt_*` strings | strategy placements |

## Demo-derived checks

When a demo directory is available, mine it before searching online:

- Gradle/POM: Maven coordinates, repo URLs, AAR names, applicationIds
- Proguard: `-keep` package patterns
- `strings.xml` and Constants: test placement IDs and naming conventions
- Sample Activities/Fragments: ad type → load/show/callback APIs
- `network_security_config.xml` and file providers: download paths / debug posture
- libs/: distinguish primary AAR vs bundled downstream AARs

For OPPO/vivo/Huawei/Honor demos, placement defaults are commonly in Java constants or string resources. For Xiaomi mediation, production strategy is usually server-side (`getmedconfig`); demo still exposes `AdType`/`AdIdSet`/`BudgetSource` vocabulary.

## Xiaomi mediation field model (only if primary)

Two-step config flow:

- `initconfig`: DSP app IDs and global style/timeout values
- `getmedconfig`: placement groups and DSP waterfall/bidding config

Common request fields: `b`, `m`, `av`, `asv`, `ai`, `pn`, `apv`, `apc`, `oaid`, `comd5`

Common response fields: `styleTimeOutConfig`, `callBackDelayTime`, `getDspLimitTime`, `data[].ct`, `poslist[].tagid|dcid|isClosed|isBid|dspParallelism|adTimeout|timeout|extraParameters`, `info[].name|parameter|weight`, blacklist rules

Reporting: `tagid` = mediation request key; `info[].parameter` = real DSP slot/code ID.

## Downstream promotion ladder

`capability (aar)` → `wired (adapter register)` → `configured (strategy lists dsp)` → `active (runtime load/show/domain)`

## Online reference anchors

Use official/vendor pages only as anchors, not substitutes for local evidence.
