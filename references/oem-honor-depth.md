# Honor Ads (商推) — Depth Card

Use when primary = Honor ads / 商推 SDK. Same section layout as other OEM depth cards.

## 1. Identity

| Item | Value |
|---|---|
| Architecture | **Direct Honor ads** + optional mediation-adapter modules |
| Demo root markers | `商推sdk`, `adsdemo`, `honor_ads_lite` |
| applicationId | `com.hihonor.adsdk.union.demo.external` |
| Primary packages | `com.hihonor.adsdk`, `com.hihonor.mcs.lite`, `ppskit` |
| Modules | `ads-banner`, `ads-splash`, `ads-reward`, `ads-interstitial`, `ads-picture-text`, `ads-mediation-adapters`, `aggregation-access` |
| Material report | `demo/reports/honor_ads_sdk_material_report.md` |

## 2. Fingerprints (tiered)

**High:** `com.hihonor.adsdk`, `HnAds`, `HnAdConfig`, `honor_ads_lite`, `ppskit`  
**Medium:** `ads-mediation-adapters`, `aggregation-access`, `com.hihonor.mms.ads`  
**Low / not primary:** `AdSlot.Builder` without `com.hihonor.*` path (collides with Pangle)  

## 3. ID & config model

| Term | Role |
|---|---|
| `slotId` / `*_unit_id` | Placement; demo often placeholder `****` until filled |
| `AdSlot.Builder.setSlotId.setWidth.setHeight` | **Size is first-class** with id |
| Feed unit ids | Large/small/three/app/h-video/v-video etc. |
| Bidding notify | win/loss, reason (`LOW_PRICE`), source (`CSJ`) — sample level |
| Reward callback bundle | `reqId`, `adUnitId` |

## 4. Format matrix (demo)

| Format | Notes |
|---|---|
| Banner default / gallery | Multiple resolutions e.g. 1080×180, 1280×720… |
| Splash img/video H/V | Size-named unit ids |
| Reward H/V | Size-named unit ids |
| Interstitial img/video H/V | Size-named unit ids |
| Feed template render | `getExpressAdView()` |
| Feed self-render | title/images/video/download/close/ad-flag holders |
| App install feed | download button holders |

**Parity note:** Honor is **size/orientation heaviest** among five.

## 5. Lifecycle anchors

1. `HnAds.get().initActivityLifecycle` + `init(context, HnAdConfig)`  
2. Config: image loader, global `HnRewardListener`  
3. Permissions / startSource as demo requires  
4. `AdSlot.Builder` slotId + width/height  
5. Type loaders: banner/splash/reward/interstitial/picture-text  
6. Express: add returned view; self-render: bind + `registerViewForInteraction`  
7. Optional bidding loss notification  
8. Reward listener with req/ad unit ids  

## 6. Bound fields to prioritize

**Request:** slotId, width, height, orientation  
**Express:** expressAdView  
**Self-render:** title, images[], customVideo, adFlag, adCloseFlag, download button  
**Bidding sample:** winPrice, lossReason, biddingSrc  
**Reward:** reqId, adUnitId  

## 7. Dynamic probes

- Real unit ids (placeholders won’t fill)  
- Same creative family across different WxH slots  
- Express vs self-render parity  
- Whether mediation-adapters/Pangle AAR actually load  
- Bid notify on wire  

## 8. Do-not list

- Honor primary from bare `AdSlot.Builder` in bytedance packages  
- Call bundled Pangle “active waterfall” without runtime  
- Ignore width/height when reporting slot strategy  
- Xiaomi tagid vocabulary  

## 9. Depth status

| Layer | Status |
|---|---|
| Demo size matrix + render modes | Strong |
| Aggregation adapters | Capability until runtime |
| Production fills | Needs valid units + traffic |
| Game shell conversion | Scan APK separately |
