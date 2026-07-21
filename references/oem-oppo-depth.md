# OPPO / HeyTap MobAd — Depth Card

Use when primary = OPPO/HeyTap MobAd. Same section layout as other OEM depth cards.

## 1. Identity

| Item | Value |
|---|---|
| Architecture | **Direct OEM ad SDK** (not Xiaomi-style tagid mediation) |
| Demo root markers | `mob_demo`, `mobad_*`, `AccessGuide` |
| Demo packages | `com.opos.mobaddemo` (+ module apps) |
| Demo AppID | `12132` |
| Primary packages | `com.opos.mobad`, `com.heytap.msp.mobad` |
| Primary AAR | `mobad_normal_pub_*.aar` + `oaid_sdk_*.aar` |
| Material report | `demo/reports/oppo_ads_sdk_material_report.md` |

## 2. Fingerprints (tiered)

**High:** `com.opos.mobad`, `com.heytap.msp.mobad`, `MobAdManager`, `mobad_normal`  
**Medium:** `PosConfigManager`, `NativeAdvanceAd`, `POS_TYPE`  
**Low / not primary:** bare `com.heytap`, `getToken` alone  

## 3. ID & config model

| Term | Role |
|---|---|
| `APP_ID` | MobAd application id |
| `posId` | **Primary placement key** per format/size |
| `posType` | Type enum for token / request construction |
| `PosConfigManager` | Demo editable posId store (SharedPreferences) |
| `getToken(posId, posType)` | Suspected bid/verify token — **medium until traffic** |
| Bidding helpers | `BiddingUtils` / `DemoBiddingUtils.notifyResult` — demo coordination, not proof of full waterfall |

No `tagid/info[].parameter` model unless Xiaomi mediation also present.

## 4. Format matrix (demo)

| Format | Example posId keys (Constants) |
|---|---|
| Banner | `BANNER_POS_ID` (e.g. `4386568`) |
| Splash / land splash | `SPLASH_POS_ID`, `LAND_SPLASH_POS_ID` |
| Hot splash | `app_hotsplash` module |
| Interstitial img H/V | `INTERSTITIAL_*_POS_ID` |
| Interstitial video H/V | `INTERSTITIAL_VIDEO_*_POS_ID` |
| Reward video | `REWARD_VIDEO_POS_ID` (e.g. `4386584`) |
| Native self-render sizes | `NATIVE_512X512_*`, `640X320_*`, `320X210_*`, group |
| Native Advance | mix / vertical / video series |
| Native template | templets + float + info-stream + post layouts |
| Native reward | download/open reward scenes |
| Mix | banner + interstitial combo |

**Parity note:** OPPO demo is **format/spec richest** among five for native.

## 5. Lifecycle anchors

1. Privacy/permissions → `InitUtils` / `MobAdManager` init with AppID  
2. Read `posId` (Constants or PosConfigManager)  
3. Construct format ad (`BannerAd`, `RewardVideoAd`, `NativeAd`, `NativeAdvanceAd`, …)  
4. `loadAd()` / sometimes `loadAdWithData(reqTransport)`  
5. Ready → `showAd()` or bind `INativeAdData` into layout  
6. **Native must** call exposure/click registration (`onAdShow` before `onAdClick`)  
7. Reward: `onReward` / `onRewardFail` (+ native reward variants)  
8. Optional: `getToken`, bidding result notify  

## 6. Bound fields to prioritize

**Request/local:** appId, posId, posType, splash params (orientation, skip areas), banner transport  
**Native response object (`INativeAdData`):** title, desc, iconFiles, imgFiles, logoFile, clickBnText, media bind  
**Errors:** `NativeAdError` / fail codes (demo logs saw `1003` no-fill)  
**Bidding (suspected):** token, win/loss/timeout notify  

## 7. Dynamic probes

- Constructor + listener hooks per posId → bind type  
- Compare fill/error/callback order across posIds (≥10 tries each in research plans)  
- Trace `getToken` into actual requests before calling it strategy  
- OAID presence on wire  
- Hot splash cold/hot triggers  

## 8. Do-not list

- Infer server waterfall from `getToken` alone  
- Treat demo-editable posIds as production competitor strategy  
- Apply Xiaomi `isBid/info[]` vocabulary  
- Mark bare `com.heytap` as ads primary  

## 9. Depth status

| Layer | Status |
|---|---|
| Demo static vocabulary / native specs | Strong |
| Production competitor waterfall | Needs APK+traffic |
| Token/bidding semantics | Medium static, needs capture |
| Game shell conversion tricks | Not in demo — scan APK shell |
