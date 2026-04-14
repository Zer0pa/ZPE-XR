<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>

# Final Status

This document is the current staged reading of the XR evidence boundary.

## Current Authority

- Phase 5 ContactPose multi-sequence (2026-04-14 rerun): mean compression `23.90x`, mean MPJPE `0.479 mm`, mean latency `0.057 ms`, mean loss error `0.399%`, modern comparator passes `0/5`. Anchor: `proofs/artifacts/2026-04-14_zpe_xr_live_014204/phase5_multi_sequence_benchmark.json`.
- Phase 4 ContactPose single-sequence (historical): compression figure was `56.144x` in the original run but has been superseded by the 2026-04-14 rerun at `23.90x`. Anchor: `proofs/artifacts/2026-03-21_zpe_xr_phase4_runpod_contactpose_124835Z/phase4_contactpose_benchmark.json`.
- Phase 4 cold-start audit: `PASS`, Comet logging disabled (key null). Anchor: `proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json`.
- Package mechanics: Rust backend, `twine check` PASS, version `0.3.0`. Anchor: `release_readiness.json`.

## Comparator Boundary

- Modern comparator gate failed `0/5` on Phase 5 multi-sequence; this blocks public release.
- Photon displacement remains open and secondary.
- Legacy comparator lanes were removed from the repo to keep the authority surface lean.

## Corpus Boundary

- ContactPose lanes are the outward-safe corpus boundary (single-sequence and multi-sequence `PASS`).
- Exact PRD corpus remains unresolved.

## Runtime Boundary

- `XR-C007` remains `PAUSED_EXTERNAL` due to device/editor/license constraints.

## Current Verdict

- outward-safe workload: ContactPose `PASS`
- package candidate: `PASS`
- cold-start trust: `PASS`
- outward channel: `PRIVATE_ONLY`
- public release readiness: `NOT_READY_FOR_PUBLIC_RELEASE`

<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>
