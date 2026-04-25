"""Phase 3 package-surface and wedge-boundary helpers."""

from __future__ import annotations

from pathlib import Path
import tomllib
from typing import Any, Mapping

from . import __version__
from .io_utils import read_json


PHASE4_CONTACTPOSE_RUN_ID = "2026-03-21_zpe_xr_phase4_runpod_contactpose_124835Z"
PHASE5_MULTI_SEQUENCE_RUN_ID = "2026-03-21_zpe_xr_phase5_multi_sequence_161900Z"


def _artifact_locator(prefix: str, run_id: str, filename: str) -> str:
    clean_prefix = prefix.strip("/")
    return f"{clean_prefix}/{run_id}/{filename}"


def _fmt_float(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def _fmt_ratio(value: float) -> str:
    return f"{value:.3f}x"


def _load_json(path: Path) -> dict[str, Any]:
    return dict(read_json(path))


def _artifact_base_dir(root: Path) -> Path:
    candidates = [
        root / "proofs" / "artifacts",
        root / "artifacts",
        root.parent / "proofs" / "artifacts",
        root.parent / "artifacts",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def _pyproject_path(root: Path) -> Path:
    candidates = [
        root / "pyproject.toml",
        root / "code" / "pyproject.toml",
        root.parent / "pyproject.toml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def load_phase_evidence(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    artifact_base = _artifact_base_dir(root)
    phase4_dir = artifact_base / PHASE4_CONTACTPOSE_RUN_ID
    phase5_dir = artifact_base / PHASE5_MULTI_SEQUENCE_RUN_ID
    return {
        "phase4_contactpose": _load_json(phase4_dir / "phase4_contactpose_benchmark.json"),
        "phase5_multi_sequence": _load_json(phase5_dir / "phase5_multi_sequence_benchmark.json"),
    }


def load_project_metadata(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    pyproject = tomllib.loads(_pyproject_path(root).read_text(encoding="utf-8"))
    project = pyproject["project"]
    return {
        "name": project["name"],
        "version": __version__,
        "requires_python": project["requires-python"],
        "description": project["description"],
        "homepage": project["urls"]["Homepage"],
        "repository": project["urls"]["Repository"],
    }


def build_wedge_claims(root: Path, *, artifact_prefix: str = "artifacts") -> dict[str, Any]:
    evidence = load_phase_evidence(root)
    phase4 = evidence["phase4_contactpose"]["benchmark"]
    phase5 = evidence["phase5_multi_sequence"]["benchmark"]
    aggregate = phase5["aggregate"]
    claims = {
        "generated_from": {
            "phase4_contactpose_run_id": PHASE4_CONTACTPOSE_RUN_ID,
            "phase5_multi_sequence_run_id": PHASE5_MULTI_SEQUENCE_RUN_ID,
        },
        "allowed_claims": [
            {
                "id": "contactpose_multi_sequence",
                "title": "ContactPose multi-sequence codec performance",
                "summary": (
                    f"Phase 5 ContactPose multi-sequence mean compression is {_fmt_ratio(aggregate['compression_ratio_vs_raw_mean'])}, "
                    f"mean MPJPE { _fmt_float(aggregate['mpjpe_mm_mean']) } mm, "
                    f"mean encode+decode latency { _fmt_float(aggregate['latency_ms_mean']) } ms, "
                    f"and mean 10% loss error { _fmt_float(aggregate['packet_loss_error_pct_mean']) }%."
                ),
                "evidence": [
                    _artifact_locator(artifact_prefix, PHASE5_MULTI_SEQUENCE_RUN_ID, "phase5_multi_sequence_benchmark.json"),
                ],
                "guardrail": "ContactPose corpus only; does not imply runtime closure.",
            },
            {
                "id": "contactpose_single_sequence",
                "title": "ContactPose single-sequence benchmark anchor",
                "summary": (
                    f"Phase 4 ContactPose single-sequence benchmark preserves "
                    f"{ _fmt_ratio(phase4['compression_metrics']['compression_ratio_vs_raw']) } compression vs raw, "
                    f"{ _fmt_float(phase4['fidelity_metrics']['mpjpe_mm']) } mm MPJPE, "
                    f"{ _fmt_float(phase4['latency_metrics']['combined_avg_ms']) } ms latency, "
                    f"and { _fmt_float(phase4['packet_loss_metrics']['pose_error_percent']) }% pose error at 10% loss."
                ),
                "evidence": [
                    _artifact_locator(artifact_prefix, PHASE4_CONTACTPOSE_RUN_ID, "phase4_contactpose_benchmark.json"),
                ],
                "guardrail": "Single-sequence anchor; modern comparator gate failed in Phase 5 multi-sequence run.",
            },
        ],
        "open_claims": [
            {
                "id": "modern_comparator_gate",
                "title": "Modern comparator multi-sequence gate",
                "status": "FAILED",
                "reason": f"Modern comparator passes {aggregate['modern_comparator_pass_count']}/{aggregate['sequence_count']} in Phase 5.",
                "evidence": [
                    _artifact_locator(artifact_prefix, PHASE5_MULTI_SEQUENCE_RUN_ID, "phase5_multi_sequence_benchmark.json"),
                ],
            },
            {
                "id": "runtime_closure",
                "title": "Unity/Meta runtime closure",
                "status": "PAUSED_EXTERNAL",
                "reason": "XR-C007 remains paused due to device/editor/license constraints.",
                "evidence": [
                    "proofs/FINAL_STATUS.md",
                ],
            },
            {
                "id": "photon_displacement",
                "title": "Photon displacement",
                "status": "OPEN",
                "reason": "Photon semantics-equivalent comparison remains secondary and open.",
                "evidence": [
                    "proofs/FINAL_STATUS.md",
                ],
            },
            {
                "id": "exact_prd_corpus",
                "title": "Exact PRD egocentric corpus closure",
                "status": "UNRESOLVED",
                "reason": "ContactPose is outward-safe but not the exact PRD corpus.",
                "evidence": [
                    "proofs/FINAL_STATUS.md",
                ],
            },
        ],
        "forbidden_claims": [
            {
                "id": "market_leading_runtime",
                "claim": "Market-leading XR runtime",
                "reason": "Runtime closure is still explicitly paused.",
            },
            {
                "id": "photon_closed",
                "claim": "Photon is displaced",
                "reason": "Photon remains a secondary, open comparator row.",
            },
            {
                "id": "exact_corpus_closed",
                "claim": "Exact PRD corpus is closed",
                "reason": "ContactPose is a substitute lane, not the exact named corpus.",
            },
            {
                "id": "public_release_ready",
                "claim": "Ready for public release",
                "reason": "Modern comparator gate failed in Phase 5.",
            },
        ],
    }
    return claims


def build_package_surface(
    root: Path,
    *,
    artifact_prefix: str = "artifacts",
    build_summary: Mapping[str, Any],
    install_smoke: Mapping[str, Any],
    test_summary: Mapping[str, Any],
    stage_verify: Mapping[str, Any],
) -> dict[str, Any]:
    evidence = load_phase_evidence(root)
    project = load_project_metadata(root)
    phase4 = evidence["phase4_contactpose"]["benchmark"]
    phase5 = evidence["phase5_multi_sequence"]["benchmark"]
    aggregate = phase5["aggregate"]
    return {
        "package": project,
        "verification": {
            "pytest_passed": bool(test_summary.get("passed")),
            "pytest_summary": test_summary.get("summary"),
            "build_passed": bool(build_summary.get("passed")),
            "built_artifacts": list(build_summary.get("artifacts", [])),
            "install_smoke_passed": bool(install_smoke.get("passed")),
            "install_smoke_version": install_smoke.get("version"),
            "stage_verify_passed": bool(stage_verify.get("passed")),
        },
        "evidence_snapshot": {
            "compression_vs_raw": aggregate["compression_ratio_vs_raw_mean"],
            "mpjpe_mm": aggregate["mpjpe_mm_mean"],
            "combined_avg_ms": aggregate["latency_ms_mean"],
            "pose_error_percent_10_loss": aggregate["packet_loss_error_pct_mean"],
            "modern_comparator_passes": aggregate["modern_comparator_pass_count"],
            "sequence_count": aggregate["sequence_count"],
            "phase4_single_sequence_compression": phase4["compression_metrics"]["compression_ratio_vs_raw"],
        },
        "anchors": {
            "phase4_contactpose": _artifact_locator(
                artifact_prefix, PHASE4_CONTACTPOSE_RUN_ID, "phase4_contactpose_benchmark.json"
            ),
            "phase5_multi_sequence": _artifact_locator(
                artifact_prefix, PHASE5_MULTI_SEQUENCE_RUN_ID, "phase5_multi_sequence_benchmark.json"
            ),
            "final_status": "proofs/FINAL_STATUS.md",
        },
        "release_readiness": "PUBLISHED_PYPI",
        "release_blockers": [
            "MODERN_COMPARATOR_GATE_FAILED",
            "XR_C007_PAUSED_EXTERNAL",
            "EXACT_PRD_CORPUS_UNRESOLVED",
        ],
    }


def render_package_surface_markdown(surface: Mapping[str, Any]) -> str:
    snapshot = surface["evidence_snapshot"]
    verification = surface["verification"]
    artifacts = surface["verification"]["built_artifacts"]
    artifact_lines = "\n".join(f"- `{artifact['name']}` ({artifact['bytes']} bytes)" for artifact in artifacts) or "- none"
    return f"""# Phase 3 Package Surface

## Package Candidate

- package: `{surface['package']['name']}`
- version: `{surface['package']['version']}`
- requires-python: `{surface['package']['requires_python']}`
- pytest: `{verification['pytest_summary']}`
- build passed: `{verification['build_passed']}`
- clean install smoke: `{verification['install_smoke_passed']}`
- staged verify: `{verification['stage_verify_passed']}`

## Fresh Evidence Snapshot

- compression vs raw: `{_fmt_ratio(snapshot['compression_vs_raw'])}`
- MPJPE: `{_fmt_float(snapshot['mpjpe_mm'])} mm`
- combined latency: `{_fmt_float(snapshot['combined_avg_ms'])} ms`
- pose error at 10% loss: `{_fmt_float(snapshot['pose_error_percent_10_loss'])}%`
- modern comparator passes: `{snapshot['modern_comparator_passes']}/{snapshot['sequence_count']}`
- Phase 4 single-sequence compression: `{_fmt_ratio(snapshot['phase4_single_sequence_compression'])}`

## Build Artifacts

{artifact_lines}

## Release Read

Verdict: `{surface['release_readiness']}`
"""


def render_wedge_claims_markdown(claims: Mapping[str, Any]) -> str:
    allowed = "\n".join(
        f"- `{item['id']}`: {item['summary']}"
        for item in claims["allowed_claims"]
    )
    open_claims = "\n".join(
        f"- `{item['id']}`: {item['status']} — {item['reason']}"
        for item in claims["open_claims"]
    )
    forbidden = "\n".join(
        f"- `{item['id']}`: {item['claim']} — {item['reason']}"
        for item in claims["forbidden_claims"]
    )
    return f"""# Phase 3 Wedge Claims

## Allowed

{allowed}

## Open

{open_claims}

## Forbidden

{forbidden}
"""


def render_staged_files(surface: Mapping[str, Any], claims: Mapping[str, Any]) -> dict[str, str]:
    anchors = surface["anchors"]
    snapshot = surface["evidence_snapshot"]
    readme = f"""# ZPE-XR

ZPE-XR is a deterministic XR hand-stream codec and evaluation harness, published on PyPI as `zpe-xr` v0.3.1.

The modern comparator gate remains 0/5 FAIL and runtime closure remains PAUSED_EXTERNAL.

## Current Authority

- Phase 5 ContactPose multi-sequence evidence is anchored to `{anchors['phase5_multi_sequence']}`.
- Phase 4 ContactPose single-sequence anchor is `{anchors['phase4_contactpose']}`.
- Boundary and release-status truth is consolidated in `{anchors['final_status']}`.

## Current Metrics

- compression vs raw: `{_fmt_ratio(snapshot['compression_vs_raw'])}`
- MPJPE: `{_fmt_float(snapshot['mpjpe_mm'])} mm`
- combined latency: `{_fmt_float(snapshot['combined_avg_ms'])} ms`
- pose error at 10% loss: `{_fmt_float(snapshot['pose_error_percent_10_loss'])}%`
- modern comparator passes: `{snapshot['modern_comparator_passes']}/{snapshot['sequence_count']}`

## What This Repo Does Not Prove

- Photon displacement is still open.
- `XR-C007` remains `PAUSED_EXTERNAL`.
- ContactPose does not close the exact PRD corpus gap.
- Public release readiness is not established.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e "./code[dev]"
python ./executable/verify.py
```

Optional test replay:

```bash
python -m pytest ./code/tests -q
```

## Go Next

- Read [proofs/FINAL_STATUS.md](proofs/FINAL_STATUS.md)
- Read [proofs/RELEASE_READINESS_REPORT.md](proofs/RELEASE_READINESS_REPORT.md)
- Read [PUBLIC_AUDIT_LIMITS.md](PUBLIC_AUDIT_LIMITS.md)
- Read [AUDITOR_PLAYBOOK.md](AUDITOR_PLAYBOOK.md)
"""

    audit_limits = """# Public Audit Limits

This file defines what the staged ZPE-XR repo can and cannot establish right now.

## What This Staged Repo Can Establish

- a buildable package candidate with a non-placeholder package version
- Phase 5 ContactPose multi-sequence metrics and Phase 4 single-sequence anchor
- the current allowed/open/forbidden wedge boundary documented in `proofs/FINAL_STATUS.md`

## What This Staged Repo Does Not Establish

- Photon displacement
- production Unity/Meta runtime readiness
- exact PRD corpus closure
- public-release readiness

## Known Limits

- ContactPose is the outward-safe corpus boundary, not the exact PRD corpus
- the package is published on PyPI; the modern comparator gate (0/5) remains the primary open quality gate
"""

    auditor = f"""# Auditor Playbook

This is the shortest honest audit path for the current ZPE-XR package (v0.3.1, published on PyPI).

## Shortest Staged Audit Path

1. Clone or use the staged repo.
2. Create an environment and install the package:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e "./code[dev]"
```

3. Run the staged verification entrypoint:

```bash
python ./executable/verify.py
```

4. Optional test replay:

```bash
python -m pytest ./code/tests -q
```

## What To Inspect

- `proofs/FINAL_STATUS.md`
- `proofs/RELEASE_READINESS_REPORT.md`
- `{anchors['phase5_multi_sequence']}`
- `{anchors['phase4_contactpose']}`
- `PUBLIC_AUDIT_LIMITS.md`

## Expected Current Reading

- package imports cleanly from `code/source`
- Phase 5 ContactPose metrics present
- Photon remains open
- `XR-C007` remains `PAUSED_EXTERNAL`
- public release readiness is still not established
"""

    changelog = """# Changelog

## 2026-03-21

- aligned documentation to the ZPE-IMC layout standard without importing IMC-specific claims
- refreshed the front door to the Phase 5 authority chain and private-only release posture
- added the shared IMC visual assets to `.github/assets/readme/`
- created a canonical documentation registry and falsification report

## 2026-03-20

- upgraded the staged repo from a historical staging shell to a truthful package candidate surface
- refreshed staged README, proof status, and audit notes from the fresh March 20 evidence chain
- carried forward runtime `PAUSED_EXTERNAL` status, ContactPose readiness, and explicit public-release blockers
- added build/install-smoke evidence to the staged package story without promoting public release

## 2026-03-09

- formed the first clean inner-repo boundary under `ZPE-XR/`
- split repo material into `code/`, `docs/`, `proofs/`, and `executable/`
- added private-staging front-door, legal, audit, and support surfaces
"""

    docs_index = """# Docs Index

- `docs/ARCHITECTURE.md`: repo map, runtime map, and authority classes
- `docs/LEGAL_BOUNDARIES.md`: license and dataset/runtime caveats
- `docs/FAQ.md`: quick answers for operators and reviewers
- `docs/SUPPORT.md`: contact and support routing
- `AUDITOR_PLAYBOOK.md`: shortest honest staged audit path
- `PUBLIC_AUDIT_LIMITS.md`: explicit proof and publication limits
- `proofs/FINAL_STATUS.md`: current staged claim boundary
- `proofs/RELEASE_READINESS_REPORT.md`: release-readiness blocker read
"""

    code_readme = f"""# zpe-xr

Python package for the ZPE-XR codec and evaluation harness. Published on PyPI as `zpe-xr`.

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

## Current Bounded Read

- version: `{surface['package']['version']}`
- ContactPose codec evidence: yes
- public release readiness: no
- runtime closure: `PAUSED_EXTERNAL`

This package README does not claim Photon displacement, runtime closure, exact-corpus closure, or public-release readiness.
"""

    proofs_readme = f"""# Proofs

This directory contains the current staged reading of the repo and the compact Phase 4/Phase 5 evidence bundles.

## Current Staged Reading

- `proofs/FINAL_STATUS.md`
- `proofs/RELEASE_READINESS_REPORT.md`
- `{anchors['phase5_multi_sequence']}`
- `{anchors['phase4_contactpose']}`

## Notes

- legacy pre-Phase 4 bundles were removed to keep the authority surface lean
"""

    final_status = f"""# Final Status

This document is the current staged reading of the XR evidence boundary.

## Current Authority

- Phase 5 ContactPose multi-sequence: mean compression `{_fmt_ratio(snapshot['compression_vs_raw'])}`, mean MPJPE `{_fmt_float(snapshot['mpjpe_mm'])} mm`, mean latency `{_fmt_float(snapshot['combined_avg_ms'])} ms`, mean loss error `{_fmt_float(snapshot['pose_error_percent_10_loss'])}%`, modern comparator passes `{snapshot['modern_comparator_passes']}/{snapshot['sequence_count']}`. Anchor: `{anchors['phase5_multi_sequence']}`.
- Phase 4 ContactPose single-sequence: compression `{_fmt_ratio(snapshot['phase4_single_sequence_compression'])}`. Anchor: `{anchors['phase4_contactpose']}`.
- Phase 4 cold-start audit: `PASS`, Comet logging disabled (key null). Anchor: `proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json`.
- Package mechanics: Rust backend, `twine check` PASS, version `{surface['package']['version']}`. Anchor: `release_readiness.json`.

## Comparator Boundary

- Modern comparator gate failed `{snapshot['modern_comparator_passes']}/{snapshot['sequence_count']}`; blocks public release.
- Photon displacement remains open and secondary.

## Corpus Boundary

- ContactPose lanes are the outward-safe corpus boundary.
- Exact PRD corpus remains unresolved.

## Runtime Boundary

- `XR-C007` remains `PAUSED_EXTERNAL` due to device/editor/license constraints.

## Current Verdict

- outward-safe workload: ContactPose `PASS`
- package candidate: `PASS`
- cold-start trust: `PASS`
- PyPI publication: `PUBLISHED` (v0.3.1 on PyPI)
- modern comparator gate: `FAIL` (0/5)
- Unity/Meta runtime closure: `PAUSED_EXTERNAL`
"""

    release_readiness = """# Release Readiness Report

Date: 2026-03-21 (original); updated 2026-04-14
Verdict: `PUBLISHED_PYPI` (v0.3.1 on PyPI)
Modern Comparator Gate: `0/5 FAIL`
Runtime Closure: `PAUSED_EXTERNAL`

## What Was Completed In Phase 5

- repaired the package surface to build through `maturin` with a real Rust backend
- passed `maturin develop --release`, staged tests, `maturin build --release`, `twine check`, and fresh-venv wheel install/import smoke
- executed the decisive Phase 5 ContactPose multi-sequence benchmark on RunPod with live Comet logging
- produced a non-null Phase 5 Comet experiment key: `0e957cb027364d36880f6962fd70b78f`
- reused and then removed the remote `contactpose_sample.zip`, leaving the verified workspace compact
- completed surface adjudication and release-channel classification from the closed evidence chain

## Blocking Gaps

- the governing public-release comparator gate failed: the modern comparator row passed `0/5` sequences on the Phase 5 multi-sequence ContactPose run
- public comparator-displacement language is therefore unsupported
- `XR-C007` remains `PAUSED_EXTERNAL` for any future runtime-facing channel

## Non-Blocking But Important

- the package is mechanically valid: Rust backend, x86_64 wheel, `twine check` PASS, and fresh install/import smoke PASS
- the outward-safe ContactPose lane is stronger than before: mean `23.90x` compression vs raw, mean `0.479 mm` MPJPE, mean `0.057 ms` encode+decode latency, mean `0.399%` pose error at `10%` loss across five sequences
- Phase 4 cold-start Comet logging was disabled (key null)
- the strongest honest channel is now a private/internal package surface, not a public release
"""

    return {
        "README.md": readme,
        "PUBLIC_AUDIT_LIMITS.md": audit_limits,
        "AUDITOR_PLAYBOOK.md": auditor,
        "CHANGELOG.md": changelog,
        "docs/README.md": docs_index,
        "code/README.md": code_readme,
        "proofs/README.md": proofs_readme,
        "proofs/FINAL_STATUS.md": final_status,
        "proofs/RELEASE_READINESS_REPORT.md": release_readiness,
    }
