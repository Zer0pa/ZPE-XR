# ZPE XR Wave-1 Master Runbook

## 1. Scope and Lane Lock
- Lane root: `code/`
- Forbidden edit paths:
  - any path outside this repo boundary
  - external sector repos and historical workspace wrappers
- Execution order (hard): Gate A -> Gate B -> Gate C -> Gate D -> Gate E -> Gate M1 -> Gate M2 -> Gate M3 -> Gate M4 -> Gate E-G1 -> Gate E-G2 -> Gate E-G3 -> Gate E-G4 -> Gate E-G5 -> Gate F-G1 -> Gate F-G2 -> Gate E (final adjudication pass).

## 2. Mission and Claims
This run adjudicates PRD claims XR-C001..XR-C007:
- XR-C001: compression ratio >= 10x.
- XR-C002: MPJPE <= 2 mm.
- XR-C003: encode+decode <= 1 ms.
- XR-C004: pose error < 5% at 10% packet loss.
- XR-C005: gesture accuracy >= 95%.
- XR-C006: multiplayer hand-stream <= 40 KB/s for 4-player session.
- XR-C007: Unity roundtrip MPJPE <= 2 mm.

No claim upgrade is allowed without concrete artifact evidence path under:
`proofs/artifacts/2026-02-20_zpe_xr_wave1/`.

Commercialization closure rule:
- If a claim is blocked by hardware/runtime or non-commercial/restricted assets and no commercial-safe open alternative is proven equivalent, mark the claim `PAUSED_EXTERNAL` with command evidence.

## 3. Popper-First Falsification Policy
Before claim promotion, run destructive tests:
- DT-XR-1 malformed packet + sequence corruption.
- DT-XR-2 packet loss + jitter sweep.
- DT-XR-3 gesture confusion/adversarial movement set.
- DT-XR-4 determinism replay on fixed seeds.
- DT-XR-5 bandwidth stress at multiplayer rates.

Claim mapping (falsification-first):
- XR-C001: attempt to falsify with high-motion, high-entropy sequences where compression should degrade.
- XR-C002: attempt to falsify with abrupt trajectory changes and quantization edge cases.
- XR-C003: attempt to falsify with sustained 90 FPS benchmark and P99 latency checks.
- XR-C004: attempt to falsify with 10-30% packet loss and jitter bursts.
- XR-C005: attempt to falsify with lookalike gestures and temporal perturbation.
- XR-C006: attempt to falsify with bursty packets + 4-player traffic model.
- XR-C007: attempt to falsify with Unity adapter serialization/deserialization drift.

## 4. Determinism and Seed Policy
- Global deterministic seeds: `[1103, 2207, 3301, 4409, 5501]`
- Python hash seeding: `PYTHONHASHSEED=0`
- PRNG: `random.Random(seed)` for all synthetic data generation.
- Determinism acceptance: 5/5 hash-consistent runs for codec outputs and core metrics.

## 5. Comparator Integrity Plan
Comparators declared before coding:
- Incumbent baseline comparator: raw OpenXR-like float stream (positions + rotations) at 90 FPS.
- Modern comparator: float16 delta stream with zlib packet compression.

Comparator usage:
- Compression and bandwidth metrics will report vs both comparators.
- If modern comparator implementation diverges from expected semantics, report impact and keep related sub-claims `INCONCLUSIVE`.

## 6. Dataset/Resource Provenance Lock
Primary planned resources:
- HOT3D reference (Meta/ECCV 2024) for dataset parity target.
- OpenXR hand-joint contract (26 joints/hand).
- Unity XR Interaction Toolkit + Netcode/FishNet integration contracts.
- MANO/AvatarPoser references for body-extension design traceability.

Resource fallback protocol (mandatory):
1. Capture failure signature (e.g., network blocked, license-gated asset unavailable).
2. Use nearest viable substitute (deterministic synthetic fixture or interface-level harness).
3. Log substitution and comparability impact.
4. Keep affected items `INCONCLUSIVE` unless equivalence is demonstrated.

## 7. Command Ledger Link
Predeclared command ledger:
- `runbooks/COMMAND_LEDGER.md`

## 8. Expected Artifact Contract
All required outputs will be created in:
`proofs/artifacts/2026-02-20_zpe_xr_wave1/`

