# Gate F Runbook: Commercialization and Closure Adjudication

## Objective
Close open `FAIL`/`INCONCLUSIVE` claims to `PASS`, `FAIL`, or `PAUSED_EXTERNAL` with explicit evidence under Appendix F.

## Commands (Predeclared)
1. `set -a; source .env; set +a`
2. `PYTHONHASHSEED=0 python3 code/scripts/run_gate_f.py`
3. `PYTHONHASHSEED=0 python3 code/scripts/run_gate_e.py`

## Expected Outputs
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/gate_f_result.json`
- updated `proofs/artifacts/2026-02-20_zpe_xr_wave1/claim_status_delta.md`
- updated `proofs/artifacts/2026-02-20_zpe_xr_wave1/impracticality_decisions.json`
- updated `proofs/artifacts/2026-02-20_zpe_xr_wave1/license_risk_register_xr.md`
- updated `proofs/artifacts/2026-02-20_zpe_xr_wave1/net_new_gap_closure_matrix.json`

## Commercialization Rule
If only non-commercial/restricted assets exist and no commercial-safe open alternative is proven equivalent:
1. mark claim status `PAUSED_EXTERNAL`,
2. include command evidence and blocker signature,
3. record claim impact in `impracticality_decisions.json`.

## Fail Signatures
- Claim status is promoted without evidence artifact paths.
- Hardware/runtime dependency unresolved but claim marked `PASS`.
- Restricted-license path treated as commercial-safe without legal evidence.

## Rollback
- Revert only claim-adjudication script deltas (`code/scripts/run_gate_f.py`, `code/scripts/run_gate_e.py`).
- Re-run Gate F then final Gate E.

## Fallback
- If hardware/runtime cannot be executed locally, keep claim `PAUSED_EXTERNAL` and keep lane-level decision `NO-GO` for production runtime assertions.
