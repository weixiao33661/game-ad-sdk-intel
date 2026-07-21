# Ad Monetization Model Reference

Use this reference to normalize terminology when analyzing competitor game ad strategy.

## Core Concepts

- **Ad placement / ad unit**: A game-side opportunity to request an ad, such as splash, rewarded, interstitial, banner, native/feed, template, or interactive end card.
- **Mediation**: A layer that routes one game placement to multiple ad networks/DSPs and applies server-side strategy.
- **Waterfall**: Sequential or priority-based loading across networks. Evidence usually appears as order, priority, weight, timeout, and fallback fields.
- **Bidding**: Networks compete by price or score before serving. Evidence often appears as `isBid`, `bid`, `ecpm`, `floor`, `price`, `precision`, `auction`, or parallel loading.
- **Frequency cap**: Rules limiting impressions per user/session/day/scene. Search for `cap`, `limit`, `daily`, `interval`, `cooldown`, `show_count`, `last_show`.
- **Preload/cache**: Loading ads before display. Search for `preload`, `cache`, `ttl`, `expire`, `pool`, `ready`, `loadAndShow`.
- **Reward verification**: Rewarded ads may report local callbacks, server callbacks, transaction IDs, reward amount/type, or verification tokens.
- **A/B and segmentation**: Strategy variations by group, bucket, layer, channel, version, country, region, new user, retention day, payer status, or risk state.

## Strategy Questions

Answer these in the report:

- Which SDK is the top-level coordinator?
- Is the architecture OEM mediation, direct OEM SDK, or third-party mediation (see `oem-architecture-matrix.md`)?
- Which downstream DSPs are integrated but not necessarily active? (capability → wired → configured → active)
- Which placements are actually called by game code?
- Which placements only exist in bundled SDK resources?
- Which IDs are local mediation tags and which are downstream DSP placement/code IDs?
- Which fields control enable/disable, priority, weight, Bidding, parallelism, timeout, frequency, cache, and fallback?
- Which callbacks grant game rewards and which only report ad lifecycle events?
- What client conversion UX exists (click-also-reward, fake close, forced store/deeplink)?
- Which risk signals may bias strategy responses or ad fill?

## Evidence Priorities

Prefer this order:

1. Runtime traffic and callback traces tied to a specific game action.
2. Code path from game UI/Unity bridge to SDK load/show/callback.
3. Resource/config IDs consumed by code.
4. SDK registration or adapter classes.
5. Residual strings/resources with no consumer.

Do not say a placement is "actually used" unless a game call path or runtime evidence exists. Say "SDK capability exists" for adapters/resources without a game entrypoint.

## Reference Anchors

Use official docs only to normalize concepts; local artifacts remain primary evidence:

- IAB Open Measurement SDK: ad measurement and viewability vocabulary.
- Google AdMob Mediation: waterfall and Bidding concepts.
- AppLovin MAX: mediation, waterfall, Bidding, and placement concepts.
- Pangle/GDT/Huawei/OEM docs: ad format and SDK naming conventions.
