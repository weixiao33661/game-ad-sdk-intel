# Honor Ads Profile

Use this profile when static evidence points to Honor Ads or Honor commercial promotion SDK as the primary ad SDK.

See also: `oem-architecture-matrix.md` (Honor row), full depth card `oem-honor-depth.md`, demo markers `商推sdk` / `adsdemo` / `honor_ads_lite`. `AdSlot.Builder` only counts under `com.hihonor.*` packages. Size/orientation unit IDs are first-class.

## Static Fingerprints

- Packages: `com.hihonor.adsdk`, `com.hihonor.mcs.lite`, `com.hihonor.mms.ads`, `ppskit`.
- Dependencies/modules: `honor_ads_lite`, `honor_ads_tools`, `ads-banner`, `ads-splash`, `ads-reward`, `ads-interstitial`, `ads-picture-text`, `ads-mediation-adapters`, `aggregation-access`.
- APIs/classes: `HnAds`, `HnAdConfig`, `AdSlot.Builder`, `BannerAdLoad`, picture-text express/self-render classes.
- Proguard keep rules are strong fingerprints.

## ID And Config Model

- `slotId` / `*_unit_id`: Honor placement IDs, often separated by ad type, orientation, and material size.
- `AdSlot.Builder.setSlotId().setWidth().setHeight()`: placement plus size constraint.
- Feed/picture-text unit IDs separate large image, small image, three-image, app, horizontal video, vertical video, template, and self-render modes.
- Bidding APIs may include win/loss notification, source, reason, and price-like values.

## Lifecycle Anchors

- Init: `HnAds.get().initActivityLifecycle(...)` and `HnAds.get().init(context, HnAdConfig)`.
- Load: ad-type load helpers such as banner, splash, reward, interstitial, picture-text.
- Render: `getExpressAdView()` for template; self-render binds title/images/video/download/close/ad-flag fields.
- Reward: global or configured `HnRewardListener`, with request/ad-unit identifiers in callback data.

## Dynamic Validation

- Record permission, lifecycle, and image loader state before comparing results.
- Compare slot IDs by size/orientation to confirm server-side material matching.
- For bidding examples, capture notification calls and traffic before assigning price/loss semantics.

## Reporting Notes

- Honor profile is size/specification heavy; report width/height and orientation alongside placement ID.
- Treat `ads-mediation-adapters` as possible aggregation evidence, not proof of a specific downstream DSP without runtime evidence.
