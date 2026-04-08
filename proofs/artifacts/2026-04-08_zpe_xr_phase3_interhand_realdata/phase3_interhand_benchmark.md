# Phase 3 InterHand2.6M Benchmark

- dataset: `InterHand2.6M`
- splits: `train, val, test`
- total frames: `2828`

| Split | Capture | Sequence | Frames | Ratio | MPJPE (mm) | Combined latency (ms) |
|-------|---------|----------|--------|-------|------------|-----------------------|
| train | 1 | 0390_dh_touchROM | 1545 | 3.787x | 0.567 | 0.097 |
| val | 0 | ROM09_Interaction_Fingers_Touching | 607 | 4.150x | 0.617 | 0.093 |
| test | 1 | ROM01_No_Interaction_2_Hand | 676 | 4.795x | 0.676 | 0.084 |

## Aggregate

- mean compression vs raw: `4.244x`
- mean MPJPE: `0.620 mm`
- mean combined latency: `0.091 ms`
- quality pass: `True`
- latency pass: `True`
