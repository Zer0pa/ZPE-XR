# Gate M2 Runbook: Unity Runtime Integration Path

## Objective
Attempt runtime-level Meta XR + XR Interaction Toolkit integration beyond interface-only harness.

## Commands (Predeclared)
1. `set -a; source .env; set +a`
2. `PYTHONHASHSEED=0 python3 code/scripts/run_gate_m2.py`

## Expected Outputs
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/max_claim_resource_map.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/license_risk_register_xr.md`

## Fail Signatures
- Unity CLI missing.
- Meta XR SDK unavailable in lane.
- package registry/auth errors.

## Rollback
- Patch integration probe scripts and rerun M2+ downstream.

## Fallback
- Contract-level probe retained; runtime claims move to `PAUSED_EXTERNAL` when engine runtime/device cannot be executed and no commercial-safe equivalent is proven.
