# Public Hand Benchmark Scaffold

This directory is a planning scaffold for broader public-hand benchmark work.

It does **not** contain new measured benchmark authority. The governing measured anchors remain the existing ContactPose artifacts already referenced in `proofs/FINAL_STATUS.md`.

## What Is Here

- `public_hand_benchmark_manifest.json`
- one `*_status.json` file per dataset lane

These artifacts capture:

- official dataset surfaces
- current access or registration posture
- recommended cache layout
- current adapter status
- current benchmark status

## Current Interpretation

- ContactPose is the only runnable dataset lane in the nested repo today.
- InterHand2.6M, FreiHAND, HO-3D, DexYCB, and OakInk are scaffold-only in this phase.
- `NOT_RUN` means there is no measured benchmark claim for that dataset yet.

## Regeneration

```bash
python ./code/scripts/export_public_benchmark_manifest.py
```

or:

```bash
make benchmark-manifest
```
