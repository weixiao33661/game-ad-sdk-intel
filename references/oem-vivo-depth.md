# vivo Ads — Depth Card

Use when primary = vivo mobile ad SDK. Same section layout as other OEM depth cards.

## 1. Identity

| Item | Value |
|---|---|
| Architecture | **Direct vivo SDK** + often **bundled** GDT/KS/Pangle AARs |
| Demo root markers | `6240-adsdk-open-demo`, `adsdk-open-demo` |
| applicationId | `com.vivo.adnet.demo.app` |
| Primary packages | `com.vivo.mobilead` |
| Primary AARs | `open_ad_*.aar` (vivo) — distinguish from Pangle `open_ad_sdk_*.aar` |
| Bundled (residual until proven) | `GDTSDK.unionNormal*.aar`, `kssdk-ad-*.aar`, `open_ad_sdk_*.aar`, `oaid_sdk_*.aar` |
| Material report | `demo/reports/vivo_ads_sdk_material_report.md` |
| Dynamic corpus | `demo/reports/dynamic/vivo/` (frida logs, screens) |

## 2. Fingerprints (tiered)

**High:** `com.vivo.mobilead`, `VivoAdManager`, `UnifiedVivo`  
**Medium:** `NativeAdParams`, `VivoNativeAd`, `VivoAdError`  
**Low / not primary:** `open_ad_` / `open_ad_sdk` without vivo packages; bare `AdParams.Builder`  

## 3. ID & config model

| Term | Role |
|---|---|
| `MEDIA_ID` | Media/app id style constant |
| `POSITION_ID` / `*_POSITION_ID` | Placement keys (splash/banner/interstitial/native/reward/…) |
| `AdParams.Builder(posId)` | Standard request entry |
| `NativeAdParams.Builder(posId)` | Native/self-render entry |
| `BANNER_AD_TIME` | Local banner interval (demo e.g. related to 15s class constants) |
| Bidding dialog fields | winner/source/package/price inputs — demo level |
| Privacy | `setAgreePrivacyStrategy(true)` **before** init |

## 4. Format matrix (demo)

| Format | Anchors |
|---|---|
| Splash (legacy/unified/pro) | `SPLASH_POSITION_ID`, multiple activities |
| Banner unified | `BANNER_POSITION_ID` |
| Interstitial img/video | `INTERSTITIAL_*`, `VIDEO_INTERSTITIAL_*` |
| Native stream | large/multi/small/none/video layouts |
| Native Pro stream | `layout_pro_stream_*` |
| Native express templates | material-specific position ids; **mix img/video** note in UI |
| Float icon | frequency caveat in code comments (~minutes) |
| Reward video | `VIDEO_POSITION_ID` / unified reward |

## 5. Lifecycle anchors

1. `VivoAdManager.setAgreePrivacyStrategy(true)`  
2. `init(application, adConfig, callback)`  
3. Build `AdParams` / `NativeAdParams` with posId (+ orientation/interval)  
4. `loadAd()` on Unified* or native classes  
5. Ready: `onAdReady` / load success — may return `View`  
6. Show: `showAd()` or add view; native bind + exposure/click  
7. Callbacks: show/click/close/skip/timeOver/reward/`VivoAdError`  

## 6. Bound fields to prioritize

**Request:** posId, orientation, banner interval, privacy flags  
**Response:** ad View; native response object fields (title/images/video/CTA — confirm names in SDK version)  
**Errors:** `VivoAdError` msg/code  
**Bidding demo:** exchange dialog fields  
**Downstream:** only if adapter load/domain proves GDT/KS/Pangle  

## 7. Dynamic probes

- Prefer existing `reports/dynamic/vivo` frida sessions as patterns  
- Hook `AdParams.Builder` / load/show/reward  
- Privacy false vs true  
- Float icon repeated requests for frequency  
- Domain logs to see if bundled DSPs fire  
- Native express mix ratio over N loads  

## 8. Do-not list

- vivo primary from Pangle `open_ad_sdk` AAR name alone  
- “Waterfall partners = GDT+KS+Pangle” from libs/ folder only  
- Skip privacy-before-init when explaining no-fill  
- Xiaomi tagid model  

## 9. Depth status

| Layer | Status |
|---|---|
| Demo static vocabulary | Strong |
| Dynamic frida corpus | **Stronger than other four demos** in this repo |
| Bundled DSP activation | Per-run proof required |
| Production competitor strategy | APK-specific |
