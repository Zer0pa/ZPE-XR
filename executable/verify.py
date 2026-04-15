#!/usr/bin/env python3
"""Root-owned staged-repo verification entrypoint."""

from __future__ import annotations

import json
from pathlib import Path
import sys


PHASE5_BENCHMARK = (
    "proofs/artifacts/2026-04-14_zpe_xr_live_014204/phase5_multi_sequence_benchmark.json"
)
PHASE6_COMPARATOR = (
    "proofs/artifacts/2026-03-29_zpe_xr_phase6_mac_comparator_arm64/"
    "phase6_mac_comparator_benchmark.json"
)
PHASE4_COLD_START = (
    "proofs/artifacts/2026-03-21_zpe_xr_phase4_cold_start/phase4_cold_start_audit.json"
)
PHASE5_RELEASE_DECISION = (
    "proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/"
    "phase5_release_decision.md"
)
PHASE5_SURFACE_ADJUDICATION = (
    "proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/"
    "phase5_surface_adjudication.md"
)


def _canonical_source_root(repo_root: Path) -> Path:
    return repo_root / "code" / "source"


def _candidate_site_packages(repo_root: Path) -> tuple[Path, ...]:
    roots = (
        repo_root / ".venv",
        repo_root / "code" / ".venv",
        repo_root / ".venv_release_smoke",
        repo_root / "code" / ".venv_release_smoke",
    )
    candidates: list[Path] = []
    for root in roots:
        candidates.extend(sorted(root.glob("lib/python*/site-packages")))
    return tuple(path for path in candidates if path.exists())


def _readme_path(repo_root: Path) -> Path:
    if (repo_root / "README.md").exists():
        return repo_root / "README.md"
    return repo_root / "ZPE-XR" / "README.md"

def _doc_path(repo_root: Path, relative: str) -> Path:
    candidate = repo_root / relative
    if candidate.exists():
        return candidate
    return repo_root / "ZPE-XR" / relative


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    source_root = _canonical_source_root(repo_root)
    if not source_root.exists():
        raise RuntimeError(f"canonical source root not found for verify.py: {source_root}")
    for site_packages in _candidate_site_packages(repo_root):
        site_packages_str = str(site_packages)
        if site_packages_str not in sys.path:
            sys.path.append(site_packages_str)

    readme_path = _readme_path(repo_root)
    architecture_doc = _doc_path(repo_root, "docs/ARCHITECTURE.md")
    legal_boundaries_doc = _doc_path(repo_root, "docs/LEGAL_BOUNDARIES.md")
    checks = {
        "repo_root": str(repo_root),
        "canonical_source_root": str(source_root),
        "site_packages": [str(path) for path in _candidate_site_packages(repo_root)],
        "phase5_benchmark_present": (repo_root / PHASE5_BENCHMARK).exists(),
        "phase6_comparator_present": (repo_root / PHASE6_COMPARATOR).exists(),
        "phase4_cold_start_present": (repo_root / PHASE4_COLD_START).exists(),
        "phase5_release_decision_present": (repo_root / PHASE5_RELEASE_DECISION).exists(),
        "phase5_surface_adjudication_present": (repo_root / PHASE5_SURFACE_ADJUDICATION).exists(),
        "architecture_doc_present": architecture_doc.exists(),
        "legal_boundaries_doc_present": legal_boundaries_doc.exists(),
        "root_readme_present": readme_path.exists(),
    }
    try:
        import zpe_xr  # noqa: PLC0415
    except ModuleNotFoundError as exc:
        checks["package_import"] = False
        checks["package_import_error"] = f"{exc.__class__.__name__}: {exc}"
        checks["package_version"] = None
        checks["package_version_is_placeholder"] = True
        print(json.dumps(checks, indent=2, sort_keys=True))
        return 2

    checks["package_import"] = True
    checks["package_version"] = getattr(zpe_xr, "__version__", "unknown")
    checks["package_version_is_placeholder"] = getattr(zpe_xr, "__version__", "0.0.0") == "0.0.0"
    print(json.dumps(checks, indent=2, sort_keys=True))
    required_truthy = [
        "package_import",
        "phase5_benchmark_present",
        "phase6_comparator_present",
        "phase4_cold_start_present",
        "phase5_release_decision_present",
        "phase5_surface_adjudication_present",
        "architecture_doc_present",
        "legal_boundaries_doc_present",
        "root_readme_present",
    ]
    ok = all(checks[key] for key in required_truthy) and not checks["package_version_is_placeholder"]
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
