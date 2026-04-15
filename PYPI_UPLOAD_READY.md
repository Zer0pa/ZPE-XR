<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>

<table align="center" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td width="33%"><a href="README.md"><img src=".github/assets/readme/nav/what-this-is.svg" alt="Front Door" width="100%"></a></td>
    <td width="33%"><a href="proofs/FINAL_STATUS.md"><img src=".github/assets/readme/nav/current-authority.svg" alt="Current Authority" width="100%"></a></td>
    <td width="33%"><a href="proofs/RELEASE_READINESS_REPORT.md"><img src=".github/assets/readme/nav/go-next.svg" alt="Release Readiness" width="100%"></a></td>
  </tr>
</table>

<p>
  <img src=".github/assets/readme/section-bars/release-notes.svg" alt="PYPI UPLOAD" width="100%">
</p>

# PyPI Upload Readiness

Current verdict: `PUBLISHED_PYPI` (v0.3.0)

zpe-xr v0.3.0 is published on PyPI. The modern comparator gate failed `0/5` (float16+zlib baseline beats ZPE-XR on fidelity on all 5 ContactPose sequences), so comparator-displacement claims remain unsupported, but the package itself is publicly installable.

## Environment

- `TWINE_USERNAME=__token__`
- `TWINE_PASSWORD=<pypi_api_token>`

## Validated Wheel

- `code/rust/zpe_xr_kernel/target/wheels/zpe_xr-0.3.0-cp314-cp314-macosx_10_12_x86_64.whl`

## Upload Command

```bash
python -m twine upload code/rust/zpe_xr_kernel/target/wheels/zpe_xr-0.3.0-cp314-cp314-macosx_10_12_x86_64.whl
```

<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>
