# Public Audit Limits

This note defines what the public ZPE-XR audit path can and cannot establish.

It is intentionally narrow. It keeps the public XR audit path honest without turning package mechanics, benchmark results, or current blockers into a pass narrative.

## What The Public Audit Path Can Establish

- the live acquisition surface at `https://github.com/Zer0pa/ZPE-XR.git`
- the package install/verify path using `python ./executable/verify.py`
- the current staged package version `0.3.0`
- the current primary benchmark identity in `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json`
- the cold-start audit and release-readiness machine surfaces
- the honest current verdict of `PRIVATE_ONLY` and `NOT_READY_FOR_PUBLIC_RELEASE`

## What The Public Audit Path Does Not Establish

- Unity or Meta runtime closure
- Photon displacement
- exact PRD corpus closure
- a public-release pass
- broader commercial or scientific diligence outside the shipped XR proof surface

## Public Audit Limits Matrix

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

## Feature Flags And Keys

No manual feature flags are required for the recommended public audit path:

- `python ./executable/verify.py`
- `python -m pytest ./code/tests -q`

No telemetry keys are required for that path:

- `COMET_API_KEY` is optional
- `OPIK_API_KEY` is optional

Any live-telemetry surfaces are subordinate to the local proof artifacts shipped in this repo.

## Honest Reading Rules

- Read ContactPose as the outward-safe benchmark lane, not as the exact PRD corpus.
- Read `PRIVATE_ONLY` and `NOT_READY_FOR_PUBLIC_RELEASE` as governing truth, not as a marketing delay.
- Read the failed modern comparator row as a real blocker, not as a soft caveat.
- Read `XR-C007 = PAUSED_EXTERNAL` as a runtime-closure blocker, not as an implied near-pass.
- Read package mechanics and release readiness separately: the package can be mechanically valid while the release gate is still closed.

## Use These Files Together

- `AUDITOR_PLAYBOOK.md`
- `README.md`
- `docs/FAQ.md`
- `docs/ARCHITECTURE.md`
- `docs/LEGAL_BOUNDARIES.md`
- `proofs/FINAL_STATUS.md`
- `proofs/RELEASE_READINESS_REPORT.md`
- `release_readiness.json`
