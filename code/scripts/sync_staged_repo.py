#!/usr/bin/env python3
"""Synchronize the staged ZPE-XR mirror from the canonical root workspace."""

from __future__ import annotations

import argparse
from datetime import datetime, UTC
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_xr.io_utils import write_json
from zpe_xr.runtime_paths import artifact_ref, canonical_root, resolve_artifact_dir, staged_repo_root


TEXT_SUFFIXES = {".json", ".md", ".txt"}
HISTORICAL_ARTIFACT_RUN_ID = "2026-02-20_zpe_xr_wave1"
COPY_GROUPS = [
    ("src", "code/src"),
    ("scripts", "code/scripts"),
    ("tests", "code/tests"),
    ("executable", "executable"),
    ("pyproject.toml", "code/pyproject.toml"),
    ("runbooks", "proofs/runbooks"),
]


def _ignore(_: str, names: List[str]) -> List[str]:
    ignored: List[str] = []
    for name in names:
        if name == "__pycache__" or name.endswith((".pyc", ".pyo")) or name.endswith(".egg-info"):
            ignored.append(name)
    return ignored


def _copy_tree(src: Path, dst: Path) -> int:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=_ignore)
    return sum(1 for path in dst.rglob("*") if path.is_file())


def _copy_file(src: Path, dst: Path) -> int:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return 1


def _rewrite_artifact_refs(base_dir: Path, replacements: Dict[str, str]) -> int:
    updated = 0
    for path in base_dir.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        rewritten = text
        for old_prefix, new_prefix in replacements.items():
            rewritten = rewritten.replace(old_prefix, new_prefix)
        if rewritten != text:
            path.write_text(rewritten, encoding="utf-8")
            updated += 1
    return updated


def _run_stage_fixture_generation(stage_code_root: Path) -> None:
    env = dict(os.environ)
    env.setdefault("PYTHONHASHSEED", "0")
    commands = [
        [sys.executable, "scripts/lock_resources.py"],
        [sys.executable, "scripts/generate_fixtures.py"],
    ]
    for command in commands:
        subprocess.run(command, cwd=str(stage_code_root), check=True, env=env)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    if args.run_id:
        import os

        os.environ["ZPE_XR_ARTIFACT_RUN_ID"] = args.run_id

    root = canonical_root(ROOT)
    stage_root = staged_repo_root(root)
    stage_code_root = stage_root / "code"
    stage_proofs_root = stage_root / "proofs"
    artifact_dir = resolve_artifact_dir(root)
    stage_artifact_dir = stage_proofs_root / "artifacts" / artifact_dir.name

    copied: List[Dict[str, Any]] = []
    for src_rel, dst_rel in COPY_GROUPS:
        src = root / src_rel
        dst = stage_root / dst_rel
        count = _copy_tree(src, dst) if src.is_dir() else _copy_file(src, dst)
        copied.append({"source": src_rel, "target": dst_rel, "files": count})

    _run_stage_fixture_generation(stage_code_root)

    copied_artifact_files = 0
    if artifact_dir.exists():
        if stage_artifact_dir.exists():
            shutil.rmtree(stage_artifact_dir)
        shutil.copytree(artifact_dir, stage_artifact_dir, ignore=_ignore)
        copied_artifact_files = sum(1 for path in stage_artifact_dir.rglob("*") if path.is_file())
        artifact_rewrites = {}
        for candidate in (root / "artifacts").iterdir():
            if candidate.is_dir():
                artifact_rewrites[f"artifacts/{candidate.name}"] = f"proofs/artifacts/{candidate.name}"
        _rewrite_artifact_refs(
            stage_artifact_dir,
            artifact_rewrites,
        )

    report = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "canonical_root": str(root),
        "stage_root": str(stage_root),
        "artifact_run_id": artifact_dir.name,
        "copied_groups": copied,
        "copied_artifact_files": copied_artifact_files,
        "stage_artifact_dir": str(stage_artifact_dir),
        "artifact_ref_root": artifact_ref(root),
        "artifact_ref_stage": f"proofs/artifacts/{artifact_dir.name}",
    }

    if artifact_dir.exists():
        write_json(artifact_dir / "staged_sync_report.json", report)
    write_json(stage_artifact_dir / "staged_sync_report.json" if stage_artifact_dir.exists() else stage_root / "staged_sync_report.json", report)

    print(f"Staged sync complete for run {artifact_dir.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
