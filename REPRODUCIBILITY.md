# Reproducibility

## Canonical Inputs

Repo-local canonical inputs and corpus manifests:

- `code/fixtures/benchmark_config.json`
- `code/fixtures/resource_lock.json`
- `code/fixtures/synthetic_hot3d_snapshot_v1.json`
- `proofs/artifacts/public_hand_benchmarks/public_hand_benchmark_manifest.json`
- `proofs/artifacts/public_hand_benchmarks/contactpose_status.json`

Measured authority artifacts:

- `proofs/artifacts/2026-04-14_zpe_xr_live_014204/phase5_multi_sequence_benchmark.json`
- `proofs/artifacts/2026-03-29_zpe_xr_phase6_mac_comparator_arm64/phase6_mac_comparator_benchmark.json`

Raw third-party hand-pose corpora are not committed to this repository; their public access status is tracked in `proofs/artifacts/public_hand_benchmarks/`.

## Golden-Bundle Hash

Pending. This will be populated by the `receipt-bundle.yml` workflow in Wave 3.

## Verification Command

```bash
git clone https://github.com/Zer0pa/ZPE-XR.git zpe-xr
cd zpe-xr
python -m venv .venv
source .venv/bin/activate
python -m pip install "./code[dev]"
python ./executable/verify.py
python -m pytest ./code/tests -q
```

## Supported Runtimes

- Python 3.11+ package surface.
- Rust/PyO3 kernel built through `maturin`.
- Current PyPI wheel targets cover Linux x86_64, Linux aarch64, macOS arm64, and Windows x86_64.
- Unity, Meta runtime closure, and broader XR runtime integration remain outside the current verified surface.
