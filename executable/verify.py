#!/usr/bin/env python3
"""Root-owned staged-repo verification entrypoint."""

from __future__ import annotations

import json
from pathlib import Path
import sys


PHASE1_RUN_ID = "2026-03-20_zpe_xr_wave1_live"
PHASE2_RUN_ID = "2026-03-20_zpe_xr_phase2_pre_runpod"


def _candidate_source_root(repo_root: Path) -> Path | None:
    for candidate in (
        repo_root / "source",
        repo_root / "src",
        repo_root / "code" / "source",
        repo_root / "code" / "src",
    ):
        if candidate.exists():
            return candidate
    return None


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


def _artifact_root(repo_root: Path) -> Path:
    if (repo_root / "artifacts").exists():
        return repo_root / "artifacts"
    return repo_root / "proofs" / "artifacts"


def _proof_root(repo_root: Path) -> Path:
    if (repo_root / "proofs").exists():
        return repo_root / "proofs"
    return repo_root / "ZPE-XR" / "proofs"


def _audit_limits_path(repo_root: Path) -> Path:
    if (repo_root / "PUBLIC_AUDIT_LIMITS.md").exists():
        return repo_root / "PUBLIC_AUDIT_LIMITS.md"
    return repo_root / "ZPE-XR" / "PUBLIC_AUDIT_LIMITS.md"


def _readme_path(repo_root: Path) -> Path:
    if (repo_root / "README.md").exists():
        return repo_root / "README.md"
    return repo_root / "ZPE-XR" / "README.md"


def _latest_phase3_dir(repo_root: Path) -> Path | None:
    phase3_dirs = sorted(_artifact_root(repo_root).glob("*phase3_packaging*"))
    if not phase3_dirs:
        return None
    return phase3_dirs[-1]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    source_root = _candidate_source_root(repo_root)
    if source_root is None:
        raise RuntimeError("no source root found for verify.py")
    sys.path.insert(0, str(source_root))
    for site_packages in _candidate_site_packages(repo_root):
        site_packages_str = str(site_packages)
        if site_packages_str not in sys.path:
            sys.path.insert(1, site_packages_str)

    phase3_dir = _latest_phase3_dir(repo_root)
    artifact_root = _artifact_root(repo_root)
    proof_root = _proof_root(repo_root)
    audit_limits = _audit_limits_path(repo_root)
    readme_path = _readme_path(repo_root)
    checks = {
        "repo_root": str(repo_root),
        "source_root": str(source_root),
        "site_packages": [str(path) for path in _candidate_site_packages(repo_root)],
        "fresh_phase1_bundle_present": (artifact_root / PHASE1_RUN_ID).exists(),
        "fresh_phase2_bundle_present": (artifact_root / PHASE2_RUN_ID).exists(),
        "phase3_bundle_present": phase3_dir is not None,
        "phase3_bundle": str(phase3_dir) if phase3_dir is not None else None,
        "final_status_present": (proof_root / "FINAL_STATUS.md").exists(),
        "release_readiness_present": (proof_root / "RELEASE_READINESS_REPORT.md").exists(),
        "audit_limits_present": audit_limits.exists(),
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
        "fresh_phase1_bundle_present",
        "fresh_phase2_bundle_present",
        "phase3_bundle_present",
        "final_status_present",
        "release_readiness_present",
        "audit_limits_present",
        "root_readme_present",
    ]
    ok = all(checks[key] for key in required_truthy) and not checks["package_version_is_placeholder"]
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
