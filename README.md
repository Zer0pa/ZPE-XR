# ZPE-XR

ZPE-XR is a deterministic XR hand-stream codec and evaluation harness for
dual-hand pose compression, packet-loss recovery, gesture classification, and
Unity-envelope roundtrip checks.

This repository is a private staging repo. It is not a public-release surface,
and it is not proof-complete.

## Current Authority

Current repo truth is split across three surfaces:

- `code/`: the runnable package, tests, fixtures, and gate scripts.
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/`: the historical Wave-1 evidence
  bundle copied from the pre-repo workspace.
- `proofs/FINAL_STATUS.md` and `proofs/RELEASE_READINESS_REPORT.md`: the
  current staged reading of what that bundle does and does not establish.

Historical bundle files remain preserved as evidence lineage. They include some
older flat-workspace paths and over-strong labels. Those historical strings do
not outrank the current repo docs.

## What This Repo Currently Supports

- Historical Wave-1 metrics copied into this repo:
  - compression ratio vs raw: `24.28x`
  - MPJPE: `0.884 mm`
  - average encode+decode latency: `0.0833 ms`
  - 10% packet-loss target case pose error: `1.633%`
  - gesture accuracy: `1.000`
  - modeled 4-player session bandwidth: `15.81 KB/s`
- Local package install from `./code`
- Repo-local minimal sanity via `python ./executable/verify.py`

## What This Repo Does Not Currently Prove

- HOT3D-backed full claim closure from the checked-in scripts
- external-corpus closure for HOI-M3 or HO-Cap
- production Unity/Meta XR runtime validation
- cold-clone verification for this staged snapshot
- public-release readiness

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e "./code[dev]"
python ./executable/verify.py
```

Optional local test replay:

```bash
python -m pytest ./code/tests -q
```

## Repo Layout

- `code/`: package, tests, fixtures, and gate scripts
- `docs/`: architecture, FAQ, legal boundaries, and support routing
- `proofs/`: current status notes plus the preserved historical artifact bundle
- `AUDITOR_PLAYBOOK.md`: shortest honest staged-audit path
- `PUBLIC_AUDIT_LIMITS.md`: explicit limits of what this staged repo can prove

## Go Next

- Read [docs/README.md](docs/README.md)
- Read [proofs/FINAL_STATUS.md](proofs/FINAL_STATUS.md)
- Read [AUDITOR_PLAYBOOK.md](AUDITOR_PLAYBOOK.md)
