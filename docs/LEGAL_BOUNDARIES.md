# Legal Boundaries

This note is a release-surface summary only. `../LICENSE` is the legal source of truth for Zer0pa Source-Available License v6.0 (SAL v6.0).

## Package Surfaces

- `code/pyproject.toml` is governed by the root `LICENSE`.
- `code/rust/zpe_xr_kernel/Cargo.toml` is an internal crate under the root `LICENSE`.
- `code/source/zpe_xr/` is the shipped package source surface under the root `LICENSE`.
- `release_readiness.json` is package/readiness metadata, not an independent license surface.

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

## Claim Discipline

Historical or aspirational prose does not outrank:

- `proofs/FINAL_STATUS.md`
- `proofs/RELEASE_READINESS_REPORT.md`
- `PUBLIC_AUDIT_LIMITS.md`

Package validity, benchmark validity, runtime closure, and public-release readiness must stay separated. A real package surface does not automatically create a real runtime-closure or public-release claim.
