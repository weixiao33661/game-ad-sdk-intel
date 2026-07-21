# Golden case: com.wjly.dcxns.mi

Use this to **eval** the skill. An agent with the skill should rediscover these conclusions (or explicitly mark env-limited gaps). Do not copy blindly into other samples.

## Sample

- Package: `com.wjly.dcxns.mi`
- Channel: Xiaomi (`channelId=xiaomi_app`)
- Engine: Unity + Java bridge
- Shell: `CC00000069FF1F720006FF79E49DCF60` VM / native Frida maps check
- Workspace example: `analysis/dcxns`

## Must-find inventory

| id | class |
|---|---|
| xiaomi mediation + mimo | primary_mediation + demand |
| bytedance/pangle | demand_source |
| tencent/gdt | demand_source |
| applovin max unity plugin | residual/bridge → GameManager |
| huawei/vivo/oppo from weak strings | must NOT be active without packages |

## Must-find local units

- APPID `2882303761520480139`
- rewardSlotId `0e3d75824d784b418cb13ccc1ce22fc8`
- bannerSlotId `a640aadac7f8287f6e1a79f4abadc667`
- instSlotId `9fb2f4ea649cd39548a302ae9651b7c8`
- CONFIG_URL zllinks `getGameInitConfig`

## Must-find remote surface

- `config/union/v1/initconfig`
- `config/union/v1/getmedconfig`
- parsers/builders under `com.xiaomi.ad.mediation.sdk`

## Must-find placement strategies (clean extract)

| role | tagid | style | waterfall |
|---|---|---|---|
| reward | `0e3d75824d784b418cb13ccc1ce22fc8` | 82 | tencent `4205448818314827` w6, bytedance `978105104` w6, mimo same-as-tagid w5, isBid true |
| banner | `a640aadac7f8287f6e1a79f4abadc667` | 52 | mimo only w5 |
| interstitial | `9fb2f4ea649cd39548a302ae9651b7c8` | 26 | bytedance `983863002` w6, mimo w5 |

## Must-find triggers (partial)

- Banner: `SDKUtils.onCreate` + 10s delay `BannerUtil.showBanner`
- Reward: `GameManager.post_show_video` → `SDK.showRewardedVideo`
- Interstitial entry exists; pacing may be shelled → unknown OK if probed

## Must-find reward rules

- `onReward` → `showAward(0)`
- `onRewardClicked` → also `showAward(0)`
- close without reward → `showAward(1)`

## Must-find conversion mechanism

- Fake close: hide skip, set DownloadButtonICP text to `关闭`
- Landing: mimarket / hap / deeplink chain

## Must-find risk posture

- Native Frida/maps detection exists
- Mediation requests send brand/model/oaid/package/versions/comd5
- Do not claim full server risk without clean vs root medconfig diff

## Fail criteria for eval

Agent **fails** if it:

1. Ships primary field dict dominated by `tt_appdownloader_*` / flex layout keys
2. Marks Huawei/Vivo active from `SplashView` / `open_ad_` only
3. Reports only local slot ids without DSP `parameter`s for reward
4. Omits click-also-reward or fake-close when code evidence exists in tree
5. Treats AppLovin MAX as primary mediation on this Xiaomi pack
6. Gives weights without saying isBid/load group semantics

## Pass artifacts

- Bound dictionary includes `isBid`, `weight`, `parameter`, `tagid` with consumers
- `strategy_model.json` reward placement matches table above (or newer runtime supersession with evidence)
- One-pager states three-DSP reward bid 6/6/5 and MiMo banner
- Unknowns mention interstitial pacing and/or creative URLs if not captured

## Prior human reports (regression sources)

- `01_reports/ad_sdk_strategy_reverse_report.md`
- `01_reports/ad_sdk_static_deep_report.md`
- `01_reports/ad_strategy_flow.md`
- `01_reports/fake_close_repro_full_report.md`
- `clean_mi10_*/extracted_json/clean_strategy_extract_summary.md`
