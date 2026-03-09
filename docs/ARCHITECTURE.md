# Architecture

## Repo Map

- `code/src/zpe_xr/codec.py`: packet format, quantization, parser, concealment
- `code/src/zpe_xr/network.py`: sequence transport and realtime recovery
- `code/src/zpe_xr/pipeline.py`: gate evaluation helpers
- `code/src/zpe_xr/gesture.py`: synthetic gesture evaluation
- `code/src/zpe_xr/unity.py`: Unity-envelope serialization contract
- `code/tests/`: small deterministic regression surface
- `code/scripts/`: historical gate and appendix scripts
- `proofs/`: current status notes plus preserved historical artifacts

## Authority Classes

- Source-repo truth: `code/`, current repo docs, and staged reports
- Historical evidence: `proofs/artifacts/2026-02-20_zpe_xr_wave1/`
- External dependency truth: Unity, Meta XR SDK, HOT3D, MANO, HOI-M3, HO-Cap
  availability and licensing, which can constrain claims without being present
  in the repo

## Runtime Shape

The shipped package implements a deterministic codec for two-hand joint streams.
It covers:

- keyframe and delta packet encoding
- bounded packet parsing and checksum validation
- realtime loss recovery with concealment and backup deltas
- metric helpers for compression, fidelity, bandwidth, and latency
- a Unity-envelope compatibility layer

The current repo does not ship a production Unity or device runtime. It ships
the codec and the evaluation harness.
