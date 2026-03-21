<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>

<table align="center" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td width="33%"><a href="../README.md"><img src="../.github/assets/readme/nav/what-this-is.svg" alt="Front Door" width="100%"></a></td>
    <td width="33%"><a href="README.md"><img src="../.github/assets/readme/nav/go-next.svg" alt="Docs Index" width="100%"></a></td>
    <td width="33%"><a href="SUPPORT.md"><img src="../.github/assets/readme/nav/quickstart-and-license.svg" alt="Support" width="100%"></a></td>
  </tr>
</table>

<p>
  <img src="../.github/assets/readme/section-bars/questions.svg" alt="FAQ" width="100%">
</p>

# FAQ

## What is ZPE-XR?

A deterministic XR hand-stream codec and evaluation harness for compression, network resilience, and gesture scoring. It is a private-stage package candidate, not a public release.

## Is this repo public-ready?

No. The current verdict is `PRIVATE_ONLY` and `NOT_READY_FOR_PUBLIC_RELEASE`.

## Is this available on PyPI?

No. The only supported acquisition surface is a local checkout.

## What is the current authority anchor?

The Phase 5 ContactPose multi-sequence run and the release-readiness verdict:

<table width="100%" border="1" bordercolor="#b8c0ca" cellpadding="0" cellspacing="0">
  <thead>
    <tr>
      <th align="left" width="28%">Anchor</th>
      <th align="left" width="52%">Value</th>
      <th align="left" width="20%">Evidence</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Authority run</td>
      <td>Phase 5 ContactPose multi-sequence</td>
      <td><code>proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json</code></td>
    </tr>
    <tr>
      <td>Release verdict</td>
      <td><code>PRIVATE_ONLY</code>, <code>NOT_READY_FOR_PUBLIC_RELEASE</code></td>
      <td><code>proofs/RELEASE_READINESS_REPORT.md</code></td>
    </tr>
    <tr>
      <td>Claim boundary</td>
      <td>Runtime closure and public release blocked</td>
      <td><code>proofs/FINAL_STATUS.md</code></td>
    </tr>
  </tbody>
</table>

## Does this repo prove runtime readiness?

No. `XR-C007` remains `PAUSED_EXTERNAL` pending device/editor and license clearance.

## What is the fastest local sanity check?

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install "./code[dev]"
python ./executable/verify.py
```

## Where are the authoritative metrics?

Use the Phase 5 multi-sequence benchmark artifact and the staged status report:

- `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.md`
- `proofs/FINAL_STATUS.md`

<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>
