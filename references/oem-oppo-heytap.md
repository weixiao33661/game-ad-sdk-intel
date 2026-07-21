# OPPO / HeyTap MobAd Profile

Use this profile when static evidence points to OPPO/HeyTap MobAd as the primary ad SDK.

See also: `oem-architecture-matrix.md` (OPPO row), full depth card `oem-oppo-depth.md`, demo markers `mob_demo` / `mobad_*` / `AccessGuide`. Do not apply Xiaomi `tagid/info[]` semantics here.

## Static Fingerprints

- Packages: `com.opos.mobad`, `com.heytap.msp.mobad`, `com.heytap`.
- SDK files: `mobad_*.aar`, `mobad_normal_pub_*.aar`, OAID dependencies.
- APIs/classes: `MobAdManager`, `PosConfigManager`, `NativeAd`, `NativeAdvanceAd`.
- Common modules: demo projects often split banner, hot splash, interstitial, native, template, and reward modules.

## ID And Config Model

- `appId`: OPPO MobAd application ID.
- `posId`: OPPO ad placement ID; usually the key local field.
- `posType`: placement/ad type for token or request construction.
- `getToken(posId, posType)`: token generation for placement verification or bidding-style server coordination; report as suspected until traffic confirms impact.
- `PosConfigManager`: demo helper that persists editable `posId` values in preferences.

## Lifecycle Anchors

- Init: app helper calls `MobAdManager` after privacy/permission setup.
- Load: construct ad object with `context + posId + listener` or ad-type-specific config.
- Show/render: SDK activity/view for splash/banner/reward/interstitial, or app layout for native self-render.
- Native fields: title, icon/image/logo, CTA, privacy/download fields, interaction binding.

## Dynamic Validation

- Capture requests for each `posId` and compare error/fill/callback order.
- Hook ad object constructors and listener callbacks to bind `posId` to actual ad type.
- Track `getToken` input/output and only assign meaning after observing request usage.

## Reporting Notes

- Distinguish demo-editable test `posId` from production app-owned placement IDs.
- Treat OPPO material URLs, landing pages, and server strategy as runtime-only unless captured.
- Do not infer waterfall or bidding from `getToken` alone.
