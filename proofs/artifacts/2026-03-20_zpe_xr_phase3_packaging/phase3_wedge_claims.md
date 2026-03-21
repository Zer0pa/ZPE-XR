# Phase 3 Wedge Claims

## Allowed

- `codec_frozen_lane`: Fresh root rerun preserves 24.277x compression vs raw, 0.884 mm MPJPE, 0.067 ms average encode+decode latency, and 1.633% pose error at 10% loss.
- `synthetic_gesture_sidecar`: Fresh synthetic gesture evaluation remains at 1.000 accuracy with the claim kept inside the synthetic corpus boundary.
- `ultraleap_bounded_row`: ZPE remains smaller than the open-source Ultraleap VectorHand row under the documented close transport semantics.
- `contactpose_local_lane`: ContactPose is ready for local intake with an explicit 21-to-26 topology adapter and the exact PRD corpus gap preserved.

## Open

- `photon_displacement`: OPEN — Photon's documented compressed hand path is smaller but narrower in semantics, so the row stays open.
- `runtime_closure`: PAUSED_EXTERNAL — Editor, disk, device-trace, and MANO-license blockers remain active.
- `exact_prd_corpus`: UNRESOLVED — ContactPose is the best outward-safe lane available now, but it is not the exact PRD surface.
- `public_release_readiness`: NOT_READY — Blind-clone and release-channel decision phases are still outstanding.

## Forbidden

- `market_leading_runtime`: Market-leading XR runtime — Runtime closure is still explicitly paused.
- `photon_closed`: Photon is displaced — Photon remains an open semantics-mismatched row.
- `exact_corpus_closed`: Exact PRD corpus is closed — ContactPose is a substitute lane, not the exact named corpus.
- `public_release_ready`: Ready for public release — Package candidate formation does not replace blind-clone or release-channel closure.
