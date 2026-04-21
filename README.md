<p align="center">
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>

<p align="center"><strong>Deterministic hand transport for XR two-hand streams: sub-millisecond encode+decode latency, byte-identical replay, and mixed-gesture packet delivery on the current ContactPose lane.</strong></p>
<p align="center"><em>The codec package is real. The ContactPose benchmark lane is real. Public release readiness is still blocked because the modern comparator gate remains 0/5 and runtime closure stays external.</em></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-SAL%20v6.2-e5e7eb?labelColor=111111" alt="License: SAL v7.0"></a>
  <a href="code/pyproject.toml"><img src="https://img.shields.io/badge/python-3.11%2B-e5e7eb?labelColor=111111" alt="Python 3.11+"></a>
  <a href="https://pypi.org/project/zpe-xr/"><img src="https://img.shields.io/badge/release-PyPI%20v0.3.0-e5e7eb?labelColor=111111" alt="Release: PyPI v0.3.0"></a>
  <a href="proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_surface_adjudication.md"><img src="https://img.shields.io/badge/current%20gate-PRIVATE__ONLY-e5e7eb?labelColor=111111" alt="Current gate: PRIVATE_ONLY"></a>
</p>
<p align="center">
  <a href="docs/ARCHITECTURE.md"><img src="https://img.shields.io/badge/quick%20verify-install%20%26%20verify-e5e7eb?labelColor=111111" alt="Quick verify: install and verify"></a>
  <a href="docs/ARCHITECTURE.md"><img src="https://img.shields.io/badge/architecture-runtime%20map-e5e7eb?labelColor=111111" alt="Architecture: runtime map"></a>
  <a href="docs/LEGAL_BOUNDARIES.md"><img src="https://img.shields.io/badge/public%20audit-explicit%20limits-e5e7eb?labelColor=111111" alt="Public audit: explicit limits"></a>
  <a href="proofs/artifacts/2026-03-29_zpe_xr_phase6_mac_comparator_arm64/phase6_mac_comparator_benchmark.md"><img src="https://img.shields.io/badge/comparator%20gate-0%2F5%20fail-e5e7eb?labelColor=111111" alt="Comparator gate: 0/5 fail"></a>
</p>

# ZPE-XR

| What This Is | Key Metrics | Competitive Benchmarks | What We Prove | What We Don't Claim |
|---|---|---|---|---|
| [Jump](#what-this-is) | [Jump](#key-metrics) | [Jump](#competitive-benchmarks) | [Jump](#what-we-prove) | [Jump](#what-we-dont-claim) |

| Commercial Readiness | Tests and Verification | Proof Anchors | Repo Shape | Quick Start |
|---|---|---|---|---|
| [Jump](#commercial-readiness) | [Jump](#tests-and-verification) | [Jump](#proof-anchors) | [Jump](#repo-shape) | [Jump](#quick-start) |

## What This Is

ZPE-XR is a deterministic transport codec for two-hand joint streams. It targets XR platform teams that care about packet size, transport determinism, and replay behavior more than a generic compression headline.

The honest public wedge is transport behavior on the current ContactPose lane: `0.057 ms` mean encode+decode latency, byte-identical replay, and `0.479 mm` mean position error while moving far less data than raw streams. The package is real and published. Public release readiness is not real because the modern comparator gate is still `0/5`, Photon remains narrower semantics, and runtime closure for Unity or Meta remains external.

## Key Metrics

| Metric | Value | Baseline |
|---|---|---|
| Compression vs raw | 23.90x | Ultraleap 8.47x |
| Mean position error | 0.479 mm MPJPE | float16+zlib 0.277 mm |
| Encode+decode latency | 0.057 ms mean | float16+zlib 0.084 ms |
| Modern comparator gate | 0/5 passed | float16+zlib wins 5/5 |

## Competitive Benchmarks

The benchmark story is mixed on purpose. ZPE-XR carries a strong transport surface on the outward-safe ContactPose lane, but the closest modern local proxy still beats it on fidelity. That is why the release posture stays private-only.

| Tool | Compression | Fidelity | Boundary |
|---|---|---|---|
| ZPE-XR live ContactPose lane | 23.90x | 0.479 mm MPJPE | Real measured repo lane |
| float16+zlib local proxy | 4.33x | 0.277 mm MPJPE | Modern comparator that wins 5/5 |
| Ultraleap VectorHand | 8.47x | — | Code-derived transport-only comparator |
| Photon Fusion XR Hands | 38.32x | — | Doc-derived, narrower semantics than full position transport |

## What We Prove

- The `zpe-xr` package and repo install surfaces are real.
- The current ContactPose rerun proves `23.90x` compression vs raw, `0.057 ms` mean encode+decode latency, and `0.479 mm` mean position error on the selected five-sequence lane.
- Byte-identical replay is part of the carried transport surface.
- The cold-start audit and release-decision packet are present and live in the repo.
- The repo can tell the truth about strong transport behavior without pretending comparator superiority or runtime closure.

## What We Don't Claim

- No public release readiness.
- No Unity or Meta runtime closure.
- No Photon displacement claim.
- No exact PRD-corpus closure claim.
- No broad hand-tracking superiority claim.

## Commercial Readiness

| Field | Value |
|---|---|
| Verdict | `PRIVATE_ONLY` |
| Release posture | Live work in progress; not a final official release |
| Ideal first buyer | XR platform team or spatial-computing infrastructure team |
| Deployment | SDK — Python package candidate with evaluation harness |
| Current blocker | Modern comparator gate `0/5` plus `XR-C007` runtime closure `PAUSED_EXTERNAL` |

The repo is commercially legible now because the transport wedge is explicit, but the release gate remains shut. The correct outward posture is private evaluation, not public rollout.

## Tests and Verification

| Code | Check | Verdict |
|---|---|---|
| V_01 | ContactPose benchmark lane | PASS |
| V_02 | Package mechanics | PASS |
| V_03 | Cold-start audit | PASS |
| V_04 | Modern comparator gate | FAIL |
| V_05 | XR-C007 runtime closure | INC |
| V_06 | Public release readiness | FAIL |

## Proof Anchors

| Path | Why it matters |
|---|---|
| `proofs/artifacts/2026-04-14_zpe_xr_live_014204/phase5_multi_sequence_benchmark.json` | Current ContactPose transport metrics |
| `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_surface_adjudication.md` | Governing claim boundary and verdict |
| `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_release_decision.md` | Release decision and blocker framing |
| `proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json` | Package cold-start audit |
| `proofs/artifacts/2026-03-29_zpe_xr_phase6_mac_comparator_arm64/phase6_mac_comparator_benchmark.md` | Comparator failure surface that keeps the gate closed |

## Repo Shape

| Area | Purpose |
|---|---|
| `code/` | Installable package and tests |
| `executable/` | Root verification entrypoint |
| `docs/` | Architecture, legal boundaries, and public audit limits |
| `proofs/` | Live benchmark artifacts, adjudications, and comparator packets |

## Quick Start

Install from PyPI:

```bash
pip install zpe-xr
```

Verify from source:

```bash
git clone https://github.com/Zer0pa/ZPE-XR.git zpe-xr
cd zpe-xr
python -m venv .venv
source .venv/bin/activate
python -m pip install "./code[dev]"
python ./executable/verify.py
python -m pytest ./code/tests -q
```

Read `docs/ARCHITECTURE.md` first, then `docs/LEGAL_BOUNDARIES.md`, then the Phase 5 and Phase 6 proof anchors above. `LICENSE` is the legal source of truth; the repo uses SAL v7.0.
