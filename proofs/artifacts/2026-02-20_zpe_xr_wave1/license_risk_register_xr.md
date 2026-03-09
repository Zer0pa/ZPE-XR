# License Risk Register (XR Max Wave)

| Resource | License/Gate | Risk | Decision | Claim impact | Evidence |
|---|---|---|---|---|---|
| HOT3D toolkit | CC BY-NC 4.0 (+ MANO constraints) | Commercial publication constraints may apply. | Retained for benchmarking; commercialization risk explicitly tracked. | XR-C001/XR-C002/XR-C005 remain metric-valid with commercialization caveat. | artifacts/2026-02-20_zpe_xr_wave1/max_resource_lock.json |
| HOI-M3 | Public publication endpoint only | Public executable corpus endpoint not confirmed. | IMP-ACCESS logged; synthetic stress path retained. | No automatic claim downgrade from this resource alone. | artifacts/2026-02-20_zpe_xr_wave1/impracticality_decisions.json |
| HO-Cap | Public publication endpoint only | Public executable corpus endpoint not confirmed. | IMP-ACCESS logged; runtime-retarget evidence not promoted. | XR-C007 remains runtime-blocked. | artifacts/2026-02-20_zpe_xr_wave1/impracticality_decisions.json |
| MANO | Registration + non-commercial research terms | Commercial retarget usage unresolved. | IMP-LICENSE logged and tied to runtime commercialization pause. | XR-C007 -> PAUSED_EXTERNAL. | artifacts/2026-02-20_zpe_xr_wave1/impracticality_decisions.json |
| Unity runtime/Meta SDK | Runtime dependency gate | Unity CLI available=False, Meta SDK endpoint available=True. | Hardware/runtime path paused externally. | XR-C007=PAUSED_EXTERNAL. | artifacts/2026-02-20_zpe_xr_wave1/gate_m2_result.json |
