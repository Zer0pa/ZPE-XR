"""Cold-start staged package audit helpers for Phase 4."""

from __future__ import annotations

from pathlib import Path
import shutil
from typing import Any


FORBIDDEN_PHRASES = {
    "ready_for_public_release": "ready for public release",
    "photon_displaced": "photon is displaced",
    "market_leading_runtime": "market-leading xr runtime",
}

REQUIRED_MARKERS = {
    "comparator_gate_fail": ("proofs/RELEASE_READINESS_REPORT.md", "0/5 FAIL"),
    "photon_open": ("proofs/FINAL_STATUS.md", "Photon displacement remains open"),
    "runtime_paused": ("proofs/FINAL_STATUS.md", "PAUSED_EXTERNAL"),
}


def copy_staged_snapshot(stage_root: Path, snapshot_root: Path) -> Path:
    if snapshot_root.exists():
        shutil.rmtree(snapshot_root)
    shutil.copytree(
        stage_root,
        snapshot_root,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"),
    )
    return snapshot_root


def audit_outward_claims(snapshot_root: Path) -> dict[str, Any]:
    checked_files = [
        "README.md",
        "PUBLIC_AUDIT_LIMITS.md",
        "proofs/FINAL_STATUS.md",
        "proofs/RELEASE_READINESS_REPORT.md",
    ]
    forbidden_hits = []
    for rel_path in checked_files:
        text = (snapshot_root / rel_path).read_text(encoding="utf-8").lower()
        for hit_id, phrase in FORBIDDEN_PHRASES.items():
            if phrase in text:
                forbidden_hits.append({"id": hit_id, "file": rel_path, "phrase": phrase})

    missing_required_markers = []
    for marker_id, (rel_path, needle) in REQUIRED_MARKERS.items():
        text = (snapshot_root / rel_path).read_text(encoding="utf-8")
        if needle not in text:
            missing_required_markers.append({"id": marker_id, "file": rel_path, "needle": needle})

    return {
        "checked_files": checked_files,
        "forbidden_hits": forbidden_hits,
        "missing_required_markers": missing_required_markers,
        "pass": not forbidden_hits and not missing_required_markers,
    }
