# Xiaomi MiMo Mediation — Depth Card

Use when primary = Xiaomi mediation / MiMo. Same section layout as other OEM depth cards.

## 1. Identity

| Item | Value |
|---|---|
| Architecture | **OEM mediation** (not direct-only) |
| Demo root markers | `聚合SDK2.5.0`, `MediationSDK-open-client`, `mimo-mediation-sample` |
| Demo applicationId | `com.xiaomi.ad.mimo_mediation.demo` |
| Primary packages | `com.xiaomi.ad.mediation`, `com.miui.zeus.mimo` |
| Primary AAR | `mimo_sdk.aar` |
| Analytics often bundled | `com.xiaomi.onetrack` (not demand) |
| Material report | `demo/reports/xiaomi_mimo_mediation_material_report.md` |
| Competitor golden | `com.wjly.dcxns.mi` (channel pack, not demo) |

## 2. Fingerprints (tiered)

**High:** `com.xiaomi.ad.mediation`, `com.miui.zeus.mimo`, `MiMoNewSdk`, `MIMOAdSdkConfig`, `config/union/v1/getmedconfig`, `initconfig`, `mimo_sdk`  
**Medium:** `AdRepository`, `MMRewardVideoAd`, `MMAdSplash`, `MMAdTemplate`  
**Low / not primary:** `OneTrack`, `libmimo_` alone, GDT/TT FileProvider alone  

## 3. ID & config model

| Term | Role |
|---|---|
| appId (init) | Mediation app id |
| Demo `AdType` + `AdIdSet` | Local map: release/test/budget1/budget2 ids per format |
| `BudgetSource` | Demo traffic-source switch |
| Production `tagid` | Logical placement game requests |
| `info[].name` | `mimo` / `tencent` / `bytedance` |
| `info[].parameter` | **Real DSP** upId / GDT pos / Pangle codeId |
| `info[].weight` | Sort / eCPM-like |
| `isBid`, `dspParallelism`, `isClosed` | Load policy switches |
| `extraParameters.style` | Template/style hint |
| `dcid`, `comd5` | Config group / checksum |

**Server pair (production):** `initconfig` → DSP appids + style timeouts; `getmedconfig` → poslist strategy.

**Do not** use `tagid/info[]` names on OPPO/vivo/Huawei/Honor primaries.

## 4. Format matrix (demo)

| Format | Demo anchors |
|---|---|
| Fullscreen interstitial video H/V | `HRO_FULLSCREEN_VIDEO_AD`, `VER_FULLSCREEN_VIDEO_AD` |
| Half interstitial img/video/mix | `HRO_HALF_*`, `VER_HALF_*` |
| Reward video | `REWARD_VIDEO_*`, horizontal/new variants |
| Splash | `SPLASH_AD`, `VER_SPLASH_AD` |
| Banner | `BannerFragment` / menu |
| Template native | `TEMPLATE_AD_2` … `TEMPLATE_AD_13` |
| Feed self-render | `FEED_POS_ID_1/2/3` |

## 5. Lifecycle anchors

1. `MiMoNewSdk.init(context, appId, appName, MIMOAdSdkConfig, listener)`  
2. Optional settings: debug, test env ids, test server, personalized, parallel  
3. Resolve id: `AdConfigManager.getAdId(AdType)` / production tagid  
4. Load: `MMAdSplash|MMRewardVideoAd|MMAdTemplate|…` or `AdRepository.loadAds`  
5. Show: `showAd(activity)` / template show  
6. Callbacks: show / click / dismiss / reward / video complete  

Production load policy: `isBid` → parallel group else serial; `TaskCreateInterceptor` gates non-inited DSPs.

## 6. Bound fields to prioritize

**Request:** brand/model/rom, asv, pn/apv/apc, oaid, ai, comd5  
**Response strategy:** tagid, info[], weight, isBid, isClosed, dspParallelism, timeouts, style, blacklist  
**Creative summary (runtime):** appName, packageName, buttonName (mediation wrapper); full URLs inside DSP bodies  
**Events:** GET_ADS, VIEW, CLICK, CLOSE, REWARDED_CALL, ecpm/weight, triggerId, dcid  

## 7. Dynamic probes

- Hook `initconfig` / `getmedconfig` parsers (raw JSON)  
- Hook `AdRepository.loadAds` + task create (dsp/parameter/weight)  
- Downstream: MiMo `setUpId`, Pangle `setCodeId`, GDT reward ctor  
- Env matrix: clean vs root_frida vs proxy on same tagid  
- Competitor shells: click-also-reward, fake close (not in OEM demo)

## 8. Do-not list

- Call GDT/Pangle active from FileProvider only  
- Treat demo BudgetSource as production waterfall  
- Copy Xiaomi fields into other OEM reports  
- Treat MAX Unity bridge on `.mi` packs as primary without tracing  

## 9. Depth status

| Layer | Status |
|---|---|
| Demo static vocabulary | Strong |
| Production mediation field model | Strong (code + captures on samples like dcxns) |
| Creative full JSON | Weak without DSP response hooks |
| Game-level frequency | Often shelled / Unity — probe separately |
