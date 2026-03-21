"""Runtime path helpers for root and staged execution surfaces."""

from __future__ import annotations

from datetime import UTC, datetime
import os
from pathlib import Path

_STAGED_CODE_DIRNAME = "code"
_STAGED_PROOFS_DIRNAME = "proofs"
_CACHED_RUN_ID: str | None = None


def repo_root_from(anchor_path: str | Path) -> Path:
    anchor = Path(anchor_path).resolve()
    return anchor.parents[1] if anchor.is_file() else anchor


def is_staged_code_root(root: Path) -> bool:
    return root.name == _STAGED_CODE_DIRNAME and (root.parent / _STAGED_PROOFS_DIRNAME).exists()


def canonical_root(root: Path) -> Path:
    if is_staged_code_root(root):
        return root.parent.parent
    return root


def staged_repo_root(root: Path) -> Path:
    if is_staged_code_root(root):
        return root.parent
    return root / "ZPE-XR"


def artifact_run_id() -> str:
    env_run_id = os.getenv("ZPE_XR_ARTIFACT_RUN_ID", "").strip()
    if env_run_id:
        return env_run_id

    global _CACHED_RUN_ID
    if _CACHED_RUN_ID is None:
        _CACHED_RUN_ID = datetime.now(UTC).strftime("%Y-%m-%d_zpe_xr_live_%H%M%S")
    return _CACHED_RUN_ID


def artifact_base_dir(root: Path) -> Path:
    if is_staged_code_root(root):
        return root.parent / _STAGED_PROOFS_DIRNAME / "artifacts"
    return root / "artifacts"


def resolve_artifact_dir(root: Path) -> Path:
    return artifact_base_dir(root) / artifact_run_id()


def artifact_ref(root: Path, *parts: str) -> str:
    prefix = "proofs/artifacts" if is_staged_code_root(root) else "artifacts"
    suffix = "/".join(part.strip("/") for part in parts if part)
    return f"{prefix}/{artifact_run_id()}/{suffix}" if suffix else f"{prefix}/{artifact_run_id()}"


def canonical_relpath(root: Path, target: Path) -> str:
    return str(target.resolve().relative_to(canonical_root(root)))
