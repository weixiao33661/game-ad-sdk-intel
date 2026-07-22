# Tooling: jadx-mcp and IDA MCP

## Order (mandatory)

```text
APK / existing decompile
  → 1) jadx-mcp   (always first)
  → 2) native gate?
        → yes: ida-pro-mcp and/or idalib-mcp on selected .so
        → no: skip IDA
  → 3) device available?
        → yes: MANDATORY clean minimum dynamic set (see dynamic-validation.md)
        → no: L1 static only; mark hypotheses
```

Do **not** open every `.so` in IDA. Do **not** start with dynamic hooks before a jadx model + hypothesis backlog.

## 1. jadx-mcp (primary static surface)

Use for:

| Task | Feeds metrics |
|---|---|
| Manifest activities/services/providers/permissions | SDK inventory, download chain |
| Package paths + adapter registration | primary vs demand |
| `strings.xml` / Constants slot & app ids | local units, metric 8 |
| init / load / show / reward / click call chains | metrics 2, 3, 5 |
| Request builders + response parsers | metrics 1, 4, 5 |
| `System.loadLibrary` / `vm_*` / shell entry | native gate |
| UI rewrite / DownloadButton / award bridge | click strategy, conversion |

### jadx must-do checklist

- [ ] Package / version / channel flavor
- [ ] Ad-related Manifest components
- [ ] Primary mediation or direct OEM with package-path evidence
- [ ] Local slot/appId/config URLs
- [ ] Game bridge to ad show (Unity plugin → GameManager → SDK…)
- [ ] Remote config endpoints + parser class names
- [ ] Device fields assembled into requests
- [ ] Reward/click/close callback → game award
- [ ] List of `.so` that may own ad/protection logic
- [ ] **Hypothesis backlog** started (`hypotheses[]`)

**Exit:** Java/Kotlin model good enough to fill draft of all 8 metrics as `hypothesis` or better.

## 2. Native gate → IDA

### Trigger IDA if any of:

1. Ad load/show/frequency decision is only in native/VM shell
2. Request signing/encryption is native
3. Frida/root/maps/integrity checks live in `.so`
4. Java layer is a thin trampoline (`vm_void`, single JNI exports)
5. Critical strings for config/risk only appear in `.so`

### Tool choice

| Tool | When |
|---|---|
| `ida-pro-mcp` | Interactive RE: xrefs, functions, decompile hot paths |
| `idalib-mcp` | Batch/headless: exports, string scan, multiple so triage |

### IDA must-do (when triggered)

- [ ] Identify so name + role (shell / ad / crypto / detect)
- [ ] Map JNI or export → Java caller
- [ ] Document detection or crypto behavior with **address/function**
- [ ] Promote/refute related hypotheses only with so evidence
- [ ] Do **not** write bypass recipes for third-party production controls

**Exit:** `analysis_path.ida_sos[]` filled; metrics 6/7 (and maybe 1/2) updated.

## 3. Device dynamic (MANDATORY when device available)

See `dynamic-validation.md` and `instrumentation-policy.md`.

Static output = proposals. Dynamic = dispose (`confirmed` / `refuted` / `inconclusive`).

**Frida:** default **L-Obs** (print-only) on config/load/show/reward/pre-encrypt.  
If shell scans `/proc/self/maps` or Frida artifacts → **PB-07** (late attach, narrow hooks, then L-Meas on authorized device only, or blocker).  
Never skip clean minimum set just because Frida is blocked.

## 4. Evidence pointers

| Source | Pointer form |
|---|---|
| jadx | `sources/.../File.java` or class.method |
| IDA | `libfoo.so!sub_XXXX` or function name + offset |
| Dynamic | env tag + log/Activity/screenshot/hook name |

## 5. Anti-patterns

- IDA-first on all natives
- Treating adapter registration as live waterfall without dynamic or config proof
- Writing frequency caps as fact from UI strings only
- Declaring server risk rules from a single root session
- Using LLM judge instead of jadx/IDA/device work
