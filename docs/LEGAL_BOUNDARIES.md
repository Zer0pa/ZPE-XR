<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>

<table align="center" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td width="50%"><a href="../README.md"><img src="../.github/assets/readme/nav/what-this-is.svg" alt="Front Door" width="100%"></a></td>
    <td width="50%"><a href="../GOVERNANCE.md"><img src="../.github/assets/readme/nav/go-next.svg" alt="Governance" width="100%"></a></td>
  </tr>
</table>

<p>
  <img src="../.github/assets/readme/section-bars/license-and-ip.svg" alt="LICENSE AND IP" width="100%">
</p>

# Legal Boundaries

This document is an operational summary, not legal advice.

## Repository License

- software license: `LicenseRef-Zer0pa-SAL-6.0`
- legal source of truth: `LICENSE`
- licensing contact: `architects@zer0pa.ai`

<p>
  <img src="../.github/assets/readme/section-bars/scope.svg" alt="DATASET AND RUNTIME BOUNDARIES" width="100%">
</p>

## Dataset And Runtime Boundaries

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="22%">Area</th>
      <th align="left" width="38%">Boundary</th>
      <th align="left" width="20%">Status</th>
      <th align="left" width="20%">Evidence Anchor</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ContactPose</td>
      <td>Outward-safe corpus lane only; not the exact PRD corpus.</td>
      <td>Allowed (limited)</td>
      <td><code>proofs/FINAL_STATUS.md</code></td>
    </tr>
    <tr>
      <td>HOT3D</td>
      <td>Historical benchmarking context only; public/commercial use caveated.</td>
      <td>Restricted</td>
      <td><code>proofs/FINAL_STATUS.md</code></td>
    </tr>
    <tr>
      <td>MANO</td>
      <td>Registration/licensing unresolved; blocks runtime retarget closure.</td>
      <td>Blocked</td>
      <td><code>proofs/FINAL_STATUS.md</code></td>
    </tr>
    <tr>
      <td>HOI-M3 / HO-Cap</td>
      <td>External corpus access and executable closure not established.</td>
      <td>Not established</td>
      <td><code>PUBLIC_AUDIT_LIMITS.md</code></td>
    </tr>
    <tr>
      <td>Unity / Meta XR SDK</td>
      <td>Runtime integration remains externally gated.</td>
      <td>Blocked</td>
      <td><code>proofs/FINAL_STATUS.md</code></td>
    </tr>
  </tbody>
</table>

<p>
  <img src="../.github/assets/readme/section-bars/evidence-and-claims.svg" alt="CLAIM DISCIPLINE" width="100%">
</p>

## Claim Discipline

This repo may describe historical artifacts, but historical prose does not outrank the current staged claim-boundary notes in `proofs/FINAL_STATUS.md` and `PUBLIC_AUDIT_LIMITS.md`.

<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>
