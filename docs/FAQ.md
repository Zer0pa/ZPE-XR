# FAQ

## What is ZPE-XR?

A deterministic XR hand-stream codec and evaluation harness for compression,
network resilience, gesture scoring, and Unity-envelope checks.

## Is this repo public-ready?

No. It is a private staging repo.

## What is the current proof anchor?

The preserved historical Wave-1 bundle under
`proofs/artifacts/2026-02-20_zpe_xr_wave1/`, read together with
`proofs/FINAL_STATUS.md`.

## Does this repo prove device-runtime readiness?

No. Unity/Meta runtime closure remains externally constrained.

## What is the fastest local sanity check?

```bash
python -m pip install -e "./code[dev]"
python ./executable/verify.py
```
