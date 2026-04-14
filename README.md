<p align="center">
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-SAL%20v6.0-e5e7eb?labelColor=111111" alt="License: SAL v6.0"></a>
  <a href="code/pyproject.toml"><img src="https://img.shields.io/badge/python-3.11%2B-e5e7eb?labelColor=111111" alt="Python 3.11+"></a>
  <a href="proofs/FINAL_STATUS.md"><img src="https://img.shields.io/badge/current%20authority-2026--03--21-e5e7eb?labelColor=111111" alt="Current authority: 2026-03-21"></a>
  <a href="release_readiness.json"><img src="https://img.shields.io/badge/release-private%20only-e5e7eb?labelColor=111111" alt="Release: private only"></a>
  <a href="proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json"><img src="https://img.shields.io/badge/current%20gate-0%2F5%20modern%20comparator-e5e7eb?labelColor=111111" alt="Current gate: 0/5 modern comparator"></a>
</p>
<p align="center">
  <a href="AUDITOR_PLAYBOOK.md"><img src="https://img.shields.io/badge/quick%20verify-local%20install%20%26%20verify-e5e7eb?labelColor=111111" alt="Quick verify"></a>
  <a href="proofs/FINAL_STATUS.md"><img src="https://img.shields.io/badge/proof%20anchors-status%20%2B%20benchmark-e5e7eb?labelColor=111111" alt="Proof anchors"></a>
  <a href="docs/ARCHITECTURE.md"><img src="https://img.shields.io/badge/architecture-runtime%20map-e5e7eb?labelColor=111111" alt="Architecture runtime map"></a>
  <a href="docs/LEGAL_BOUNDARIES.md"><img src="https://img.shields.io/badge/lane%20boundaries-dataset%20%2F%20runtime%20limits-e5e7eb?labelColor=111111" alt="Lane boundaries"></a>
  <a href="PUBLIC_AUDIT_LIMITS.md"><img src="https://img.shields.io/badge/public%20audit-explicit%20limits-e5e7eb?labelColor=111111" alt="Public audit limits"></a>
</p>

# ZPE-XR

<table align="center" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td width="20%"><a href="#what-this-is"><img src=".github/assets/readme/nav/what-this-is.svg" alt="What This Is" width="100%"></a></td>
    <td width="20%"><a href="#current-authority"><img src=".github/assets/readme/nav/current-authority.svg" alt="Current Authority" width="100%"></a></td>
    <td width="20%"><a href="#current-metrics"><img src=".github/assets/readme/nav/throughput.svg" alt="Current Metrics" width="100%"></a></td>
    <td width="20%"><a href="#quick-start"><img src=".github/assets/readme/nav/quickstart-and-license.svg" alt="Quick Start" width="100%"></a></td>
    <td width="20%"><a href="#ecosystem"><img src=".github/assets/readme/nav/go-next.svg" alt="Ecosystem" width="100%"></a></td>
  </tr>
</table>

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3.4.gif" alt="ZPE-XR Upper Insert" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

<a id="what-this-is"></a>


## Quick Start

The steps below are repository verification guidance for the live ZPE-XR workstream. They are not a public-release install claim and they do not imply runtime closure on Unity or Meta targets.

```bash
git clone https://github.com/Zer0pa/ZPE-XR.git zpe-xr
cd zpe-xr
python -m venv .venv
source .venv/bin/activate
python -m pip install "./code[dev]"
python ./executable/verify.py
```

Optional direct test replay:

```bash
python -m pytest ./code/tests -q
```

Current live repo:

- clone target: <code>https://github.com/Zer0pa/ZPE-XR.git</code>
- package metadata: <code>code/pyproject.toml</code>
- install/verify path: <code>python ./executable/verify.py</code>
- optional direct replay: <code>python -m pytest ./code/tests -q</code>

Not provided today:

- no PyPI release
- no public-release verdict
- no runtime-closure pass narrative

License boundary:

- Free use at or below the SAL v6.0 threshold; see `LICENSE` for exact terms.
- SPDX identifier: `LicenseRef-Zer0pa-SAL-6.0`.
- Commercial, hosted, or legal-interpretation questions route to `architects@zer0pa.ai`.
- The release posture remains `PRIVATE_ONLY` until the comparator and runtime gates are actually closed.


## What This Is

ZPE-XR is the canonical Zer0pa XR workstream for a deterministic hand-pose transport codec and evaluation harness. This repository is the governing public-facing surface for the XR package candidate: it exposes the code, the package boundary, the staged evidence, and the current non-claims. It is buildable and inspectable, but it is not a public-release pass narrative.

