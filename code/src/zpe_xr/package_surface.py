"""Phase 3 package-surface and wedge-boundary helpers."""

from __future__ import annotations

from pathlib import Path
import tomllib
from typing import Any, Mapping

from . import __version__
from .io_utils import read_json


PHASE1_RUN_ID = "2026-03-20_zpe_xr_wave1_live"
PHASE2_RUN_ID = "2026-03-20_zpe_xr_phase2_pre_runpod"


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
    phase1_dir = artifact_base / PHASE1_RUN_ID
    phase2_dir = artifact_base / PHASE2_RUN_ID
    return {
        "compression": _load_json(phase1_dir / "xr_compression_benchmark.json"),
        "fidelity": _load_json(phase1_dir / "xr_fidelity_eval.json"),
        "latency": _load_json(phase1_dir / "xr_latency_benchmark.json"),
        "packet_loss": _load_json(phase1_dir / "xr_packet_loss_resilience.json"),
        "gesture": _load_json(phase1_dir / "xr_gesture_eval.json"),
        "bandwidth": _load_json(phase1_dir / "xr_bandwidth_eval.json"),
        "phase1_summary": _load_json(phase1_dir / "phase1_execution_summary.json"),
        "phase2_comparator": _load_json(phase2_dir / "phase2_comparator_matrix.json"),
        "phase2_runtime": _load_json(phase2_dir / "phase2_runtime_probe_matrix.json"),
        "phase2_corpus": _load_json(phase2_dir / "phase2_outward_corpus_probe.json"),
        "phase2_summary": _load_json(phase2_dir / "phase2_execution_summary.json"),
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
    claims = {
        "generated_from": {
            "phase1_run_id": PHASE1_RUN_ID,
            "phase2_run_id": PHASE2_RUN_ID,
        },
        "allowed_claims": [
            {
                "id": "codec_frozen_lane",
                "title": "Fresh frozen-lane codec performance",
                "summary": (
                    f"Fresh root rerun preserves {_fmt_ratio(evidence['compression']['compression_ratio_vs_raw'])} "
                    f"compression vs raw, { _fmt_float(evidence['fidelity']['mpjpe_mm']) } mm MPJPE, "
                    f"{ _fmt_float(evidence['latency']['combined_avg_ms']) } ms average encode+decode latency, "
                    f"and { _fmt_float(evidence['packet_loss']['target_case']['pose_error_percent']) }% pose error at 10% loss."
                ),
                "evidence": [
                    _artifact_locator(artifact_prefix, PHASE1_RUN_ID, "xr_compression_benchmark.json"),
                    _artifact_locator(artifact_prefix, PHASE1_RUN_ID, "xr_fidelity_eval.json"),
                    _artifact_locator(artifact_prefix, PHASE1_RUN_ID, "xr_latency_benchmark.json"),
                    _artifact_locator(artifact_prefix, PHASE1_RUN_ID, "xr_packet_loss_resilience.json"),
                ],
                "guardrail": "Synthetic frozen v1 lane only; does not imply runtime closure.",
            },
            {
                "id": "synthetic_gesture_sidecar",
                "title": "Synthetic compressed-space gesture sidecar",
                "summary": (
                    f"Fresh synthetic gesture evaluation remains at { _fmt_float(evidence['gesture']['accuracy']) } accuracy "
                    "with the claim kept inside the synthetic corpus boundary."
                ),
                "evidence": [
                    _artifact_locator(artifact_prefix, PHASE1_RUN_ID, "xr_gesture_eval.json"),
                ],
                "guardrail": "Synthetic only; not a broader external-vocabulary claim.",
            },
            {
                "id": "ultraleap_bounded_row",
                "title": "Bounded Ultraleap transport comparison",
                "summary": "ZPE remains smaller than the open-source Ultraleap VectorHand row under the documented close transport semantics.",
                "evidence": [
                    _artifact_locator(artifact_prefix, PHASE2_RUN_ID, "phase2_comparator_matrix.json"),
                ],
                "guardrail": "This is a bounded comparator row, not a universal incumbent-displacement claim.",
            },
            {
                "id": "contactpose_local_lane",
                "title": "ContactPose readiness as the first outward-safe local corpus lane",
                "summary": "ContactPose is ready for local intake with an explicit 21-to-26 topology adapter and the exact PRD corpus gap preserved.",
                "evidence": [
                    _artifact_locator(artifact_prefix, PHASE2_RUN_ID, "phase2_outward_corpus_probe.json"),
                ],
                "guardrail": "ContactPose readiness does not close the exact PRD egocentric corpus requirement.",
            },
        ],
        "open_claims": [
            {
                "id": "photon_displacement",
                "title": "Photon displacement",
                "status": "OPEN",
                "reason": "Photon's documented compressed hand path is smaller but narrower in semantics, so the row stays open.",
                "evidence": [
                    _artifact_locator(artifact_prefix, PHASE2_RUN_ID, "phase2_comparator_matrix.json"),
                ],
            },
            {
                "id": "runtime_closure",
                "title": "Unity/Meta runtime closure",
                "status": "PAUSED_EXTERNAL",
                "reason": "Editor, disk, device-trace, and MANO-license blockers remain active.",
                "evidence": [
                    _artifact_locator(artifact_prefix, PHASE2_RUN_ID, "phase2_runtime_probe_matrix.json"),
                ],
            },
            {
                "id": "exact_prd_corpus",
                "title": "Exact PRD egocentric corpus closure",
                "status": "UNRESOLVED",
                "reason": "ContactPose is the best outward-safe lane available now, but it is not the exact PRD surface.",
                "evidence": [
                    _artifact_locator(artifact_prefix, PHASE2_RUN_ID, "phase2_outward_corpus_probe.json"),
                ],
            },
            {
                "id": "public_release_readiness",
                "title": "Public release readiness",
                "status": "NOT_READY",
                "reason": "Blind-clone and release-channel decision phases are still outstanding.",
                "evidence": [
                    _artifact_locator(artifact_prefix, PHASE1_RUN_ID, "phase1_execution_summary.json"),
                    _artifact_locator(artifact_prefix, PHASE2_RUN_ID, "phase2_execution_summary.json"),
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
                "reason": "Photon remains an open semantics-mismatched row.",
            },
            {
                "id": "exact_corpus_closed",
                "claim": "Exact PRD corpus is closed",
                "reason": "ContactPose is a substitute lane, not the exact named corpus.",
            },
            {
                "id": "public_release_ready",
                "claim": "Ready for public release",
                "reason": "Package candidate formation does not replace blind-clone or release-channel closure.",
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
    comparator = evidence["phase2_comparator"]
    runtime = evidence["phase2_runtime"]
    corpus = evidence["phase2_corpus"]
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
            "compression_vs_raw": evidence["compression"]["compression_ratio_vs_raw"],
            "mpjpe_mm": evidence["fidelity"]["mpjpe_mm"],
            "combined_avg_ms": evidence["latency"]["combined_avg_ms"],
            "pose_error_percent_10_loss": evidence["packet_loss"]["target_case"]["pose_error_percent"],
            "gesture_accuracy": evidence["gesture"]["accuracy"],
            "bandwidth_kb_per_s_4_player": evidence["bandwidth"]["kbps_for_4_player_session"],
            "ultraleap_status": next(verdict["status"] for verdict in comparator["verdicts"] if "Ultraleap" in verdict["claim"]),
            "photon_status": next(verdict["status"] for verdict in comparator["verdicts"] if "Photon" in verdict["claim"]),
            "runtime_status": runtime["xr_c007_status_candidate"],
            "contactpose_status": corpus["contactpose"]["status"],
            "exact_prd_corpus_status": corpus["exact_prd_gap"]["status"],
        },
        "anchors": {
            "phase1_summary": _artifact_locator(artifact_prefix, PHASE1_RUN_ID, "phase1_execution_summary.json"),
            "phase2_summary": _artifact_locator(artifact_prefix, PHASE2_RUN_ID, "phase2_execution_summary.json"),
            "compression": _artifact_locator(artifact_prefix, PHASE1_RUN_ID, "xr_compression_benchmark.json"),
            "gesture": _artifact_locator(artifact_prefix, PHASE1_RUN_ID, "xr_gesture_eval.json"),
            "comparator": _artifact_locator(artifact_prefix, PHASE2_RUN_ID, "phase2_comparator_matrix.json"),
            "runtime": _artifact_locator(artifact_prefix, PHASE2_RUN_ID, "phase2_runtime_probe_matrix.json"),
            "corpus": _artifact_locator(artifact_prefix, PHASE2_RUN_ID, "phase2_outward_corpus_probe.json"),
        },
        "release_readiness": "NOT_READY_FOR_PUBLIC_RELEASE",
        "release_blockers": [
            "BLIND_CLONE_NOT_EXECUTED",
            "PHOTON_ROW_OPEN",
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
- gesture accuracy: `{_fmt_float(snapshot['gesture_accuracy'])}`
- 4-player modeled bandwidth: `{_fmt_float(snapshot['bandwidth_kb_per_s_4_player'])} KB/s`
- Ultraleap row: `{snapshot['ultraleap_status']}`
- Photon row: `{snapshot['photon_status']}`
- runtime: `{snapshot['runtime_status']}`
- ContactPose: `{snapshot['contactpose_status']}`
- exact PRD corpus: `{snapshot['exact_prd_corpus_status']}`

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

ZPE-XR is a private-stage package candidate for a deterministic XR hand-stream codec and evaluation harness.

This repo is buildable and inspectable, but it is not yet public-release proof and it is not a runtime-closure claim surface.

## Current Authority

- Fresh frozen-lane evidence is anchored to `{anchors['phase1_summary']}`.
- Direct-comparator and runtime boundary evidence is anchored to `{anchors['phase2_summary']}`.
- The current outward wedge is narrow:
  - fresh codec transport/fidelity/latency/loss results
  - bounded synthetic gesture sidecar
  - bounded Ultraleap row
  - ContactPose readiness as an outward-safe local corpus lane

## Current Metrics

- compression vs raw: `{_fmt_ratio(snapshot['compression_vs_raw'])}`
- MPJPE: `{_fmt_float(snapshot['mpjpe_mm'])} mm`
- combined latency: `{_fmt_float(snapshot['combined_avg_ms'])} ms`
- pose error at 10% loss: `{_fmt_float(snapshot['pose_error_percent_10_loss'])}%`
- gesture accuracy: `{_fmt_float(snapshot['gesture_accuracy'])}`

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
- fresh frozen-lane evidence from the March 20 root rerun
- bounded direct-comparator, runtime, and outward-safe corpus status from Phase 2
- the current allowed/open/forbidden wedge boundary documented in `proofs/FINAL_STATUS.md`

## What This Staged Repo Does Not Establish

- Photon displacement
- production Unity/Meta runtime readiness
- exact PRD corpus closure
- blind-clone closure for this exact staged snapshot
- public-release readiness

## Known Limits

- ContactPose is the first outward-safe local corpus lane, not the exact PRD corpus
- the package candidate is truthful but still below release approval
- the historical 2026-02-20 bundle remains evidence lineage, not the current repo's sovereign truth
"""

    auditor = f"""# Auditor Playbook

This is the shortest honest audit path for the current private-stage package candidate.

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
- `{anchors['phase1_summary']}`
- `{anchors['phase2_summary']}`
- `PUBLIC_AUDIT_LIMITS.md`

## Expected Current Reading

- package imports cleanly from `code/src`
- the fresh March 20 evidence chain is present
- Photon remains open
- `XR-C007` remains `PAUSED_EXTERNAL`
- public release readiness is still not established
"""

    changelog = """# Changelog

## 2026-03-20

- upgraded the staged repo from a historical staging shell to a truthful package candidate surface
- refreshed staged README, proof status, and audit notes from the fresh March 20 evidence chain
- carried forward the bounded Ultraleap win, Photon open row, runtime `PAUSED_EXTERNAL` status, and ContactPose readiness
- added build/install-smoke evidence to the staged package story without promoting public release

## 2026-03-09

- formed the first clean inner-repo boundary under `ZPE-XR/`
- split repo material into `code/`, `docs/`, `proofs/`, and `executable/`
- staged the historical Wave-1 artifact bundle under `proofs/artifacts/`
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

Private-stage Python package candidate for the ZPE-XR codec and evaluation harness.

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
- fresh frozen-lane codec evidence: yes
- public release readiness: no
- runtime closure: `PAUSED_EXTERNAL`

This package README does not claim Photon displacement, runtime closure, exact-corpus closure, or public-release readiness.
"""

    proofs_readme = f"""# Proofs

This directory contains the current staged reading of the repo plus the preserved historical Wave-1 artifact bundle.

## Current Staged Reading

- `proofs/FINAL_STATUS.md`
- `proofs/RELEASE_READINESS_REPORT.md`
- `{anchors['phase1_summary']}`
- `{anchors['phase2_summary']}`

## Preserved Historical Evidence

- `proofs/artifacts/2026-02-20_zpe_xr_wave1/`
- `proofs/runbooks/`

The copied historical bundle remains evidence lineage. It does not outrank the fresh March 20 evidence chain used by the current staged proof boundary.
"""

    final_status = f"""# Final Status

This document is the current staged reading of the XR evidence boundary.

## Claim Status

| Claim | Current staged reading | Anchor | Notes |
|---|---|---|---|
| `XR-C001` | PASS | `{_artifact_locator('proofs/artifacts', PHASE1_RUN_ID, 'xr_compression_benchmark.json')}` | `{_fmt_ratio(snapshot['compression_vs_raw'])}` compression vs raw on fresh root rerun |
| `XR-C002` | PASS | `{_artifact_locator('proofs/artifacts', PHASE1_RUN_ID, 'xr_fidelity_eval.json')}` | `{_fmt_float(snapshot['mpjpe_mm'])} mm` MPJPE on the frozen synthetic lane |
| `XR-C003` | PASS | `{_artifact_locator('proofs/artifacts', PHASE1_RUN_ID, 'xr_latency_benchmark.json')}` | `{_fmt_float(snapshot['combined_avg_ms'])} ms` average encode+decode latency |
| `XR-C004` | PASS | `{_artifact_locator('proofs/artifacts', PHASE1_RUN_ID, 'xr_packet_loss_resilience.json')}` | `{_fmt_float(snapshot['pose_error_percent_10_loss'])}%` pose error at `10%` packet loss |
| `XR-C005` | PASS | `{_artifact_locator('proofs/artifacts', PHASE1_RUN_ID, 'xr_gesture_eval.json')}` | synthetic gesture corpus only |
| `XR-C006` | PASS | `{_artifact_locator('proofs/artifacts', PHASE1_RUN_ID, 'xr_bandwidth_eval.json')}` | modeled multi-player bandwidth only |
| `XR-C007` | `PAUSED_EXTERNAL` | `{_artifact_locator('proofs/artifacts', PHASE2_RUN_ID, 'phase2_runtime_probe_matrix.json')}` | runtime closure is still blocked by editor/device/license constraints |

## Comparator Boundary

- Ultraleap row: bounded PASS under close transport semantics.
- Photon row: OPEN because the documented compressed path is narrower in semantics and smaller in bytes/frame.

## Corpus Boundary

- ContactPose: `READY_FOR_LOCAL_INTAKE` with the explicit `21-to-26` adapter path.
- Exact PRD corpus: `UNRESOLVED`.

## Current Verdict

- package candidate: formed
- proof honesty: improved and refreshed from fresh evidence
- public release readiness: not established
"""

    release_readiness = """# Release Readiness Report

Date: 2026-03-20
Verdict: `NOT_READY_FOR_PUBLIC_RELEASE`

## What Was Completed In This Phase

- upgraded package metadata from placeholder status to a real package candidate
- built fresh distribution artifacts and completed clean install/import smoke
- refreshed staged README/proofs/audit surfaces from the fresh March 20 evidence chain
- preserved the narrow wedge while keeping Photon, runtime, and exact-corpus blockers explicit

## Blocking Gaps

- no blind-clone verification for the exact staged snapshot yet
- Photon row remains open
- `XR-C007` remains `PAUSED_EXTERNAL`
- exact PRD corpus remains unresolved

## Non-Blocking But Important

- package builds and imports with a non-placeholder version
- fresh Phase 1 and Phase 2 evidence is now the staged source of truth
- the staged repo is a truthful package candidate, not yet a public-release surface
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
