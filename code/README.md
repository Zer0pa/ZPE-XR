# zpe-xr

Private-stage Python package for the ZPE-XR codec and evaluation harness.

## Install

```bash
pip install -e "./code[dev]"
```

## Package Surface

- `zpe_xr.XRCodec`
- `zpe_xr.EncoderState`
- `zpe_xr.DecoderState`
- `zpe_xr.Frame`
- `zpe_xr.FrameSequence`

## Included Repo-Local Surfaces

- `src/zpe_xr/`: package code
- `tests/`: deterministic regression surface
- `scripts/`: historical gate scripts adapted to the repo layout
- `fixtures/`: synthetic fixtures and resource lock metadata

This package README does not claim public-release readiness. Use the repo-root
docs and proof files for current status.
