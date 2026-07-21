# Huawei / Petal Ads — Depth Card

Use when primary = Huawei HMS / Petal Ads. Same section layout as other OEM depth cards.

## 1. Identity

| Item | Value |
|---|---|
| Architecture | **Direct HMS ads SDK** |
| Demo root markers | `hms-ads-demo-java` |
| applicationId | `com.huawei.hms.ads.sdk` |
| Primary packages | `com.huawei.hms.ads`, `com.huawei.openalliance.ad` |
| Gradle | `com.huawei.hms:ads-lite`, `ads-consent`, `ads-omsdk` |
| Material report | `demo/reports/huawei_petal_ads_material_report.md` |

## 2. Fingerprints (tiered)

**High:** `com.huawei.hms.ads`, `com.huawei.openalliance.ad`, `HwAds`, `com.huawei.hms:ads-lite`  
**Medium:** `NativeAdLoader`, `InstreamAdLoader`, `RewardAd`/`SplashAd` **under HMS packages**  
**Low / not primary:** bare `SplashView`, `BannerView`, `ads-consent` alone  

## 3. ID & config model

| Term | Role |
|---|---|
| `banner_ad_id` / `ad_id_*` / `slotId` | Placement ids (demo often **official test** ids like `testw6vs28auh3`) |
| `AdParam` | Common request param object |
| `RequestOptions` | Personalization / non-personalized |
| `NativeAdConfiguration` | e.g. multi-image constraints |
| Consent flow | May block loading ads entirely |

Test IDs are **format examples**, not production competitor strategy.

## 4. Format matrix (demo)

| Format | Demo id keys / entry |
|---|---|
| Banner | `banner_ad_id` → `BannerActivity` |
| Native large/small/three/video/image-only/download-btn | `ad_id_native*` + `NativeViewFactory` templates |
| Reward | `ad_id_reward` → `RewardActivity` |
| Splash H/V | `ad_id_splash`, `ad_id_splash_landscape` |
| Interstitial img/video | `image_ad_id`, `video_ad_id` |
| Instream | `instream_ad_id` |
| Bidding splash | `BiddingSplashActivity` |

## 5. Lifecycle anchors

1. `HwAds.init(application)`  
2. Optional consent / protocol dialogs  
3. Build `AdParam` (+ RequestOptions)  
4. Format load: `BannerView.loadAd`, `NativeAdLoader`, `RewardAd.loadAd`, `SplashView`/`SplashAd`, `InstreamAdLoader`  
5. Native bind: title/media/images/CTA/source → `NativeView`  
6. Reward: `show` + `RewardAdStatusListener` (`onRewarded`, close, fail)  
7. Listeners: load success/fail, closed, dismissed  

## 6. Bound fields to prioritize

**Request:** adId/slotId, AdParam, RequestOptions personalized state, orientation  
**NativeAd getters:** title, mediaContent, images, videoOperator, adSource, callToAction  
**Reward:** reward object / onRewarded  
**Measurement:** OM SDK presence (viewability vocabulary)  
**Errors:** load fail codes  

## 7. Dynamic probes

- Consent on vs off vs “do not load ads”  
- Personalized vs non-personalized RequestOptions  
- Native getter dumps on loaded ads  
- Reward callback order  
- Bidding splash traffic only if that path exercised  

## 8. Do-not list

- Primary from `SplashView` string without HMS packages  
- Treat `test*` ids as competitor production units  
- Assume mediation waterfall (this demo is direct SDK)  
- Copy Xiaomi tagid model  

## 9. Depth status

| Layer | Status |
|---|---|
| Demo static + native field model | Strong |
| Consent/personalization gates | Strong statically |
| Bidding/frequency/cache | Weak without traffic |
| Competitor channel packs | Verify HMS actually initialized |
