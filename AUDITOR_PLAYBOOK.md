<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>

<table align="center" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td width="33%"><a href="README.md"><img src=".github/assets/readme/nav/what-this-is.svg" alt="Front Door" width="100%"></a></td>
    <td width="33%"><a href="PUBLIC_AUDIT_LIMITS.md"><img src=".github/assets/readme/nav/runtime-proof.svg" alt="Audit Limits" width="100%"></a></td>
    <td width="33%"><a href="docs/ARCHITECTURE.md"><img src=".github/assets/readme/nav/go-next.svg" alt="Architecture" width="100%"></a></td>
  </tr>
</table>

<p>
  <img src=".github/assets/readme/section-bars/verification.svg" alt="SHORTEST AUDIT PATH" width="100%">
</p>

# Auditor Playbook

This is the shortest honest audit path for the current private-stage package candidate.

## Shortest Staged Audit Path

1. Clone or use the staged repo.
2. Create an environment and install the package:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install "./code[dev]"
```

3. Run the staged verification entrypoint:

```bash
python ./executable/verify.py
```

4. Optional test replay:

```bash
python -m pytest ./code/tests -q
```

<p>
  <img src=".github/assets/readme/section-bars/proof-corpus.svg" alt="WHAT TO INSPECT" width="100%">
</p>

## What To Inspect

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="38%">Artifact</th>
      <th align="left" width="62%">Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>proofs/FINAL_STATUS.md</code></td>
      <td>Claim boundary and current status.</td>
    </tr>
    <tr>
      <td><code>proofs/RELEASE_READINESS_REPORT.md</code></td>
      <td>Release verdict and blockers.</td>
    </tr>
    <tr>
      <td><code>release_readiness.json</code></td>
      <td>Machine-readable release readiness.</td>
    </tr>
    <tr>
      <td><code>proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json</code></td>
      <td>Primary authority benchmark.</td>
    </tr>
    <tr>
      <td><code>proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json</code></td>
      <td>Cold-start audit evidence.</td>
    </tr>
    <tr>
      <td><code>proofs/artifacts/2026-03-21_zpe_xr_phase4_runpod_contactpose_124835Z/phase4_contactpose_benchmark.json</code></td>
      <td>Phase 4 single-sequence benchmark.</td>
    </tr>
    <tr>
      <td><code>PUBLIC_AUDIT_LIMITS.md</code></td>
      <td>Scope boundary for external readers.</td>
    </tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/section-bars/summary.svg" alt="EXPECTED CURRENT READING" width="100%">
</p>

## Expected Current Reading

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="42%">Check</th>
      <th align="left" width="58%">Expected Read</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Package surface</td>
      <td>Imports from <code>code/source</code>; Rust backend present.</td>
    </tr>
    <tr>
      <td>Authority run</td>
      <td>Phase 5 ContactPose multi-sequence benchmark.</td>
    </tr>
    <tr>
      <td>Comparator gate</td>
      <td>Modern comparator failed <code>0/5</code>; blocks public release.</td>
    </tr>
    <tr>
      <td>Runtime closure</td>
      <td><code>XR-C007</code> remains <code>PAUSED_EXTERNAL</code>.</td>
    </tr>
    <tr>
      <td>Release readiness</td>
      <td><code>NOT_READY_FOR_PUBLIC_RELEASE</code>.</td>
    </tr>
  </tbody>
</table>

<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>
