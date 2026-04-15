# Auditor Playbook

This page is the shortest honest audit path for the current ZPE-XR repo surface.

It is not a legal opinion, not a runtime-closure pass, and not a substitute for the governing blocker surfaces.

## Three Dimensions

- Dimension 1: the package surface is real and locally verifiable.
- Dimension 2: the ContactPose benchmark surface is real and bounded.
- Dimension 3: the repo keeps blocker states explicit instead of smoothing them into pass language.

## Shortest Public Audit Path

1. Acquire the live XR repo:

```bash
git clone https://github.com/Zer0pa/ZPE-XR.git zpe-xr
cd zpe-xr
```

2. Create an environment and install the package:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install "./code[dev]"
```

3. Run the staged verification entrypoint:

```bash
python ./executable/verify.py
```

4. Optional test replay:

```bash
python -m pytest ./code/tests -q
```

5. Inspect the current proof anchors:

- `proofs/FINAL_STATUS.md`
- `proofs/RELEASE_READINESS_REPORT.md`
- `release_readiness.json`
- `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json`
- `proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json`

## Authority Matrix

| Anchor / artifact | Class | What it is for | What it is not for |
|---|---|---|---|
| `release_readiness.json` | package authority | install/build/package status | public-release clearance |
| `phase5_multi_sequence_benchmark.json` | benchmark authority | current ContactPose metrics and failed comparator row | runtime closure |
| `proofs/FINAL_STATUS.md` | claim boundary | current blocker and non-claim surface | package build instructions |
| `proofs/RELEASE_READINESS_REPORT.md` | release verdict | governing private/public posture | a proof that blockers are closed |
| `phase4_cold_start_audit.json` | cold-start hygiene | staged install/import sanity | a substitute for the Phase 5 benchmark |

## Expected Current Truth

- package version `0.3.0`
- local install/verify path succeeds on the staged package surface
- mean compression `23.90x`, mean MPJPE `0.479 mm`, mean latency `0.057 ms`, mean loss error `0.399%`
- modern comparator gate `0/5`
- release verdict `PUBLISHED_PYPI` (v0.3.0); modern comparator gate `0/5 FAIL`
- runtime closure `XR-C007 = PAUSED_EXTERNAL`

## If Your Replay Disagrees

Treat it as a replay mismatch, not as a free-form argument. Capture:

- commit hash
- exact command run
- stdout/stderr
- whether the disagreement is package, benchmark, or blocker-state related

Then read:

- `PUBLIC_AUDIT_LIMITS.md`
- `docs/FAQ.md`
- `docs/ARCHITECTURE.md`
