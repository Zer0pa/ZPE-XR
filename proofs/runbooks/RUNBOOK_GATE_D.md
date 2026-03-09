# Gate D Runbook: Malformed/Adversarial/Determinism Campaigns

## Objective
Attempt falsification under malformed, adversarial, and deterministic replay stress.

## Commands (Predeclared)
1. `PYTHONHASHSEED=0 python3 code/scripts/run_gate_d.py`

## Expected Outputs
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/determinism_replay_results.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/falsification_results.md`

## Fail Signatures
- Any uncaught exception/crash in malformed corpus.
- Determinism hash mismatch in any of 5 seeds.

## Rollback
- Harden parser bounds checks and replay path.
- Re-run Gate D and Gate E.

## Fallbacks
- If cryptographic hash module fails, use deterministic byte-equality plus CRC32 fallback and mark reduced assurance.

## Gate PASS Criteria
- Crash rate 0% on malformed/adversarial campaigns.
- Determinism 5/5 hash-consistent.
