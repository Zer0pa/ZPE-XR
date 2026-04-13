# V6 Authority Surface — Completion Report

**Repo:** ZPE-XR  
**Agent:** Codex  
**Date:** 2026-04-14  
**Branch:** campaign/v6-authority-surface

## Dimensions Executed

- [x] **A: Key Metrics** — rewritten with phase5 benchmark authority and comparator baseline evidence.
- [x] **B: Competitive Benchmarks** — added from phase6 comparator benchmark evidence.
- [x] **C: pip Install Fix** — added root `pyproject.toml`, updated license to SAL 6.2.
- [x] **D: Publish Workflow** — added maturin publish workflow.
- [ ] **E: Proof Sync** — N/A.

## Verification

- pip install from root: PASS (maturin develop in repo venv)
- import test: PASS (`import zpe_xr`, version `0.3.0`)
- Proof anchors verified: 1/1 exist
- Competitive claims honest: YES (code-derived and doc-derived lanes labeled)

## Key Metrics Written

| Metric | Value | Baseline | Proof File |
|--------|-------|----------|------------|
| COMPRESSION | 56.144× | vs Ultraleap 8.465× (code-derived) | proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json |
| MPJPE | 0.4786 mm | position fidelity | proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json |
| LATENCY | 0.026 ms | mean encode+decode | proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json |
| COMPARATOR_GATE | 0/5 pass | modern comparators | proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json |

## Issues / Blockers

- Draco baseline reference from the brief is not present in any retained XR proof artifact. Used Ultraleap VectorHand baseline from phase6 comparator benchmark instead.
