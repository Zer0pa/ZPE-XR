# Phase 2 Outward-Safe Corpus Probe

- Generated: `2026-03-20T00:05:36.878190+00:00`
- Disk headroom GiB: `11.37`

## ContactPose
- Status: `READY_FOR_LOCAL_INTAKE`
- License: `MIT License`
- Sample data reachable: `True`
- Sample data size: `1.8G`
- Joint topology: `21-joint OpenPose hand format`

## Ego4D Hands & Objects
- Status: `CONTEXT_ONLY_FALLBACK`
- License: `MIT License`
- Direct 3D hand-pose benchmark: `False`
- Reason: Official Hands & Objects benchmark is interaction/object-state oriented, not a direct 3D hand-pose transport benchmark.

## Exact PRD Gap
- `egocentric_100k_exact_prd_surface`: The exact PRD-named egocentric corpus was not concretely locatable as an official directly executable 3D hand-pose source during this phase.

## Verdict
- ContactPose is the strongest outward-safe freely reachable corpus lane available now; the exact PRD egocentric corpus remains unresolved, and Ego4D Hands & Objects is not a direct pose-equivalent benchmark.
