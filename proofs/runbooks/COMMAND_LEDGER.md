# Command Ledger (Predeclared)

## Environment
- `python3 --version`
- `PYTHONHASHSEED=0`
- `set -a; source .env; set +a`

## Gate A
- `mkdir -p code/src/zpe_xr code/tests code/scripts code/fixtures proofs/artifacts/2026-02-20_zpe_xr_wave1`
- `PYTHONHASHSEED=0 python3 code/scripts/lock_resources.py`

## Gate B
- `PYTHONHASHSEED=0 python3 code/scripts/generate_fixtures.py`
- `PYTHONHASHSEED=0 python3 code/scripts/run_gate_b.py`

## Gate C
- `PYTHONHASHSEED=0 python3 code/scripts/run_gate_c.py`

## Gate D
- `PYTHONHASHSEED=0 python3 code/scripts/run_gate_d.py`

## Gate E
- `PYTHONHASHSEED=0 python3 -m pytest ./code/tests -q > proofs/artifacts/2026-02-20_zpe_xr_wave1/regression_results.txt`
- `PYTHONHASHSEED=0 python3 code/scripts/run_gate_e.py`

## Gate M1 (HOT3D path)
- `PYTHONHASHSEED=0 python3 code/scripts/run_gate_m1.py`

## Gate M2 (Unity runtime and toolkit path)
- `PYTHONHASHSEED=0 python3 code/scripts/run_gate_m2.py`

## Gate M3 (extended stress)
- `PYTHONHASHSEED=0 python3 code/scripts/run_gate_m3.py`

## Gate M4 (residual risk closure)
- `PYTHONHASHSEED=0 python3 code/scripts/run_gate_m4.py`

## Appendix E NET-NEW gates
- `PYTHONHASHSEED=0 python3 code/scripts/run_appendix_e.py`

## Appendix F commercialization closure gates
- `PYTHONHASHSEED=0 python3 code/scripts/run_gate_f.py`
- `PYTHONHASHSEED=0 python3 code/scripts/run_gate_e.py`

## RunPod readiness supplements (when GPU path is required or conditional)
- `source .venv/bin/activate && python -m pip freeze > proofs/artifacts/2026-02-20_zpe_xr_wave1/runpod_requirements_lock.txt`

## Expected Failure Signatures
- `Compression ratio below threshold`
- `Fidelity threshold breach`
- `Latency threshold breach`
- `Uncaught crash in malformed corpus`
- `Determinism mismatch`
- `IMP-LICENSE`
- `IMP-ACCESS`
- `IMP-COMPUTE`
- `IMP-STORAGE`
- `IMP-NOCODE`
- `PAUSED_EXTERNAL`
- `UNITY_RUNTIME_OR_DEVICE_UNAVAILABLE`

## Rollback Marker
On gate failure: patch minimally and rerun failed gate + downstream gates.
