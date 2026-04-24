<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>

<p>
  <img src="../.github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

This document is the architecture index for the current ZPE-XR runtime and proof surface.

Canonical anchors:

- External acquisition surface: `https://github.com/Zer0pa/ZPE-XR.git`
- Contact: `architects@zer0pa.ai`
- Python package root: `code/source/zpe_xr`
- Rust kernel crate: `code/rust/zpe_xr_kernel`
- Verification entrypoint: `executable/verify.py`
- Governing proof surfaces: `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_release_decision.md` and `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_surface_adjudication.md`

<p>
  <img src="../.github/assets/readme/section-bars/interface-contracts.svg" alt="INTERFACE CONTRACTS" width="100%">
</p>

| Surface | Role | Canonical path |
|---|---|---|
| Public API | Package entrypoints for encode/decode/gesture/info | `code/source/zpe_xr/__init__.py`, `code/source/zpe_xr/api.py` |
| Codec envelope | Packet encode/parse and recovery logic | `code/source/zpe_xr/codec.py` |
| Verification path | Repo-local install and smoke verification | `executable/verify.py` |
| Evidence authority | Claim boundary and release verdict | `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_release_decision.md`, `proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_surface_adjudication.md` |
| Proxy benchmark lanes | Same-machine proxy evidence, not runtime displacement | `proofs/artifacts/2026-03-29_zpe_xr_phase7_ultraleap_local/phase7_ultraleap_local_benchmark.md`, `proofs/artifacts/2026-03-29_zpe_xr_phase8_photon_local/phase8_photon_local_benchmark.md` |
| Machine-readable package state | Current product/wedge summary | `docs/market_surface.json` |

<p>
  <img src="../.github/assets/readme/section-bars/word-layout.svg" alt="WORD LAYOUT" width="100%">
</p>

The XR packet envelope in `code/source/zpe_xr/codec.py` is packet-based rather than a single fixed token word. The governing packet fields are:

| Envelope field | Source |
|---|---|
| `magic`, `version`, `flags` | `_HEADER_STRUCT = struct.Struct("<3sBBHHIBB")` |
| `seq`, `backup_seq`, `timestamp_ms` | `_HEADER_STRUCT` |
| `current_count`, `backup_count` | `_HEADER_STRUCT` |
| keyframe quantized joints or delta entries | `_QVEC_STRUCT`, `_ENTRY_STRUCT` |
| CRC32 checksum tail | `_CHECKSUM_STRUCT` |

<p>
  <img src="../.github/assets/readme/section-bars/modality-markers.svg" alt="MODALITY MARKERS" width="100%">
</p>

Primary runtime and evaluation surfaces:

- `XRCodec`, `EncoderState`, `DecoderState` for codec mechanics
- `encode`, `decode`, `gesture_match`, `codec_info` for package API
- `network.py` for sequence encode/decode and loss-recovery evaluation
- `external_benchmarks.py` for comparator measurement surfaces
- `unity.py` for the Unity-envelope compatibility layer used in evaluation

<p>
  <img src="../.github/assets/readme/section-bars/dispatch-precedence.svg" alt="DISPATCH PRECEDENCE" width="100%">
</p>

When repo surfaces disagree, use this precedence:

1. current proof artifacts and adjudication docs
2. `docs/market_surface.json`
3. package/runtime docs
4. historical or narrative prose

<p>
  <img src="../.github/assets/readme/section-bars/open-risks-non-blocking.svg" alt="OPEN RISKS (NON-BLOCKING)" width="100%">
</p>

Deployment guardrails for architecture readers:

- package validity does not imply public-release validity
- the comparator gate is still failed at `0/5`
- runtime closure remains `PAUSED_EXTERNAL`
- ContactPose is the current outward-safe lane, not the exact PRD corpus
