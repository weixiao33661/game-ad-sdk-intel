# Xiaomi mediation quick reference

Use only when inventory shows `com.xiaomi.ad.mediation` / MiMo. Verify line numbers per sample; this is a map, not a substitute for reading the APK.

## Versions

- Observed: mediation SDK `2.5.0` (`asv` request field)

## Endpoints

| API | Typical path | Builder / parser (obfuscated names vary) |
|---|---|---|
| DSP init | `config/union/v1/initconfig` | request `rc`, parse `rb` |
| Placement strategy | `config/union/v1/getmedconfig` | request `qm`, parse `qj` |
| Host | `mediation.ad.xiaomi.com` (confirm in sample) | |

## Request fields (both configs, typical)

`b` brand · `m` model · `av` rom/android · `asv` sdk ver · `pn` package · `apv` versionName · `apc` versionCode (medconfig) · `oaid` · `ai` appId · `comd5` config hash

## initconfig response (typical)

- `code`, `message`, `comd5`
- `data[].name` + `data[].appid` → bytedance/tencent/…
- `styleTimeOutConfig` map by style
- `callBackDelayTime`

## getmedconfig response (typical)

- `getDspLimitTime` → global task timeout
- `data[].ct=1` → `app.poslist[]`
- `data[].ct=2` → `app.blacklist[]`
- poslist item: `dcid`, `tagid`, `isClosed`, `isBid`, `dspParallelism`, `adTimeout`, `timeout`, `extraParameters`, `info[]`
- info item: `name`, `parameter`, `weight`

## Load core

- Entry: `AdRepository.loadAds(context, tagId, adType, triggerId, config, listener)`
- `isClosed` → `LOAD_TAG_ID_CLOSED (-900)`
- `isBid` true → `AdParallelLoadTaskGroup` else `AdSerialLoadTaskGroup`
- `info[].parameter` → `adInternalConfig.adPositionId`
- `info[].weight` → task priority / cache ordering
- `TaskCreateInterceptor` gates bytedance/tencent until init flags true; mimo usually allowed

## Ad type constants (px.*)

| field | type |
|---|---|
| c | feed |
| d | reward video |
| e | splash |
| f | banner |
| g | full screen interstitial |
| h | template |

## Downstream mapping

| DSP name in info[] | Adapter pattern | Placement field |
|---|---|---|
| mimo | `MiMoAd*Adapter` | `ADParams.setUpId` |
| bytedance / toutiao | `ToutiaoAd*Adapter` | `AdSlot.setCodeId` |
| tencent | `TencentAd*Adapter` | GDT constructor pos id |

## Cache notes

- Config cache often under app files `mi_mediation_sdk_files/config.json` and `dspapi_config.json`
- Cache selection may tie-break toward MiMo on equal weight — verify `qf` (name varies)

## Local app shell (channel games)

Many `.mi` Unity games:

- `com.android.common.SDK` / `SDKUtils` / `GameManager`
- Native VM shell so for show/frequency
- Publisher BFF e.g. `openapi.zllinks.com` for `getGameInitConfig` + ad-callback
- Local `rewardSlotId` / `bannerSlotId` / `instSlotId` = mediation tagids

## Reward bridge pattern to verify

- `onReward` → award success
- `onRewardClicked` → sometimes also award success (competitor conversion choice)
- `onAdDismissed` without reward → award fail

## Conversion tricks seen on MiMo path

- Hide `mimo_reward_skip`
- Rewrite `DownloadButtonICP` text to `关闭`
- Click path → market / hap / deeplink handlers

Treat as P5 findings with static+runtime evidence.

## Style codes (empirical; confirm)

| style | often |
|---|---|
| 82 | reward |
| 52 | banner |
| 26 | interstitial |
| 81/41/42/115/118/… | other inventory; do not invent roles |

## What still needs sample-specific work

- Exact host/path if obfuscated differently
- Full creative JSON inside MiMo/Pangle/GDT responses
- Unity-side frequency
- Whether server changes poslist under root/proxy
