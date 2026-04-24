# Falsification Report (2026-03-21)

This report records doc-surface falsification findings and the fixes applied during this pass.

Related surfaces:

- Front door: `../README.md`
- Architecture index: `ARCHITECTURE.md`

## Unsupported Claims Removed Or Downgraded

- Removed or downgraded any public-release language to `PRIVATE_ONLY` in the front door and supporting docs.
- Removed modern-comparator displacement claims; the Phase 5 gate failed `0/5` and blocks public release.
- Replaced Wave-1 (2026-02-20) anchors with the current 2026-03-21 evidence chain where authoritative.
- Removed the Phase 4 cold-start Comet key claim; audit evidence shows logging disabled (key null).
- Removed `code/src` as a canonical runtime root; docs now point to `code/source` and the Rust-backed package surface.
- Removed legacy artifact bundles and updated docs to remove stale anchors.
- Updated citation and changelog language to reflect the removal of legacy bundles.

## Path And Render Issues Found

- Missing local visual assets in this repo: broken asset references were removed from the public docs surface.
- Stale references to editable install and `code/src` paths: corrected across docs and runbooks.
- Broken docs navigation links were narrowed to the existing front door and architecture surfaces.
- Legacy artifact folders and gate runbooks were removed to keep the repo lean; proofs map updated accordingly.

## Remaining Owner Inputs

- Runtime closure for `XR-C007` remains `PAUSED_EXTERNAL` pending device/editor availability and license clearance.
- Exact PRD corpus remains unresolved.
- Photon displacement remains open/secondary.

## Live Versus Local Drift

- Local docs are updated to the 2026-03-21 authority chain and private-only status.
- After pushing this commit, confirm the private GitHub render matches the local state.
