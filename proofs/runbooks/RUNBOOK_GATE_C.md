# Gate C Runbook: Network Resilience + Gesture + Bandwidth

## Objective
Validate packet loss resilience, gesture accuracy, and multiplayer bandwidth.

## Commands (Predeclared)
1. `PYTHONHASHSEED=0 python3 code/scripts/run_gate_c.py`

## Expected Outputs
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/xr_packet_loss_resilience.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/xr_gesture_eval.json`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/xr_bandwidth_eval.json`

## Fail Signatures
- Pose error >= 5% at 10% loss.
- Gesture accuracy < 95%.
- 4-player session > 40 KB/s.

## Rollback
- Patch concealment/FEC and gesture classifier thresholds.
- Re-run Gate C and downstream gates.

## Fallbacks
- If external network stack unavailable, use deterministic in-process network simulator.

## Gate PASS Criteria
- XR-C004, XR-C005, XR-C006 pass with direct evidence.