PRD mandatory files:
- `handoff_manifest.json`
- `before_after_metrics.json`
- `falsification_results.md`
- `claim_status_delta.md`
- `command_log.txt`
- `xr_compression_benchmark.json`
- `xr_fidelity_eval.json`
- `xr_latency_benchmark.json`
- `xr_packet_loss_resilience.json`
- `xr_gesture_eval.json`
- `xr_bandwidth_eval.json`
- `xr_unity_roundtrip.json`
- `determinism_replay_results.json`
- `regression_results.txt`

Appendix C mandatory files:
- `quality_gate_scorecard.json`
- `innovation_delta_report.md`
- `integration_readiness_contract.json`
- `residual_risk_register.md`
- `concept_open_questions_resolution.md`
- `concept_resource_traceability.json`

Appendix E mandatory files:
- `max_resource_lock.json`
- `max_resource_validation_log.md`
- `max_claim_resource_map.json`
- `impracticality_decisions.json`
- `license_risk_register_xr.md`
- `interaction_stress_report.json`
- `runpod_readiness_manifest.json` (required when any `IMP-COMPUTE`)
- `runpod_exec_plan.md` (required when any `IMP-COMPUTE`)
- `net_new_gap_closure_matrix.json`
- `gate_f_result.json`
- `runpod_requirements_lock.txt`
- `runpod_expected_artifacts.json`

NET-NEW ingestion support files:
- `resource_attempts_log.json`
- `resource_attempts_raw.log`
- `max_resource_probe_summary.json`

## 9. Rollback Criteria
Stop and rollback to last green gate when any occurs:
- Determinism mismatch.
- Uncaught crash in malformed/adversarial runs.
- Latency breach (>1.0 ms combined encode+decode).
- Fidelity breach (>2.0 mm MPJPE).

Rollback action:
1. Revert only failing gate implementation delta.
2. Patch minimal change.
3. Re-run failed gate and all downstream gates.

## 10. Fallback Plan
If external runtime dependencies (SDKs/datasets) are unavailable locally:
- Continue with deterministic, interface-faithful synthetic harnesses.
- Report comparability limits in `concept_resource_traceability.json` and `residual_risk_register.md`.
- Do not over-upgrade affected claims.

## 11. Beyond-Brief Innovation Plan (Predeclared)
Deliver at least two measurable improvements beyond minimum brief:
1. Robustness augmentation: packet-level FEC-style parity frame support and jitter-buffer concealment metrics.
2. Reproducibility augmentation: deterministic replay hashes across seeds + schema-versioned integration contract.

## 12. Gate Runbook Links
- Gate A: `runbooks/RUNBOOK_GATE_A.md`
- Gate B: `runbooks/RUNBOOK_GATE_B.md`
- Gate C: `runbooks/RUNBOOK_GATE_C.md`
- Gate D: `runbooks/RUNBOOK_GATE_D.md`
- Gate E: `runbooks/RUNBOOK_GATE_E.md`
- Gate M1: `runbooks/RUNBOOK_GATE_M1.md`
- Gate M2: `runbooks/RUNBOOK_GATE_M2.md`
- Gate M3: `runbooks/RUNBOOK_GATE_M3.md`
- Gate M4: `runbooks/RUNBOOK_GATE_M4.md`
- Gate E-G1..E-G5: `runbooks/RUNBOOK_GATE_E_APPENDIX.md`
- Gate F-G1..F-G2: `runbooks/RUNBOOK_GATE_F.md`

## 13. Maximalization and NET-NEW Attempt Rules
1. Attempt all Appendix E resource rows for this lane: HOT3D toolkit, HOI-M3, HO-Cap.
2. Allowed impracticality codes only: `IMP-LICENSE`, `IMP-ACCESS`, `IMP-COMPUTE`, `IMP-STORAGE`, `IMP-NOCODE`.
3. Every impractical outcome requires:
   - command evidence,
   - concrete error signature,
   - fallback path,
   - claim-impact note (`PASS`/`INCONCLUSIVE`/`UNTESTED` boundaries).
4. No silent PASS for license-gated paths.
5. If any task is compute-constrained, emit RunPod readiness artifacts and keep unresolved compute-dependent claims `INCONCLUSIVE` unless equivalence is proven.
