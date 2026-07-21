# vivo Ads Profile

Use this profile when static evidence points to vivo advertising SDK as the primary ad SDK.

See also: `oem-architecture-matrix.md` (vivo row), full depth card `oem-vivo-depth.md`, demo markers `6240-adsdk-open-demo` / `adsdk-open-demo`. Prefer `com.vivo.mobilead` + `VivoAdManager`. AAR name `open_ad_sdk_*` alone may be Pangle, not vivo. Bundled GDT/KS/Pangle = residual until runtime.

## Static Fingerprints

- Packages: `com.vivo.mobilead`.
- SDK files: `open_ad_*.aar`, `open_ad_sdk_*.aar`.
- APIs/classes: `VivoAdManager`, `AdParams.Builder`, `NativeAdParams.Builder`, `UnifiedVivoBannerAd`, `UnifiedVivoSplashAd`, `UnifiedVivoRewardVideoAd`, `VivoNativeAd`, `VivoAdError`.
- Bundled dependencies may include GDT, Kuaishou, Pangle, and OAID.

## ID And Config Model

- `posId` / `POSITION_ID`: vivo placement ID.
- `AdParams.Builder(posId)`: common standard ad request entry.
- `NativeAdParams.Builder(posId)`: native/self-render request entry.
- Banner interval and orientation fields can be local request constraints.
- Bidding demo fields may include winner/source/package/price-like inputs; treat as example until traffic confirms.

## Lifecycle Anchors

- Privacy/init: `VivoAdManager.getInstance().setAgreePrivacyStrategy(true)` before `init(...)`.
- Load: `loadAd()` on unified banner/splash/reward/interstitial/native classes.
- Show/render: `showAd()` or add returned `View`/native object to app layout.
- Callback: `onAdReady`, `onAdLoadSuccess`, `onAdLoaded`, `onAdShow`, `onAdClick`, `onAdClose`, `onAdSkip`, `onAdTimeOver`, reward callbacks, `VivoAdError`.

## Dynamic Validation

- Compare privacy agreement and personalization states first.
- Hook `AdParams.Builder` and `NativeAdParams.Builder` to map `posId` to ad type.
- For native ads, bind response object fields to actual rendered layout and click/exposure registration.
- Run repeated requests for floating icon/template/native formats because demo notes indicate frequency effects.

## Reporting Notes

- Distinguish vivo primary SDK from bundled GDT/Kuaishou/Pangle dependencies.
- Do not infer active downstream mediation from AAR presence alone.
- Treat fill rate, frequency, material mix, and bidding semantics as dynamic-only unless traffic or SDK callbacks prove them.
