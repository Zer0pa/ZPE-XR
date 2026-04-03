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

<table align="center" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td width="20%"><a href="#what-this-is"><img src=".github/assets/readme/nav/what-this-is.svg" alt="What This Is" width="100%"></a></td>
    <td width="20%"><a href="#current-authority"><img src=".github/assets/readme/nav/current-authority.svg" alt="Current Authority" width="100%"></a></td>
    <td width="20%"><a href="#current-metrics"><img src=".github/assets/readme/nav/throughput.svg" alt="Current Metrics" width="100%"></a></td>
    <td width="20%"><a href="#acquisition-surface"><img src=".github/assets/readme/nav/quickstart-and-license.svg" alt="Acquisition Surface" width="100%"></a></td>
    <td width="20%"><a href="#go-next"><img src=".github/assets/readme/nav/go-next.svg" alt="Go Next" width="100%"></a></td>
  </tr>
</table>

---

## What This Is

ZPE-XR is a deterministic hand-pose transport codec for XR two-hand joint streams, optimized for package truth, replay discipline, and bounded benchmark evidence.

## Commercial Wedge

This is for **XR platform teams, headset ecosystem teams, gesture runtime teams, and spatial-computing infrastructure teams** who need deterministic hand-stream transport with measurable fidelity, bandwidth reduction, and auditable replay. The business value is reproducible hand-pose delivery at sub-millimeter fidelity (0.479 mm MPJPE), 56× compression, and sub-millisecond encode/decode latency — with every claim traceable to committed benchmark artifacts.

## Technical Wedge

The technical edge is a deterministic two-hand joint codec with ContactPose benchmark evidence: **MPJPE 0.479 mm**, **56.144× compression vs raw**, **0.026 ms encode+decode latency**. Package mechanics are real and installable. Runtime closure on Unity/Meta targets remains an open engineering gate.

## Current Readiness

**`PRIVATE_STAGE`** — ContactPose benchmark lane and package mechanics are real. Modern comparator gate (0/5) and Unity/Meta runtime closure are open blockers for public release.

## What Is Proved

- ContactPose benchmark fidelity: 0.479 mm mean per-joint position error
- 56.144× compression ratio vs raw joint streams
- 0.026 ms combined encode+decode latency
- Package mechanics: installable, testable, and locally verifiable
- Deterministic replay on the tested surface

## What Is Not Being Claimed

- Public release readiness — modern comparator gate not closed
- Unity or Meta runtime closure — XR-C007 is PAUSED_EXTERNAL
- Photon displacement claim — not yet evidenced
- Exact PRD corpus closure — ContactPose is the current safe lane, not the full target
- Broad hand-tracking superiority — claims are bounded to the ContactPose benchmark surface

## Ideal First Buyer

XR platform team or spatial-computing infrastructure team building deterministic hand-stream transport for headset or gesture-runtime pipelines.

## Deployment Model

SDK — Python package candidate with repo-local evaluation harness. Private repo checkout today; public package when comparator and runtime gates close.

## Authority / Proof Anchors

| Anchor | Artifact |
|---|---|
| Phase 5 multi-sequence benchmark | [`proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json`](proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json) |
| Release readiness report | [`proofs/RELEASE_READINESS_REPORT.md`](proofs/RELEASE_READINESS_REPORT.md) |
| Final status | [`proofs/FINAL_STATUS.md`](proofs/FINAL_STATUS.md) |

## Role In The Zer0pa Family

