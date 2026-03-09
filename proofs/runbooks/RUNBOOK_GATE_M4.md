# Gate M4 Runbook: Residual Risk Closure

## Objective
Close or explicitly accept high-severity residual risks with quantified impact.

## Commands (Predeclared)
1. `PYTHONHASHSEED=0 python3 code/scripts/run_gate_m4.py`

## Expected Outputs
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/net_new_gap_closure_matrix.json`
- updated `residual_risk_register.md`

## Fail Signatures
- unresolved high-severity risk without quantified acceptance.
- missing evidence for risk status changes.

## Rollback
- Patch closure matrix logic and rerun M4 + Appendix E gates.

## Fallback
- Keep unresolved items explicitly `OPEN` with IMP coding and evidence.
