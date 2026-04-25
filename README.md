<p align="center"><strong>Deterministic hand transport for XR two-hand streams: 23.90x compression vs raw (2.82x past Ultraleap's 8.47x), 6.63x smaller frames, and 9.5x better fidelity than the Ultraleap VectorHand proxy — on the ContactPose aggregate lane.</strong></p>
<p align="center"><em>The codec package is real. The ContactPose benchmark lane is real. Public release is BLOCKED: the modern comparator gate is 0/5 and runtime closure for Unity/Meta remains external. Transport numbers are same-machine local proxies, not vendor runtimes.</em></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-SAL%20v7.0-e5e7eb?labelColor=111111" alt="License: SAL v7.0"></a>
  <a href="code/pyproject.toml"><img src="https://img.shields.io/badge/python-3.11%2B-e5e7eb?labelColor=111111" alt="Python 3.11+"></a>
  <a href="https://pypi.org/project/zpe-xr/"><img src="https://img.shields.io/badge/release-PyPI%20v0.3.0-e5e7eb?labelColor=111111" alt="Release: PyPI v0.3.0"></a>
  <a href="proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_surface_adjudication.md"><img src="https://img.shields.io/badge/release-BLOCKED-e5e7eb?labelColor=111111" alt="Release: BLOCKED"></a>
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

ZPE-XR is a deterministic transport codec for two-hand joint streams in the Zer0pa 17-lane codec portfolio. It targets XR platform teams that care about packet size, transport determinism, and replay behavior more than a generic compression headline.

Transport behavior on the ContactPose aggregate lane (five sequences): `23.90x` compression vs raw, `0.057 ms` mean encode+decode latency, `0.479 mm` mean position error, and `6.63x` smaller frames than the Ultraleap VectorHand local proxy. The package is real and published on PyPI. Public release is BLOCKED: the modern comparator gate is `0/5` (float16+zlib wins on fidelity), Photon semantics remain narrower, and Unity/Meta runtime closure is external.

## Key Metrics

| Metric | Value | Baseline | Proof anchor |
|---|---|---|---|
| Compression vs raw (ContactPose full sequences) | 23.90x | Ultraleap 8.47x | `proofs/artifacts/2026-04-14_zpe_xr_live_014204/phase5_multi_sequence_benchmark.json` |
| Mean position error | 0.479 mm MPJPE | float16+zlib 0.277 mm (better fidelity) | `proofs/artifacts/2026-04-14_zpe_xr_live_014204/phase5_multi_sequence_benchmark.json` |
| Encode+decode latency | 0.057 ms mean | float16+zlib 0.084 ms | `proofs/artifacts/2026-04-14_zpe_xr_live_014204/phase5_multi_sequence_benchmark.json` |
| Bytes/frame vs Ultraleap VectorHand (ContactPose) | 25.9 vs 172.0 bytes — 6.63x smaller | Ultraleap VectorHand local proxy | `proofs/artifacts/2026-03-29_zpe_xr_phase7_ultraleap_local/phase7_ultraleap_local_benchmark.json` |
| Latency vs Ultraleap VectorHand (ContactPose) | 0.024 ms vs 0.154 ms — 6.4x lower | Ultraleap VectorHand local proxy | `proofs/artifacts/2026-03-29_zpe_xr_phase7_ultraleap_local/phase7_ultraleap_local_benchmark.json` |
| Bytes/frame vs Photon (ContactPose real data) | 25.9 vs 38.0 bytes — ZPE smaller on real data | Photon articulation proxy (narrower semantics) | `proofs/artifacts/2026-03-29_zpe_xr_phase8_photon_local/phase8_photon_local_benchmark.json` |
| Fidelity vs Photon (ContactPose) | 0.479 mm vs 10.683 mm MPJPE — 22x better | Photon articulation proxy | `proofs/artifacts/2026-03-29_zpe_xr_phase8_photon_local/phase8_photon_local_benchmark.json` |
| Packet-loss resilience (10% loss) | 0.399% pose error | Ultraleap 3.80% pose error (5-seq mean) | `proofs/artifacts/2026-03-29_zpe_xr_phase7_ultraleap_local/phase7_ultraleap_local_benchmark.json` + `code/tests/test_network.py` |
| 4-player modeled bandwidth @90 fps | 6.84 KB/s | Ultraleap 45.35 KB/s | `proofs/artifacts/2026-03-29_zpe_xr_phase7_ultraleap_local/phase7_ultraleap_local_benchmark.json` |
| Modern comparator gate | 0/5 passed | float16+zlib wins 5/5 | `proofs/artifacts/2026-03-29_zpe_xr_phase6_mac_comparator_arm64/phase6_mac_comparator_benchmark.json` |

## Competitive Benchmarks

The benchmark story is mixed on purpose. ZPE-XR carries a strong transport surface on the ContactPose lane — 6.63x smaller frames and 9.5x better fidelity than the Ultraleap VectorHand proxy — but the closest modern local baseline (float16+zlib) still wins on fidelity (0.277 mm vs 0.479 mm). That is the honest reason the release posture stays `PRIVATE_ONLY`. Release posture per phase5 decision: `PRIVATE_ONLY` — public package shipped on PyPI v0.3.0; vendor-runtime closure (Unity/Meta) is external; comparator gate is 0/5 vs float16+zlib. All comparator rows are same-machine local proxies, not vendor runtimes.

| Tool | Compression vs raw | Bytes/frame | Fidelity (MPJPE mm) | Latency (combined ms) | Packet-loss error (10% loss) | Boundary / evidence |
|---|---|---|---|---|---|---|
| ZPE-XR live ContactPose (full sequences) | 23.90x | 25.9 | 0.479 | 0.057 | 0.399% | `2026-04-14_zpe_xr_live_014204` — measured local |
| float16+zlib local proxy | 4.33x | 336.1 | **0.277** (wins) | 0.084 | — | `2026-03-29_zpe_xr_phase6_mac_comparator_arm64` — modern comparator wins 5/5 |
| Ultraleap VectorHand local proxy | 8.47x | 172.0 | 4.554 | 0.154 | 3.80% (5-seq mean) | `2026-03-29_zpe_xr_phase7_ultraleap_local` — proxy measured, not vendor runtime |
| Photon Fusion XR Hands articulation proxy (ContactPose) | 38.32x synthetic / ZPE smaller on real data | **38.0** (synthetic win only) | 10.683 | 0.179 | 8.90% | `2026-03-29_zpe_xr_phase8_photon_local` — narrower semantics, no hand-root pose metered |

Key ratios vs closest open-transport comparator (Ultraleap, same-machine proxy):
- Bytes: ZPE **6.63x smaller** on ContactPose real data (25.9 vs 172.0 bytes/frame)
- Latency: ZPE **6.4x lower** on ContactPose (0.024 ms vs 0.154 ms mean)
- Fidelity: ZPE **9.5x better** MPJPE (0.479 mm vs 4.554 mm)
- Packet-loss resilience: ZPE **9.5x lower** pose error at 10% loss (0.399% vs 3.80% 5-seq mean)

Note on Photon: ZPE is smaller than the Photon articulation proxy on ContactPose real-data bytes (25.9 vs 38.0 bytes/frame), but the Photon row meters only the 19-byte-per-hand finger stream and does not include shared hand-root pose — semantics are narrower than ZPE's full two-hand position stream.

## What We Prove

- The `zpe-xr` package and repo install surfaces are real.
- The current ContactPose rerun proves `23.90x` compression vs raw, `0.057 ms` mean encode+decode latency, and `0.479 mm` mean position error on the selected five-sequence lane.
- Byte-identical replay is part of the carried transport surface.
- The cold-start audit and release-decision packet are present and live in the repo.
- Same-machine proxy lanes exist for Ultraleap VectorHand and Photon Fusion XR Hands, with Photon still narrower than the frozen full-position stream.
- The repo can tell the truth about strong transport behavior without pretending comparator superiority or runtime closure.

## What We Don't Claim

- No public release readiness.
- No Unity or Meta runtime closure.
- No Photon displacement claim.
- No exact PRD-corpus closure claim.
- No broad hand-tracking superiority claim.

## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | BLOCKED |
| Release posture | `PRIVATE_ONLY` — public release withheld; package on PyPI v0.3.0 but vendor-runtime closure (Unity/Meta) is external; comparator gate is 0/5 vs float16+zlib |
| Source | `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_surface_adjudication.md` |

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
| `proofs/artifacts/2026-04-14_zpe_xr_live_014204/phase5_multi_sequence_benchmark.json` | Current ContactPose transport metrics (23.90x, 0.479 mm, 0.057 ms) |
| `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_surface_adjudication.md` | Governing claim boundary and verdict |
| `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_release_decision.md` | Release decision and blocker framing |
| `proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json` | Package cold-start audit |
| `proofs/artifacts/2026-03-29_zpe_xr_phase6_mac_comparator_arm64/phase6_mac_comparator_benchmark.json` | Comparator failure surface: float16+zlib wins 5/5, ZPE fidelity gap quantified |
| `proofs/artifacts/2026-03-29_zpe_xr_phase7_ultraleap_local/phase7_ultraleap_local_benchmark.json` | Same-machine Ultraleap proxy: 6.63x bytes, 6.4x latency, 9.5x fidelity advantage for ZPE (5-seq aggregate) |
| `proofs/artifacts/2026-03-29_zpe_xr_phase8_photon_local/phase8_photon_local_benchmark.json` | Same-machine Photon articulation proxy: ZPE smaller on real-data bytes, 22x better fidelity |

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
