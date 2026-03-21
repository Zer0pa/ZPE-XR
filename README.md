<h1 align="center">ZPE-XR</h1>

<p align="center">
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>
<p align="center">
  <img src=".github/assets/readme/zpe-masthead-option-3-2.gif" alt="ZPE-XR Masthead Variant" width="100%">
</p>
<p align="center">
  <img src=".github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-XR Masthead Variant" width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-SAL%20v6.0-e5e7eb?labelColor=111111" alt="License: SAL v6.0"></a>
  <a href="proofs/FINAL_STATUS.md"><img src="https://img.shields.io/badge/authority-2026--03--21-e5e7eb?labelColor=111111" alt="Authority: 2026-03-21"></a>
  <a href="release_readiness.json"><img src="https://img.shields.io/badge/release-private%20only-e5e7eb?labelColor=111111" alt="Release: private only"></a>
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

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

<a id="what-this-is"></a>
<h2 align="center">What This Is</h2>

ZPE-XR is a private-stage package candidate for an XR hand-stream codec and evaluation harness. The repo is buildable and inspectable, but it is not a public release and it does not claim device runtime closure.

<p>
  <img src=".github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

<a id="current-authority"></a>
<h2 align="center">Current Authority (2026-03-21)</h2>

<table width="100%" border="1" bordercolor="#111111" cellpadding="14" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="26%">Surface</th>
      <th align="left" width="34%">Locked Value</th>
      <th align="left" width="40%">Evidence</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td valign="top">Phase 5 ContactPose multi-sequence</td>
      <td valign="top">See Current Metrics table below.</td>
      <td valign="top"><a href="proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json"><code>proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json</code></a></td>
    </tr>
    <tr>
      <td valign="top">Release verdict</td>
      <td valign="top">`PRIVATE_ONLY`, `NOT_READY_FOR_PUBLIC_RELEASE`</td>
      <td valign="top"><a href="proofs/RELEASE_READINESS_REPORT.md"><code>proofs/RELEASE_READINESS_REPORT.md</code></a></td>
    </tr>
    <tr>
      <td valign="top">Package mechanics</td>
      <td valign="top">Version `0.3.0`, Rust-backed wheel validated, `twine check` PASS</td>
      <td valign="top"><a href="release_readiness.json"><code>release_readiness.json</code></a></td>
    </tr>
    <tr>
      <td valign="top">Cold-start audit</td>
      <td valign="top">PASS, Comet logging disabled (key null)</td>
      <td valign="top"><a href="proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json"><code>proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json</code></a></td>
    </tr>
  </tbody>
</table>

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
      <td valign="top">Mean fidelity on ContactPose.</td>
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
      <td valign="top">Gate failed; blocks public release decision.</td>
    </tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/section-bars/out-of-scope.svg" alt="STATUS AND GAPS" width="100%">
</p>

<a id="status-and-gaps"></a>
<h2 align="center">Status and Gaps</h2>

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
      <td valign="top">Modern comparator gate failed (`0/5`).</td>
      <td valign="top">Blocks public release.</td>
    </tr>
    <tr>
      <td valign="top">Runtime closure</td>
      <td valign="top">`XR-C007` remains `PAUSED_EXTERNAL`.</td>
      <td valign="top">Blocks runtime-closure claims.</td>
    </tr>
    <tr>
      <td valign="top">Comparator displacement</td>
      <td valign="top">Photon displacement open (secondary).</td>
      <td valign="top">No incumbent displacement claim.</td>
    </tr>
    <tr>
      <td valign="top">Exact PRD corpus</td>
      <td valign="top">Exact PRD corpus unresolved.</td>
      <td valign="top">Limits corpus claims.</td>
    </tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/section-bars/quick-start.svg" alt="ACQUISITION SURFACE" width="100%">
</p>

<a id="acquisition-surface"></a>
<h2 align="center">Acquisition Surface (Private/Internal Only)</h2>

Private/internal only. Not on PyPI. Supported install: local checkout:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install "./code[dev]"
python ./executable/verify.py
```

Optional test replay:

```bash
python -m pytest ./code/tests -q
```

<p>
  <img src=".github/assets/readme/section-bars/where-to-go.svg" alt="GO NEXT" width="100%">
</p>

<a id="go-next"></a>
<h2 align="center">Go Next</h2>

Start: `proofs/FINAL_STATUS.md`, `proofs/RELEASE_READINESS_REPORT.md`  
Evidence (latest): `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.md`  
Docs: `docs/README.md`, `docs/ARCHITECTURE.md`, `docs/FAQ.md`  
Audit: `AUDITOR_PLAYBOOK.md`, `PUBLIC_AUDIT_LIMITS.md`

<p>
  <img src=".github/assets/readme/section-bars/contributing-security-support.svg" alt="CONTRIBUTING, SECURITY, SUPPORT" width="100%">
</p>

<a id="contributing-security-support"></a>
<h2 align="center">Contributing, Security, Support</h2>

<table width="100%" border="1" bordercolor="#111111" cellpadding="16" cellspacing="0">
  <tr>
    <td width="33%" valign="top">Contribution workflow: <a href="CONTRIBUTING.md"><code>CONTRIBUTING.md</code></a></td>
    <td width="33%" valign="top">Security policy and reporting: <a href="SECURITY.md"><code>SECURITY.md</code></a></td>
    <td width="34%" valign="top">Support channel guide: <a href="docs/SUPPORT.md"><code>docs/SUPPORT.md</code></a></td>
  </tr>
  <tr>
    <td width="33%" valign="top">Frequently asked questions: <a href="docs/FAQ.md"><code>docs/FAQ.md</code></a></td>
    <td colspan="2" width="67%" valign="top">Public audit boundaries: <a href="PUBLIC_AUDIT_LIMITS.md"><code>PUBLIC_AUDIT_LIMITS.md</code></a></td>
  </tr>
</table>

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-XR Lower Masthead" width="100%">
</p>
