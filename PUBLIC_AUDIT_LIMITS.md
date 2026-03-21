<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>

<table align="center" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td width="33%"><a href="README.md"><img src=".github/assets/readme/nav/what-this-is.svg" alt="Front Door" width="100%"></a></td>
    <td width="33%"><a href="AUDITOR_PLAYBOOK.md"><img src=".github/assets/readme/nav/runtime-proof.svg" alt="Auditor Playbook" width="100%"></a></td>
    <td width="33%"><a href="GOVERNANCE.md"><img src=".github/assets/readme/nav/go-next.svg" alt="Governance" width="100%"></a></td>
  </tr>
</table>

<p>
  <img src=".github/assets/readme/section-bars/what-we-accept.svg" alt="PUBLIC AUDIT LIMITS" width="100%">
</p>

# Public Audit Limits

This file defines what the staged ZPE-XR repo can and cannot establish right now.

## Audit Limits Matrix

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="28%">Topic</th>
      <th align="left" width="24%">Status</th>
      <th align="left" width="48%">Evidence / Rationale</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Package candidate</td>
      <td>Established</td>
      <td><code>release_readiness.json</code> and install/verify path.</td>
    </tr>
    <tr>
      <td>Phase 5 ContactPose benchmark</td>
      <td>Established</td>
      <td><code>proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json</code></td>
    </tr>
    <tr>
      <td>Phase 4 ContactPose single-sequence</td>
      <td>Established</td>
      <td><code>proofs/artifacts/2026-03-21_zpe_xr_phase4_runpod_contactpose_124835Z/phase4_contactpose_benchmark.json</code></td>
    </tr>
    <tr>
      <td>Cold-start audit</td>
      <td>Established</td>
      <td><code>proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json</code></td>
    </tr>
    <tr>
      <td>Public release readiness</td>
      <td>Not established</td>
      <td>Modern comparator gate failed <code>0/5</code>.</td>
    </tr>
    <tr>
      <td>Photon displacement</td>
      <td>Not established</td>
      <td>Semantics mismatch; remains open.</td>
    </tr>
    <tr>
      <td>Runtime readiness (Unity/Meta)</td>
      <td>Not established</td>
      <td><code>XR-C007</code> remains <code>PAUSED_EXTERNAL</code>.</td>
    </tr>
    <tr>
      <td>Exact PRD corpus closure</td>
      <td>Not established</td>
      <td>ContactPose is outward-safe but not the exact PRD corpus.</td>
    </tr>
  </tbody>
</table>

## Known Limits

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="32%">Limit</th>
      <th align="left" width="68%">Detail</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Corpus scope</td>
      <td>ContactPose is outward-safe but not the exact PRD corpus.</td>
    </tr>
    <tr>
      <td>Release posture</td>
      <td>Package is mechanically valid but remains <code>PRIVATE_ONLY</code>.</td>
    </tr>
    <tr>
      <td>Historical lineage</td>
      <td>Legacy bundles removed; request legacy lineage if needed.</td>
    </tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>
