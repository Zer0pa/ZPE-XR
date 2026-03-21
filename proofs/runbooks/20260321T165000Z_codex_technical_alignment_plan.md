# Repo Technical Alignment Plan

Date: 2026-03-21
Repo: /Users/Zer0pa/ZPE/ZPE XR/ZPE-XR
Working Prompt: /Users/Zer0pa/ZPE/ZPE XR/ZPE-XR/proofs/runbooks/REPO_TECHNICAL_ALIGNMENT_EXECUTION_PROMPT.md
Working Supplement: /Users/Zer0pa/ZPE/ZPE XR/ZPE-XR/proofs/runbooks/REPO_TECHNICAL_EXECUTION_SUPPLEMENT.md

## Target Architecture

- Treat ZPE-XR as a private-stage Python package candidate with a repo-local Rust extension and staged verification harness.
- Make `code/source/zpe_xr` the single canonical Python source root for packaging, scripts, tests, and CI.
- Keep `executable/verify.py` as a repo-local verification harness, not an installed-runtime contract.

## Execution Steps

1. Remove `code/src` path assumptions from package metadata, scripts, tests, and verification surfaces.
2. Replace duplicated or drifting `code/src/zpe_xr` runtime code with a single canonical `code/source/zpe_xr` path and keep only the minimum compatibility surface needed for repo-local tooling.
3. Fix CI/install workflow truth so the declared package path, Rust dependency, and verification steps match the actual build architecture.
4. Falsify the aligned surface with editable install, wheel build, fresh install/import smoke, repo-local verify, test suite, and static workflow review.
5. Write a repo-local receipt with the final verdict and remaining real blockers only.
