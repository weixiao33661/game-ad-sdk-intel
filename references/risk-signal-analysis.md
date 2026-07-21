# Risk Signal Analysis Reference

Use this reference when the task involves risk-control detection, anti-analysis behavior, inconsistent traffic, proxy/root/emulator effects, or SDK integrity checks.

## Boundary

Analyze and document risk-control signals to understand how they affect observed ad strategy and protocol data. Do not provide operational steps to evade third-party production systems, fake real users, defeat anti-fraud, or manipulate ad delivery.

Acceptable outputs:

- Detection signal inventory.
- Evidence of where and how a signal is collected.
- Impact on analysis reliability.
- Controlled validation design for owned or explicitly authorized environments.
- Recommendations for cleaner measurement, such as documenting environment variables and comparing authorized baseline devices.

## Signals to Inventory

Client environment:

- Root, Magisk, su paths, bootloader/debuggable state.
- Emulator, cloud phone, virtual machine, build fingerprints, sensor anomalies.
- Proxy/VPN/TLS interception, user CA store, certificate pinning failures.
- Debugger, Frida, Xposed/LSPosed, ptrace, loaded modules, suspicious ports.
- Repackaging, signature mismatch, installer source, integrity APIs.

Behavior and account:

- Request timing, event order, repeated failures, click/show/reward consistency.
- Account age, login state, payment state, retention day, tutorial progress.
- Network reputation, IP geolocation, ASN, datacenter/proxy hints.

Protocol:

- Explicit flags: `risk`, `safe`, `verify`, `integrity`, `root`, `emulator`, `proxy`, `debug`, `score`.
- Fingerprint hashes, nonce/signature fields, challenge tokens, timestamp skew.
- Server-side deny/no-fill/config downgrade responses tied to environment changes.

## Analysis Method

1. Record the environment before interpreting traffic: device, OS, root/proxy/hook/debug state, app signature, installer, account, IP region.
2. Find signal collection code and endpoints. Record classes, methods, fields, and packet examples.
3. Compare authorized baseline runs with one variable changed at a time.
4. Attribute effects conservatively: "proxy state correlates with no-fill" is not the same as "proxy caused no-fill" until controlled.
5. Explain how each signal may bias ad strategy conclusions, such as lower fill, alternate config, disabled rewards, or extra verification.

## Report Language

Use wording like:

- "检测信号：客户端收集了 X，并在 Y 接口上报。"
- "影响判断：该信号可能导致服务端返回降级策略，需要使用授权基线设备对照。"
- "验证设计：在自有测试环境中固定账号、网络、版本和广告位，仅改变 X，比较响应字段和事件结果。"

Avoid instructions phrased as bypass recipes.
