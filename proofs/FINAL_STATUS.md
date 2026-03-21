# Final Status

This document is the current staged reading of the XR evidence boundary.

## Claim Status

| Claim | Current staged reading | Anchor | Notes |
|---|---|---|---|
| `XR-C001` | PASS | `proofs/artifacts/2026-03-20_zpe_xr_wave1_live/xr_compression_benchmark.json` | `24.277x` compression vs raw on fresh root rerun |
| `XR-C002` | PASS | `proofs/artifacts/2026-03-20_zpe_xr_wave1_live/xr_fidelity_eval.json` | `0.884 mm` MPJPE on the frozen synthetic lane |
| `XR-C003` | PASS | `proofs/artifacts/2026-03-20_zpe_xr_wave1_live/xr_latency_benchmark.json` | `0.067 ms` average encode+decode latency |
| `XR-C004` | PASS | `proofs/artifacts/2026-03-20_zpe_xr_wave1_live/xr_packet_loss_resilience.json` | `1.633%` pose error at `10%` packet loss |
| `XR-C005` | PASS | `proofs/artifacts/2026-03-20_zpe_xr_wave1_live/xr_gesture_eval.json` | synthetic gesture corpus only |
| `XR-C006` | PASS | `proofs/artifacts/2026-03-20_zpe_xr_wave1_live/xr_bandwidth_eval.json` | modeled multi-player bandwidth only |
| `XR-C007` | `PAUSED_EXTERNAL` | `proofs/artifacts/2026-03-20_zpe_xr_phase2_pre_runpod/phase2_runtime_probe_matrix.json` | runtime closure is still blocked by editor/device/license constraints |

## Comparator Boundary

- Ultraleap row: bounded PASS under close transport semantics.
- Photon row: OPEN because the documented compressed path is narrower in semantics and smaller in bytes/frame.
- Modern comparator on ContactPose is now closed as a negative public-release result: the Phase 5 multi-sequence lane passed the sovereign raw-vs-quality checks, but the modern-comparator row failed `0/5` sequences with ratios between `0.832x` and `0.835x` vs ZPE.

## Corpus Boundary

- ContactPose Phase 4 single-sequence lane: `PASS` at `proofs/artifacts/2026-03-21_zpe_xr_phase4_runpod_contactpose_124835Z/phase4_contactpose_benchmark.json` with `56.144x` compression vs raw, `0.478 mm` MPJPE, `0.025 ms` combined latency, and `0.399%` pose error at `10%` loss.
- ContactPose Phase 5 multi-sequence lane: `PASS` at `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json` with mean `56.144x` compression vs raw, mean `0.479 mm` MPJPE, mean `0.026 ms` combined latency, and mean `0.399%` pose error at `10%` loss across `mug`, `bowl`, `camera`, `binoculars`, and `ps_controller`.
- Exact PRD corpus: `UNRESOLVED`.

## Current Verdict

- outward-safe workload: ContactPose `PASS`
- package candidate: wheel build, `twine check`, and fresh-venv install `PASS`
- cold-start trust: `PASS`
- strongest supported surface: private/internal CPU-native deterministic XR hand-pose transport codec package with bounded real-data advantage versus raw
- outward channel: `PRIVATE_ONLY`
- public release readiness: `NOT_READY_FOR_PUBLIC_RELEASE`

## Why Public Release Failed

- Phase 5 fixed the Comet lineage gap with experiment key `0e957cb027364d36880f6962fd70b78f`.
- Phase 5 did not clear the governing public-release comparator gate: modern comparator passes were `0/5`.
- Public comparator-displacement or incumbent-outperforming language remains out of bounds.
