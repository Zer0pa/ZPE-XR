# Gate B Runbook: Core Codec + Baseline Fidelity/Latency

## Objective
Implement codec and evaluate compression, fidelity, latency.

## Commands (Predeclared)
1. `PYTHONHASHSEED=0 python3 code/scripts/generate_fixtures.py`
2. `PYTHONHASHSEED=0 python3 code/scripts/run_gate_b.py`

## Expected Outputs
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/xr_compression_benchmark.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/xr_fidelity_eval.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/xr_latency_benchmark.json`

## Fail Signatures
- Compression ratio < 10x.
- MPJPE > 2 mm.
- encode+decode latency > 1 ms.

## Rollback
- Revert codec changes in `code/src/zpe_xr/codec.py`.
- Re-run Gate B after quantization/packet patch.

## Fallbacks
- If vectorized path unavailable, use deterministic scalar path and record throughput impact.

## Gate PASS Criteria
- XR-C001, XR-C002, XR-C003 each pass with evidence files.
