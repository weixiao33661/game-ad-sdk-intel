# Huawei / Petal Ads Profile

Use this profile when static evidence points to Huawei HMS/Petal Ads as the primary ad SDK.

See also: `oem-architecture-matrix.md` (Huawei row), full depth card `oem-huawei-depth.md`, demo marker `hms-ads-demo-java`. Require `com.huawei.hms.ads` / `HwAds` — bare `SplashView`/`BannerView` is not enough.

## Static Fingerprints

- Packages: `com.huawei.hms.ads`, `com.huawei.openalliance.ad`.
- Dependencies: `com.huawei.hms:ads-lite`, `ads-consent`, `ads-omsdk`.
- APIs/classes: `HwAds`, `AdParam`, `BannerView`, `NativeAdLoader`, `NativeAd`, `RewardAd`, `SplashView`, `SplashAd`, `InstreamAdLoader`.

## ID And Config Model

- `adId` / `slotId`: Huawei placement ID from `strings.xml` or code.
- `AdParam`: common request parameter object.
- `RequestOptions`: privacy and personalization request options.
- Native config: multi-image/video/media constraints can be set through native ad configuration APIs.
- OM SDK and consent dependencies affect measurement and personalization interpretation.

## Lifecycle Anchors

- Init: `HwAds.init(application)`.
- Banner: `BannerView.loadAd(adParam)`.
- Native: `NativeAdLoader.Builder(context, adId).loadAd(...)`, then bind `NativeAd` to `NativeView`.
- Reward: `new RewardAd(context, adId)`, `loadAd`, `show(activity, RewardAdStatusListener)`.
- Splash/Instream: `SplashView.load`, `SplashAd.loadAd`, `InstreamAdLoader`.

## Dynamic Validation

- Compare consent and personalization states before interpreting fill/material changes.
- For native ads, hook or log `NativeAd` getters: title, media, images, source, CTA, video operator.
- For reward, record `onRewarded`, close, show-fail, and video-complete order.

## Reporting Notes

- Huawei demo placement IDs are often official test IDs; treat them as format examples, not production strategy.
- Native object fields are high-confidence semantic anchors even without packet field names.
- Bidding and frequency usually need runtime traffic; static demo code is insufficient.
