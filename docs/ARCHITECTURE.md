<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>

<table align="center" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td width="50%"><a href="../README.md"><img src="../.github/assets/readme/nav/what-this-is.svg" alt="Front Door" width="100%"></a></td>
    <td width="50%"><a href="README.md"><img src="../.github/assets/readme/nav/go-next.svg" alt="Docs Index" width="100%"></a></td>
  </tr>
</table>

<p>
  <img src="../.github/assets/readme/section-bars/repo-shape.svg" alt="REPO MAP" width="100%">
</p>

# Architecture

## Repo Map

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Path</th>
      <th align="left">Role</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>code/source/zpe_xr/</code></td>
      <td>Canonical Python runtime surface.</td>
    </tr>
    <tr>
      <td><code>code/rust/zpe_xr_kernel/</code></td>
      <td>Rust kernel and PyO3 extension.</td>
    </tr>
    <tr>
      <td><code>code/tests/</code></td>
      <td>Deterministic test suite.</td>
    </tr>
    <tr>
      <td><code>code/scripts/</code></td>
      <td>Gate, phase, and verification scripts.</td>
    </tr>
    <tr>
      <td><code>executable/verify.py</code></td>
      <td>Repo-local verification harness.</td>
    </tr>
    <tr>
      <td><code>proofs/</code></td>
      <td>Evidence corpus, release readiness, and runbooks.</td>
    </tr>
  </tbody>
</table>

<p>
  <img src="../.github/assets/readme/section-bars/evidence-and-claims.svg" alt="AUTHORITY CLASSES" width="100%">
</p>

## Authority Classes

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="22%">Class</th>
      <th align="left" width="45%">Definition</th>
      <th align="left" width="33%">Primary Evidence</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Runtime truth</td>
      <td>Executable package surface and Rust backend behavior.</td>
      <td><code>code/source/</code>, <code>code/rust/</code>, <code>release_readiness.json</code></td>
    </tr>
    <tr>
      <td>Proof authority</td>
      <td>Staged evidence and claim boundaries.</td>
      <td><code>proofs/FINAL_STATUS.md</code>, <code>proofs/RELEASE_READINESS_REPORT.md</code></td>
    </tr>
    <tr>
      <td>Audit boundary</td>
      <td>External verification and public limits.</td>
      <td><code>AUDITOR_PLAYBOOK.md</code>, <code>PUBLIC_AUDIT_LIMITS.md</code></td>
    </tr>
  </tbody>
</table>

<p>
  <img src="../.github/assets/readme/section-bars/architecture-and-theory.svg" alt="RUNTIME SHAPE" width="100%">
</p>

## Runtime Shape

The package implements a deterministic codec for two-hand joint streams and ships a Rust-backed extension. It provides:

- keyframe and delta packet encoding
- bounded packet parsing and checksum validation
- realtime loss recovery with concealment and backup deltas
- metric helpers for compression, fidelity, bandwidth, and latency
- a Unity-envelope compatibility layer for evaluation only

<p>
  <img src="../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION SURFACES" width="100%">
</p>

## Verification Surfaces

- Package verification: `executable/verify.py`
- Evidence boundary: `proofs/FINAL_STATUS.md`
- Release verdict: `proofs/RELEASE_READINESS_REPORT.md`
- Phase 5 benchmark: `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json`

<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>
