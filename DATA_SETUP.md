# Data Setup

This document is the operator guide for dataset-backed replay in the nested `ZPE-XR/` repo.

It is not a new authority surface and it does not change the current public verdict. Today, ContactPose remains the only dataset lane that is actually executed in this repo. The broader public-dataset surfaces added in Phase `09.1` are scaffolds for future work and stay explicitly `NOT_RUN` until real benchmark artifacts exist.

## Quick Read

- `python ./executable/verify.py` does **not** require external datasets.
- `python -m pytest ./code/tests -q` does **not** require external datasets.
- The real-data benchmark scripts do require ContactPose:
  - `code/scripts/run_phase4_contactpose_benchmark.py`
  - `code/scripts/run_phase5_contactpose_multi_sequence.py`
  - `code/scripts/run_phase6_mac_comparator_benchmark.py --attempt-contactpose`
- The staged tests use synthetic or in-memory fixtures; `code/tests/test_contactpose_adapter.py` does not download the real sample.

## ContactPose

### Current Download Surface

- Google Drive sample page: `https://drive.google.com/uc?export=download&id=1paUAxXgHp6wDFBFw9MI1mxGElEl2KPew`
- Repo constant: `zpe_xr.contactpose_adapter.CONTACTPOSE_SAMPLE_PAGE`
- Auto-download support: yes, through `download_contactpose_sample_zip()` and `ensure_contactpose_sample()`

### Recommended Cache Path

Use a reusable cache under:

```text
proofs/artifacts/datasets/contactpose/contactpose_sample.zip
```

The benchmark runners search for `contactpose_sample.zip` under the repo's artifact tree before they attempt a fresh download.

### Expected Archive Structure

The current adapter expects the nested sample-bundle shape below:

```text
contactpose_sample.zip
└── ContactPose sample data/
    └── grasps.zip
        └── grasps/full28_use/<object>.zip
            └── <object>/annotations.json
```

The adapter recurses through the nested zip members and reads `annotations.json` from the selected object bundle.

### Disk Guidance

- The Phase 4 and Phase 5 benchmark runners gate on a minimum of `5.0 GiB` free disk headroom before they fetch or reuse ContactPose.
- The runners download into a per-artifact `downloads/` directory and clean that temporary copy up afterward when possible.
- The stable cache path above is preferable when disk space is tight and you want reuse across runs.

## Public Benchmark Scaffold

Phase `09.1` adds a dataset manifest for the planned public benchmark surface:

- `proofs/artifacts/public_hand_benchmarks/README.md`
- `proofs/artifacts/public_hand_benchmarks/public_hand_benchmark_manifest.json`

These files describe the current status of:

- ContactPose
- InterHand2.6M
- FreiHAND
- HO-3D
- DexYCB
- OakInk

They are scaffold artifacts only. They are useful for planning cache layout, access requirements, and adapter work. They are not measured benchmark authority.

## Recommended Local Commands

```bash
make install
make verify
make test
make benchmark-manifest
```

To regenerate the public benchmark scaffold explicitly:

```bash
python ./code/scripts/export_public_benchmark_manifest.py
```

## Dataset Notes

| Dataset | Official surface | Current repo status | Recommended cache root |
| --- | --- | --- | --- |
| ContactPose | direct Google Drive sample | runnable | `proofs/artifacts/datasets/contactpose/` |
| InterHand2.6M | project page | planned, not run | `proofs/artifacts/datasets/interhand26m/` |
| FreiHAND | dataset page | planned, not run | `proofs/artifacts/datasets/freihand/` |
| HO-3D | project repo/docs | planned, not run | `proofs/artifacts/datasets/ho3d/` |
| DexYCB | official site + toolkit | planned, not run | `proofs/artifacts/datasets/dexycb/` |
| OakInk | official site + toolkit | planned, not run | `proofs/artifacts/datasets/oakink/` |

## Boundary Reminder

- New dataset setup guidance does not change the current modern comparator gate (0/5 FAIL) or runtime closure status.
- Only new measured benchmark artifacts can change dataset claims.
- The exact public comparator gate remains controlled by the current proof boundary, not by this operator document.
