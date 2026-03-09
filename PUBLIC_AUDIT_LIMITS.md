# Public Audit Limits

This file defines what the staged ZPE-XR repo can and cannot establish.

The repo is private staged on 2026-03-09. This note still uses the
public/private language so the eventual publication boundary stays explicit.

## What This Staged Repo Can Establish

- the current repo boundary and package layout
- the presence of runnable codec code under `code/`
- the presence of a preserved historical Wave-1 evidence bundle
- the current claim-boundary reading documented in `proofs/FINAL_STATUS.md`

## What This Staged Repo Does Not Establish

- public-release readiness
- blind-clone verification for this exact snapshot
- HOT3D-backed full claim closure from the checked-in scripts
- external-corpus closure for HOI-M3 or HO-Cap
- production Unity/Meta runtime readiness

## Known Limits

- the historical bundle still contains older flat-workspace and machine-absolute
  path strings
- some historical labels overstate M1 and Appendix-E closure
- the preserved bundle is evidence lineage, not self-updating runtime truth

Use this file with:

- `README.md`
- `AUDITOR_PLAYBOOK.md`
- `docs/LEGAL_BOUNDARIES.md`
- `proofs/FINAL_STATUS.md`