ZPE-XR is a product-candidate member of the Zer0pa deterministic encoding family. [ZPE-IMC](https://github.com/Zer0pa/ZPE-IMC) is the umbrella integration and dispatch layer; this repo is the domain-specific XR hand-stream wedge.

---

<a id="quickstart-and-license"></a>
<h2 align="center">Quickstart And License</h2>

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

License boundary:

- Free use at or below the SAL v6.0 threshold; see `LICENSE` for exact terms.
- SPDX identifier: `LicenseRef-Zer0pa-SAL-6.0`.
- Commercial, hosted, or legal-interpretation questions route to `architects@zer0pa.ai`.
- The release posture remains `PRIVATE_ONLY` until the comparator and runtime gates are actually closed.

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3.4.gif" alt="ZPE-XR Upper Insert" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

<a id="what-this-is"></a>
<h2 align="center">What This Is</h2>

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

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3.5.gif" alt="ZPE-XR Lower Insert" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

<a id="current-authority"></a>
<h2 align="center">Current Authority (2026-03-21)</h2>

<table width="100%" border="1" bordercolor="#111111" cellpadding="14" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="24%">Surface</th>
      <th align="left" width="36%">Locked Value</th>
      <th align="left" width="40%">Evidence</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td valign="top">Primary benchmark authority</td>
      <td valign="top">Phase 5 ContactPose multi-sequence run</td>
      <td valign="top"><a href="proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json"><code>proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json</code></a></td>
    </tr>
    <tr>
      <td valign="top">Release verdict</td>
      <td valign="top"><code>PRIVATE_ONLY</code>, <code>NOT_READY_FOR_PUBLIC_RELEASE</code></td>
      <td valign="top"><a href="proofs/RELEASE_READINESS_REPORT.md"><code>proofs/RELEASE_READINESS_REPORT.md</code></a></td>
    </tr>
    <tr>
      <td valign="top">Package mechanics</td>
      <td valign="top">Version <code>0.3.0</code>, Rust-backed build, wheel path validated, <code>twine check</code> PASS</td>
      <td valign="top"><a href="release_readiness.json"><code>release_readiness.json</code></a></td>
    </tr>
    <tr>
      <td valign="top">Cold-start audit</td>
      <td valign="top">PASS, local-only logging posture retained</td>
      <td valign="top"><a href="proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json"><code>proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json</code></a></td>
    </tr>
    <tr>
      <td valign="top">External acquisition surface</td>
      <td valign="top"><code>https://github.com/Zer0pa/ZPE-XR.git</code></td>
      <td valign="top">This repository and its current `main` branch are the live XR authority surface.</td>
    </tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/section-bars/runtime-proof-wave-1.svg" alt="PROOF SURFACE" width="100%">
</p>

<a id="proof-surface"></a>
<h2 align="center">Proof Surface</h2>

All promoted XR claims are bounded by concrete proof artifacts. Read the package result, the release verdict, and the benchmark anchors together.

<table width="100%" border="1" bordercolor="#111111" cellpadding="16" cellspacing="0">
  <tr>
    <td width="50%" valign="top">
      <strong>Final status</strong><br>
      <a href="proofs/FINAL_STATUS.md"><code>proofs/FINAL_STATUS.md</code></a><br><br>
      Current claim boundary, runtime boundary, corpus boundary, and verdict summary.
    </td>
    <td width="50%" valign="top">
      <strong>Release readiness</strong><br>
      <a href="proofs/RELEASE_READINESS_REPORT.md"><code>proofs/RELEASE_READINESS_REPORT.md</code></a><br><br>
      Public-release verdict and blocker list for the current staged package.
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <strong>Primary benchmark</strong><br>
      <a href="proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json"><code>phase5_multi_sequence_benchmark.json</code></a><br><br>
      Mean compression, fidelity, latency, packet-loss, and comparator-gate values across five ContactPose sequences.
    </td>
    <td width="50%" valign="top">
      <strong>Cold-start and package mechanics</strong><br>
      <a href="proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json"><code>phase4_cold_start_audit.json</code></a><br>
      <a href="release_readiness.json"><code>release_readiness.json</code></a><br><br>
      Installability, import surface, and staged runtime hygiene.
    </td>
  </tr>
</table>

### Proof Anchors

<table width="100%" border="1" bordercolor="#111111" cellpadding="14" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="38%">Artifact</th>
      <th align="left" width="62%">Why it matters</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td valign="top"><a href="proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json"><code>proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json</code></a></td>
      <td valign="top">Current benchmark authority for compression, fidelity, latency, packet loss, and the failed modern-comparator row.</td>
    </tr>
    <tr>
      <td valign="top"><a href="proofs/artifacts/2026-03-21_zpe_xr_phase4_runpod_contactpose_124835Z/phase4_contactpose_benchmark.json"><code>proofs/artifacts/2026-03-21_zpe_xr_phase4_runpod_contactpose_124835Z/phase4_contactpose_benchmark.json</code></a></td>
      <td valign="top">Single-sequence ContactPose anchor retained as historical-but-still-live evidence.</td>
    </tr>
    <tr>
      <td valign="top"><a href="proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json"><code>proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json</code></a></td>
      <td valign="top">Cold-start audit for the staged outward package surface.</td>
    </tr>
    <tr>
      <td valign="top"><a href="release_readiness.json"><code>release_readiness.json</code></a></td>
      <td valign="top">Machine-readable package and release-readiness summary.</td>
    </tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-2.gif" alt="ZPE-XR Mid Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/throughput.svg" alt="CURRENT METRICS" width="100%">
</p>

<a id="current-metrics"></a>
<h2 align="center">Current Metrics (Phase 5 ContactPose)</h2>

<table width="100%" border="1" bordercolor="#111111" cellpadding="14" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="28%">Metric</th>
      <th align="left" width="20%">Value</th>
      <th align="left" width="52%">Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td valign="top">Compression vs raw</td>
      <td valign="top"><code>56.144x</code></td>
      <td valign="top">Mean across five ContactPose sequences.</td>
    </tr>
    <tr>
      <td valign="top">MPJPE</td>
      <td valign="top"><code>0.479 mm</code></td>
      <td valign="top">Mean fidelity on the outward-safe ContactPose lane.</td>
    </tr>
    <tr>
      <td valign="top">Encode+decode latency</td>
      <td valign="top"><code>0.026 ms</code></td>
      <td valign="top">Mean per-frame combined latency.</td>
    </tr>
    <tr>
      <td valign="top">Pose error at 10% loss</td>
      <td valign="top"><code>0.399%</code></td>
      <td valign="top">Mean packet-loss resilience.</td>
    </tr>
    <tr>
      <td valign="top">Modern comparator gate</td>
      <td valign="top"><code>0/5</code></td>
      <td valign="top">This failure blocks the public-release verdict.</td>
    </tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/section-bars/out-of-scope.svg" alt="STATUS AND GAPS" width="100%">
</p>

<a id="status-and-gaps"></a>
<h2 align="center">Status And Gaps</h2>

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
  <img src=".github/assets/readme/section-bars/quick-start.svg" alt="ACQUISITION SURFACE" width="100%">
</p>

<a id="acquisition-surface"></a>
<h2 align="center">Acquisition Surface</h2>

Current live repo:

- clone target: <code>https://github.com/Zer0pa/ZPE-XR.git</code>
- package metadata: <code>code/pyproject.toml</code>
- install/verify path: <code>python ./executable/verify.py</code>
- optional direct replay: <code>python -m pytest ./code/tests -q</code>

Not provided today:

- no PyPI release
- no public-release verdict
- no runtime-closure pass narrative

<p>
  <img src=".github/assets/readme/section-bars/where-to-go.svg" alt="GO NEXT" width="100%">
</p>

<a id="go-next"></a>
<h2 align="center">Go Next</h2>

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
<h2 align="center">Contributing, Security, Support</h2>

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