<table width="100%" border="1" bordercolor="#111111" cellpadding="14" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="26%">Question</th>
      <th align="left" width="74%">Answer</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td valign="top">What is this repo for?</td>
      <td valign="top">A deterministic XR codec and evaluation harness for two-hand joint streams, packaging, and proof-surface adjudication.</td>
    </tr>
    <tr>
      <td valign="top">What is the current strongest claim?</td>
      <td valign="top">The outward-safe ContactPose benchmark lane is real and the package mechanics are real. Public release readiness and runtime closure are not.</td>
    </tr>
    <tr>
      <td valign="top">What is not being claimed?</td>
      <td valign="top">No Photon displacement claim, no exact-PRD-corpus closure claim, no Unity/Meta runtime closure claim, and no public-release readiness claim.</td>
    </tr>
    <tr>
      <td valign="top">Where should an outsider acquire it?</td>
      <td valign="top">`https://github.com/Zer0pa/ZPE-XR.git` is the live workstream repo that matches this package and docs surface.</td>
    </tr>
  </tbody>
</table>

| Field | Value |
|-------|-------|
| Architecture | HAND_JOINT |
| Encoding | QUAT_PACK |

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3.5.gif" alt="ZPE-XR Lower Insert" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/throughput.svg" alt="KEY METRICS" width="100%">
</p>

<a id="current-metrics"></a>
<a id="key-metrics"></a>


## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | PRIVATE_ONLY |
| Commit SHA | b0a08fa02fd1 |
| Confidence | 62% |
| Source | proofs/FINAL_STATUS.md |

- Completeness basis: `5` closed claims / `8` tracked claims | RELEASE_READINESS_JSON


## Key Metrics

| Metric | Value | Baseline |
|--------|-------|----------|
| COMPRESSION | 23.898× | vs Ultraleap 8.465× (code-derived) |
| MPJPE | 0.4786 mm | position fidelity |
| LATENCY | 0.0575 ms | mean encode+decode |
| COMPARATOR_GATE | 0/5 pass | modern comparators |

> Source: [`proofs/artifacts/2026-04-14_zpe_xr_live_014204/phase5_multi_sequence_benchmark.json`](proofs/artifacts/2026-04-14_zpe_xr_live_014204/phase5_multi_sequence_benchmark.json) | [`proofs/artifacts/2026-03-29_zpe_xr_phase6_mac_comparator_arm64/phase6_mac_comparator_benchmark.md`](proofs/artifacts/2026-03-29_zpe_xr_phase6_mac_comparator_arm64/phase6_mac_comparator_benchmark.md)


## What We Prove

- 0.4786mm mean per-joint position error | ContactPose benchmark
- 23.898× compression vs raw | two-hand joint streams
- 0.0575ms encode+decode latency
- Local package install and tests pass

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-2.gif" alt="ZPE-XR Mid Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/out-of-scope.svg" alt="WHAT WE DON'T CLAIM" width="100%">
</p>

<a id="status-and-gaps"></a>


## What We Don't Claim

- No modern comparator gate closure (0/5)
- No Unity or Meta XR runtime integration
- No release readiness
- No production headset deployment
- Rotation encoding — codec encodes joint positions only (3 floats/joint), not full pose (7 floats/joint)

<table width="100%" border="1" bordercolor="#111111" cellpadding="14" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="24%">Area</th>
      <th align="left" width="50%">Gap</th>
      <th align="left" width="26%">Impact</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td valign="top">Public release</td>
      <td valign="top">Modern comparator gate failed (<code>0/5</code>).</td>
      <td valign="top">Blocks public-release language.</td>
    </tr>
    <tr>
      <td valign="top">Runtime closure</td>
      <td valign="top"><code>XR-C007</code> remains <code>PAUSED_EXTERNAL</code>.</td>
      <td valign="top">Blocks runtime-readiness and engine-integration claims.</td>
    </tr>
    <tr>
      <td valign="top">Comparator displacement</td>
      <td valign="top">Photon displacement remains secondary and open.</td>
      <td valign="top">No incumbent-displacement claim is admissible.</td>
    </tr>
    <tr>
      <td valign="top">Exact PRD corpus</td>
      <td valign="top">ContactPose is outward-safe but not the exact PRD corpus.</td>
      <td valign="top">Limits corpus and market-fit language.</td>
    </tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-XR Lower Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/runtime-proof-wave-1.svg" alt="CURRENT AUTHORITY" width="100%">
</p>

<a id="current-authority"></a>


## Tests and Verification

| Code | Check | Verdict |
|------|-------|---------|
| V_01 | ContactPose benchmark lane | PASS |
| V_02 | Package mechanics | PASS |
| V_03 | Cold-start audit | PASS |
| V_04 | Modern comparator gate | FAIL |
| V_05 | XR-C007 runtime closure | INC |
| V_06 | Public release readiness | FAIL |


## Proof Anchors

| Path | State |
|------|-------|
| proofs/FINAL_STATUS.md | VERIFIED |
| proofs/RELEASE_READINESS_REPORT.md | VERIFIED |
| proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json | VERIFIED |
| proofs/artifacts/2026-03-21_zpe_xr_phase4_runpod_contactpose_124835Z/phase4_contactpose_benchmark.json | VERIFIED |
| proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json | VERIFIED |
| release_readiness.json | VERIFIED |


