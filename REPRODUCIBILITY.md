# Reproducibility

## Canonical Inputs

The repo-tracked canonical inputs for public verification are:

- `code/fixtures/benchmark_config.json`
- `code/fixtures/resource_lock.json`
- `code/fixtures/synthetic_hot3d_snapshot_v1.json`
- `proofs/artifacts/public_hand_benchmarks/public_hand_benchmark_manifest.json`
- `proofs/artifacts/public_hand_benchmarks/contactpose_status.json`

## Golden-Bundle Hash

This value will be populated by the `receipt-bundle.yml` workflow in Wave 3.

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

- Python 3.11+
- Source builds with the bundled PyO3 Rust kernel via `maturin`
- Repo-root verification via `python ./executable/verify.py` and `pytest ./code/tests -q`
