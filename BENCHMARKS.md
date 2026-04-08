# Benchmarks

This file keeps the current reproducible benchmark rows for the canonical `ZPE-XR` repo.

It does not upgrade the release gate. The modern comparator verdict remains `0/5`, and the repo remains `PRIVATE_ONLY`.

## Methodology

- ContactPose single-sequence anchor: `python code/scripts/run_phase4_contactpose_benchmark.py`
- ContactPose multi-sequence authority: `python code/scripts/run_phase5_contactpose_multi_sequence.py`
- ContactPose roundtrip example: `python examples/contactpose_roundtrip.py`
- Streaming latency example: `python examples/streaming_demo.py`
- WebSocket path example: `python examples/websocket_bridge.py`
- InterHand2.6M bilateral stress test: `python code/scripts/run_interhand_benchmark.py --artifact-dir proofs/artifacts/2026-04-08_zpe_xr_phase3_interhand_realdata --max-sequences 3 --min-frames 90`
- Dataset access probe receipt: `proofs/artifacts/2026-04-08_zpe_xr_phase3_dataset_access/dataset_access_status.md`

## Metric Table

| dataset | metric | value |
|---------|--------|-------|
| ContactPose | compression ratio | `56.144x` |
| ContactPose | MPJPE (mm) | `0.479` |
| ContactPose | encode+decode latency (ms) | `0.026` |
| ContactPose | modern comparator gate | `0/5` |

## Dataset Rows

| dataset | joints | frames | ratio | MPJPE (mm) | combined latency (ms) | source |
|---------|--------|--------|-------|------------|-----------------------|--------|
| ContactPose (Phase 5 multi-sequence) | `52` | `3500` | `56.144x` | `0.479` | `0.026` | `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.md` |
| ContactPose (Phase 4 single-sequence) | `52` | `90` | `56.144x` | `0.478` | `0.025` | `proofs/artifacts/2026-03-21_zpe_xr_phase4_runpod_contactpose_124835Z/phase4_contactpose_benchmark.md` |
| InterHand2.6M (Phase 3 real-data) | `52` | `2828` | `4.244x` | `0.620` | `0.091` | `proofs/artifacts/2026-04-08_zpe_xr_phase3_interhand_realdata/phase3_interhand_benchmark.md` |

## Dataset Access Status

| dataset | status | evidence |
|---------|--------|----------|
| ContactPose full corpus expansion | blocked | `proofs/artifacts/2026-04-08_zpe_xr_phase3_dataset_access/dataset_access_status.md` |
| GRAB benchmark lane | blocked | `proofs/artifacts/2026-04-08_zpe_xr_phase3_dataset_access/dataset_access_status.md` |
| InterHand2.6M bilateral benchmark | complete | `proofs/artifacts/2026-04-08_zpe_xr_phase3_interhand_realdata/phase3_interhand_benchmark.md` |

## Gate Note

- Modern comparator gate: `0/5`
- Public release posture: `PRIVATE_ONLY`
- Photon remains a secondary open comparator row
- InterHand2.6M bilateral stress test is now anchored in repo artifacts
- ContactPose full-corpus expansion and GRAB remain blocked on current public access conditions
