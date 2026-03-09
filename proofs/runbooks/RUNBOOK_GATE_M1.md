# Gate M1 Runbook: HOT3D Reproduction Path

## Objective
Execute HOT3D-backed attempt for compression/fidelity/latency reproduction.

## Commands (Predeclared)
1. `set -a; source .env; set +a`
2. `PYTHONHASHSEED=0 python3 code/scripts/run_gate_m1.py`

## Expected Outputs
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/max_resource_lock.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/max_resource_validation_log.md`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/resource_attempts_log.json`

## Fail Signatures
- HOT3D package import/install failure.
- dataset download access denied.
- license gate restriction without acceptance path.

## Rollback
- Patch resource-attempt runner only; preserve prior core gate artifacts.
- Rerun Gate M1 and downstream gates.

## Fallback
- Deterministic synthetic equivalence path with explicit `INCONCLUSIVE` claim impact if HOT3D real corpus is inaccessible.
