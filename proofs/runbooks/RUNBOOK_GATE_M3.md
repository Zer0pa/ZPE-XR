# Gate M3 Runbook: Extended Packet-Loss Stress

## Objective
Validate resilience behavior under >30% stress and adversarial interaction sequences.

## Commands (Predeclared)
1. `PYTHONHASHSEED=0 python3 code/scripts/run_gate_m3.py`

## Expected Outputs
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/interaction_stress_report.json`

## Fail Signatures
- uncaught exception in stress runner.
- malformed packet crash.
- stress metric regression vs declared bounds.

## Rollback
- Patch stress simulator and rerun M3+ downstream.

## Fallback
- None; stress execution required locally.
