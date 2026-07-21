# Xiaomi MiMo Mediation Profile

Use this profile when static evidence points to Xiaomi MiMo or Xiaomi mediation as the primary ad layer.

See also: `oem-architecture-matrix.md` (Xiaomi row), full depth card `oem-xiaomi-depth.md`, demo markers `MediationSDK-open-client` / `mimo-mediation-sample` / `聚合SDK2.5.0`.

## Static Fingerprints

- Packages: `com.xiaomi.ad.mediation`, `com.miui.zeus.mimo`, `com.xiaomi.onetrack`.
- SDK files: `mimo_sdk.aar`, `libmimo_*.so`.
- Endpoints: `config/union/v1/initconfig`, `config/union/v1/getmedconfig`.
- APIs/classes: `MiMoNewSdk`, `MIMOAdSdkConfig`, `MMAdSplash`, `MMRewardVideoAd`, `MMAdTemplate`, `AdRepository`.
- Downstream signs: GDT and TT/Pangle providers often appear as adapters, not necessarily as primary SDKs.

## ID And Config Model

- `initconfig`: initializes DSP app IDs and style timeouts.
- `getmedconfig`: returns placement strategy, waterfall/bidding, switches, and downstream DSP IDs.
- `tagid`: mediation logical placement requested by app code.
- `info[].parameter`: downstream DSP placement/code ID.
- `info[].name`: DSP name such as `mimo`, `tencent`, or `bytedance`.
- `isBid`: parallel/bidding-style loading switch.
- `dspParallelism`: number of DSP tasks that may load in parallel.
- `isClosed`: server-side placement close switch.
- `extraParameters.style`: creative/template style hint.

## Lifecycle Anchors

- Init: `MiMoNewSdk.init(context, appId, appName, MIMOAdSdkConfig, listener)`.
- Load: `MMAdSplash.load`, `MMRewardVideoAd.load`, `MMAdTemplate.load`, `AdRepository.loadAds`.
- Show: `showAd(activity)` or SDK-returned template view.
- Reward/callback: `onAdShow`, `onAdClicked`, `onAdDismissed`, `onAdReward`, `onAdVideoComplete`, `MMAdReward`.

## Dynamic Validation

- Hook config parsers and network response handlers around `initconfig` and `getmedconfig`.
- Compare `tagid`, `isClosed`, `isBid`, `dspParallelism`, `info[]`, `weight`, and `style` across clean/root/proxy runs.
- Confirm actual downstream selection by adapter load calls and foreground Activity/package/domain evidence.

## Reporting Notes

- Treat Xiaomi as a mediation layer when `getmedconfig` and adapters are present.
- Do not call GDT/Pangle/Kuaishou active just because providers or AARs exist; require adapter load or network/runtime evidence.
- Do not generalize Xiaomi `tagid/info[]` semantics to other OEMs.
