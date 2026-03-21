# Phase 2 Comparator Matrix

- Generated: `2026-03-20T00:05:33.714739+00:00`
- Frozen workload: `1800 frames`, seed `1103`, gesture `mixed`

| Comparator | Bytes/frame | 4-player KB/s | Fairness class | Read |
|---|---:|---:|---|---|
| ZPE-XR deterministic codec | 59.97 | 15.81 | frozen_v1_authority_surface | Measured directly from the frozen benchmark workload in this workspace. |
| Raw OpenXR-like float stream | 1456.00 | 383.91 | frozen_v1_authority_surface | Frozen raw baseline for AM-XR-01. |
| Frozen modern comparator | 336.47 | 88.72 | frozen_v1_authority_surface | Internal frozen modern proxy used in Phase 1. |
| Photon Fusion XR Hands (doc-derived compressed rotations) | 38.00 | 10.02 | narrower_semantics_than_frozen_v1 | Official Photon documentation states that one hand full bone rotations compress to 19 bytes instead of 386 bytes for full quaternion transfer. |
| Photon Fusion XR Hands (doc-derived full quaternion transfer) | 772.00 | 203.55 | narrower_semantics_than_frozen_v1 | Official Photon documentation states that one hand full bone rotations occupy 386 bytes. |
| Ultraleap VectorHand compressed encoding | 172.00 | 45.35 | close_transport_semantics | Open-source Ultraleap VectorHand encoding fixes NUM_BYTES=86 per hand. |

## Verdicts
- `PASS`: ZPE-XR remains clearly better than the frozen internal modern comparator on transport cost.
  Evidence: zpe_xr_current.bytes_per_frame < modern_float16_delta_plus_zlib.bytes_per_frame
- `PASS`: ZPE-XR currently beats the open-source Ultraleap VectorHand encoding on bytes/frame under the frozen two-hand stream semantics.
  Evidence: doc/code-derived Ultraleap VectorHand NUM_BYTES=86 per hand vs measured ZPE avg bytes/frame
- `OPEN`: Photon-sized incumbent displacement is not closed because Photon's documented compressed path is narrower in semantics and smaller in bytes/frame.
  Evidence: doc-derived Photon compressed rotations only = 19 bytes/hand, which is smaller than current ZPE bytes/frame but not apples-to-apples with the frozen full-position stream.
