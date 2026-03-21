"""Shared bootstrap helpers for repo-local scripts."""

from __future__ import annotations

from pathlib import Path
import sys


def activate_source_root(script_file: str | Path) -> Path:
    root = Path(script_file).resolve().parents[1]
    source_root = root / "source"
    if not source_root.exists():
        raise RuntimeError(f"canonical source root missing: {source_root}")
    source_root_str = str(source_root)
    if source_root_str not in sys.path:
        sys.path.insert(0, source_root_str)
    return root
