# Gate A Runbook: Runbook + Fixture/Resource Lock

## Objective
Establish reproducible execution scaffolding before coding.

## Preconditions
- Master runbook exists.
- Command ledger exists.

## Commands (Predeclared)
1. `mkdir -p code/src/zpe_xr code/tests code/scripts code/fixtures proofs/artifacts/2026-02-20_zpe_xr_wave1`
2. `python3 --version`
3. `PYTHONHASHSEED=0 python3 code/scripts/lock_resources.py`

## Expected Outputs
- `code/fixtures/resource_lock.json`
- `code/fixtures/synthetic_hot3d_snapshot_v1.json`
- Directory scaffold complete.

## Fail Signatures
- `python3: command not found`
- permission denied for artifact paths.
- resource lock script fails hash generation.

## Rollback
- Remove partial fixture files from `code/fixtures/`.
- Re-run Gate A commands after minimal patch.

## Fallbacks
- If runtime lacks hashlib feature (unlikely), use SHA256 via `shasum -a 256` shell fallback.

## Gate PASS Criteria
- Runbook files present.
- Resource lock fixture generated with hashes and snapshot metadata.
