# Gate E Runbook: Packaging + Claim Adjudication

## Objective
Assemble artifacts, adjudicate claims, produce scorecard and integration contract.

Final-phase note:
- After Appendix E and Gate F, rerun Gate E for final adjudication (`phase=max` with commercialization closures).

## Commands (Predeclared)
1. `PYTHONHASHSEED=0 python3 -m pytest ./code/tests -q > proofs/artifacts/2026-02-20_zpe_xr_wave1/regression_results.txt`
2. `PYTHONHASHSEED=0 python3 code/scripts/run_gate_e.py`

## Expected Outputs
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/handoff_manifest.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/before_after_metrics.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/claim_status_delta.md`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/quality_gate_scorecard.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/innovation_delta_report.md`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/integration_readiness_contract.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/residual_risk_register.md`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/concept_open_questions_resolution.md`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/concept_resource_traceability.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/command_log.txt`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/gate_f_result.json` (when Appendix F is executed)

## Fail Signatures
- Missing required artifact.
- Any claim without evidence path.
- Rubric total score < 45 or non-negotiable dimension below threshold.

## Rollback
- Patch packaging scripts and rerun Gate E.

## Fallbacks
- If pytest unavailable, run `python3 -m unittest discover -s code/tests` and record substitution impact.

## Gate PASS Criteria
- Complete artifact contract and final GO/NO-GO decision.
