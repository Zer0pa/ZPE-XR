# Appendix E Runbook: NET-NEW Ingestion and RunPod Readiness

## Objective
Execute E-G1..E-G5 with attempt-all resource probing and impracticality adjudication.

## Commands (Predeclared)
1. `set -a; source .env; set +a`
2. `PYTHONHASHSEED=0 python3 code/scripts/run_appendix_e.py`

## Expected Outputs
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/impracticality_decisions.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/net_new_gap_closure_matrix.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/runpod_readiness_manifest.json` (if any `IMP-COMPUTE`)
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/runpod_exec_plan.md` (if any `IMP-COMPUTE`)

## Fail Signatures
- any E3 resource not attempted.
- missing command evidence for skipped resource.
- license-gated path marked PASS without explicit legal note.

## Rollback
- Patch resource-attempt scripts and rerun Appendix E gates only.

## Fallback
- None for evidence logging; all resources require command-level attempts.