## Repo Shape

| Field | Value |
|-------|-------|
| Proof Anchors | 6 |
| Modality Lanes | 5 |
| Authority Source | proofs/FINAL_STATUS.md |

<p>
  <img src=".github/assets/readme/section-bars/quick-start.svg" alt="QUICK START" width="100%">
</p>

<a id="quickstart-and-license"></a>
<a id="acquisition-surface"></a>
<a id="quick-start"></a>


## Ecosystem

- [ZPE-Mocap](https://github.com/Zer0pa/ZPE-Mocap) — Human motion codec and replay.
- [ZPE-Robotics](https://github.com/Zer0pa/ZPE-Robotics) — Robot motion codec and search.
- [ZPE-IMC](https://github.com/Zer0pa/ZPE-IMC) — Multimodal codec platform surface.

<p>
  <img src=".github/assets/readme/section-bars/where-to-go.svg" alt="GO NEXT" width="100%">
</p>

<a id="go-next"></a>


---


## Competitive Benchmarks

> Source: [`proofs/artifacts/2026-03-29_zpe_xr_phase6_mac_comparator_arm64/phase6_mac_comparator_benchmark.md`](proofs/artifacts/2026-03-29_zpe_xr_phase6_mac_comparator_arm64/phase6_mac_comparator_benchmark.md)

| Comparator | Status | Result |
|-----------|--------|--------|
| **ZPE-XR staged package (local Mac)** | Measured local | 55.722 bytes/frame, 26.130× compression |
| Ultraleap VectorHand | Code-derived transport | 172.000 bytes/frame, 8.465× compression |
| Photon Fusion XR Hands (compressed rotations) | Doc-derived transport | 38.000 bytes/frame, 38.316× compression (narrower semantics) |
| Unity Netcode for GameObjects | Blocked | No runnable same-machine hand-sync benchmark |
| Normcore VR/AR | Blocked | No runnable same-machine hand-sync benchmark |

<p>
  <img src=".github/assets/readme/section-bars/evidence-and-claims.svg" alt="WHAT WE PROVE" width="100%">
</p>


## Go Next

<table width="100%" border="1" bordercolor="#111111" cellpadding="14" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="38%">If you need to...</th>
      <th align="left" width="62%">Open this</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td valign="top">Read the current verdict and claim boundary</td>
      <td valign="top"><a href="proofs/FINAL_STATUS.md"><code>proofs/FINAL_STATUS.md</code></a></td>
    </tr>
    <tr>
      <td valign="top">Read the release decision and blockers</td>
      <td valign="top"><a href="proofs/RELEASE_READINESS_REPORT.md"><code>proofs/RELEASE_READINESS_REPORT.md</code></a></td>
    </tr>
    <tr>
      <td valign="top">Understand package/runtime surfaces</td>
      <td valign="top"><a href="docs/ARCHITECTURE.md"><code>docs/ARCHITECTURE.md</code></a></td>
    </tr>
    <tr>
      <td valign="top">Orient quickly or answer common questions</td>
      <td valign="top"><a href="docs/FAQ.md"><code>docs/FAQ.md</code></a></td>
    </tr>
    <tr>
      <td valign="top">Read audit limits and non-claims</td>
      <td valign="top"><a href="PUBLIC_AUDIT_LIMITS.md"><code>PUBLIC_AUDIT_LIMITS.md</code></a></td>
    </tr>
    <tr>
      <td valign="top">Follow the shortest honest audit path</td>
      <td valign="top"><a href="AUDITOR_PLAYBOOK.md"><code>AUDITOR_PLAYBOOK.md</code></a></td>
    </tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/section-bars/contributing-security-support.svg" alt="CONTRIBUTING, SECURITY, SUPPORT" width="100%">
</p>

<a id="contributing-security-support"></a>


## Contributing, Security, Support

<table width="100%" border="1" bordercolor="#111111" cellpadding="16" cellspacing="0">
  <tr>
    <td width="33%" valign="top">Contribution workflow: <a href="CONTRIBUTING.md"><code>CONTRIBUTING.md</code></a></td>
    <td width="33%" valign="top">Security policy and reporting: <a href="SECURITY.md"><code>SECURITY.md</code></a></td>
    <td width="34%" valign="top">Support routing: <a href="docs/SUPPORT.md"><code>docs/SUPPORT.md</code></a></td>
  </tr>
  <tr>
    <td width="33%" valign="top">Questions and quick answers: <a href="docs/FAQ.md"><code>docs/FAQ.md</code></a></td>
    <td colspan="2" width="67%" valign="top">Public audit boundary: <a href="PUBLIC_AUDIT_LIMITS.md"><code>PUBLIC_AUDIT_LIMITS.md</code></a></td>
  </tr>
</table>

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3.6.gif" alt="ZPE-XR Authority Insert" width="100%">
</p>
