# Dynamic validation — hypothesis dispose

## Policy

**Static proposes. Dynamic disposes.**

- Code capability ≠ production strategy.
- When a device is available (adb device, user-provided phone, or existing clean runtime corpus for this package), the **clean minimum dynamic set is MANDATORY** before finalizing show/trigger/reward/primary-DSP conclusions.
- Frida observation and proxy capture remain optional extensions.
- Change **one variable at a time** across clean / root_frida / proxy.

## Claim states

| State | Meaning |
|---|---|
| `hypothesis` | Static or weak evidence only |
| `confirmed` | Dynamic matched expected_if_true (or multi-source proof) |
| `refuted` | Dynamic showed capability unused / opposite behavior |
| `inconclusive` | Tested but insufficient |
| `pending` | Not yet tested |

## Hypothesis record schema

```json
{
  "id": "H001",
  "claim": "reward tagid uses tencent+bytedance+mimo weights 6/6/5",
  "from": "getmedconfig parse / positions_normalized",
  "metric": 8,
  "priority": "P0",
  "playbook": "PB-05",
  "dynamic_test": "clean: open reward 5x; record Activity/adapter",
  "if_fail_next": "check init gate / cache tie-break",
  "ladder_level_reached": "L2",
  "expected_if_true": "mixed or weight-consistent winners; config info[] matches",
  "expected_if_false": "single DSP only; or tag closed/no-fill",
  "result": "confirmed",
  "evidence": ["clean positions_normalized.json", "TT/GDT/MiMo activities"],
  "env": "clean"
}
```

`playbook` / `if_fail_next` recommended for P0; `validate_outputs` warns if missing (does not fail).

## MANDATORY clean minimum set (device available)

Complete all items (or document hard blocker):

1. **Cold start** — splash/fullscreen? foreground Activity
2. **T+10–30s gameplay** — banner appears? position
3. **Rewarded 3–5 attempts** — trigger UX, which DSP Activity, fill/no-fill
4. **Interstitial if entry exists** — 1–2 attempts
5. **Reward outcome matrix** — complete watch / click-only / early close → award?
6. **Callback order** — load → show → click/reward/close via logcat or observation hooks

Optional next:

- Frida: raw `initconfig`/`getmedconfig` or OEM equivalents
- Fake-close: tap label 关闭 → market/hap?
- clean vs root_frida for **risk metric only**

## What must not stay pure hypothesis when device exists

Unless blocked (no fill network, crash loop), try to dispose:

- Primary show path actually used
- Reward success conditions
- Click-also-reward yes/no
- Banner auto timing
- At least one placement’s live DSP identity (Activity/package)
- Whether local slot is requested at all

Frequency caps and server risk may remain hypothesis without longer runs / paired envs.

## Environments

| Env | Use |
|---|---|
| `clean` | Baseline truth for strategy parameters |
| `root_frida` | Parser bodies, callbacks; not baseline alone |
| `proxy` | Wire fields; may change fill — separate column |

## Risk metric rule

Do **not** mark server risk strategy as `confirmed` from a single instrumented session. Need clean contrast or explicit server field proof.

## Protection metric rule

Document detection locations (jadx/IDA). Observation-only on device. No production bypass playbooks.

## Exit artifacts

- Updated `hypotheses[]` with results
- `03_logs/` or referenced clean captures
- Grades promoted `hypothesis` → `confirmed`/`refuted` where earned
- Report metrics 2/3/8 use confirmed language only when disposed
