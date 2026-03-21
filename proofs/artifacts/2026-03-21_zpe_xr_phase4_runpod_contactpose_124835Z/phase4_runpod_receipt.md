# Phase 4 RunPod Receipt

## Scope

- canonical root workspace: `/Users/Zer0pa/ZPE/ZPE XR`
- decisive artifact run: `2026-03-21_zpe_xr_phase4_runpod_contactpose_124835Z`
- remote execution workspace: `/workspace/zpe_xr_phase4_2026-03-21_zpe_xr_phase4_runpod_contactpose_124543Z`

## Environment

- RunPod access path used: direct TCP `root@38.80.152.72:30709`
- pod id: `wijfmmgnjovmuu`
- remote hostname: `e445a2982b5c`
- remote Python: `3.11.10`
- local free disk before reconciliation: `37 GiB`
- remote free disk after cleanup: `146 TiB`

## Execution Chain

1. Repaired the root-owned Phase 4 runner, runtime-path handling, outer-root verify path, and the ContactPose sample resolver.
2. Confirmed the ContactPose Google Drive sample is a nested bundle: `contactpose_sample.zip -> grasps.zip -> object.zip -> annotations.json`.
3. Patched the ContactPose adapter to traverse the real nested archive structure.
4. Re-ran local verify and unit tests successfully.
5. Executed the decisive outward-safe benchmark on RunPod instead of the local Mac.
6. Seeded the final clean rerun from a RunPod-resident sample cache to avoid another large fetch.

## Result

- execution status: `EXECUTED`
- sovereign verdict: `PASS`
- compression vs raw: `56.144x`
- MPJPE: `0.478 mm`
- combined latency: `0.025 ms`
- pose error at `10%` loss: `0.399%`
- selected sequence: `ContactPose sample data/grasps.zip::grasps/full36_use/binoculars.zip::binoculars/annotations.json`
- secondary modern-comparator check: `False` with ratio vs ZPE `0.833x`

## Disk Handling

- local workspace remained compact at about `5.5M`
- only compact benchmark artifacts were copied back to the Mac
- the earlier redundant RunPod probe directory and failed workspace were deleted
- one RunPod-resident sample cache was kept in the verified workspace to avoid repeated 1.9G downloads

## Comet

- Comet experiment creation was unavailable because `COMET_API_KEY` was not present on the local Mac or the RunPod environment
- the run still wrote `comet_run_manifest.json` with a null experiment key

## Evidence

- `proofs/artifacts/2026-03-21_zpe_xr_phase4_runpod_contactpose_124835Z/phase4_contactpose_benchmark.json`
- `proofs/artifacts/2026-03-21_zpe_xr_phase4_runpod_contactpose_124835Z/phase4_contactpose_benchmark.md`
- `proofs/artifacts/2026-03-21_zpe_xr_phase4_runpod_contactpose_124835Z/comet_run_manifest.json`
