#!/usr/bin/env python3
"""Run the Phase 5 ContactPose multi-sequence benchmark with mandatory Comet logging."""

from __future__ import annotations

from datetime import UTC, datetime
import os
from pathlib import Path
import shutil
import sys
from typing import Any, Dict

from _bootstrap import activate_source_root

ROOT = activate_source_root(__file__)

from zpe_xr.codec import XRCodec
from zpe_xr.comet_utils import (
    append_run_manifest,
    create_experiment,
    experiment_key,
    git_head,
    log_asset_if_exists,
    log_mapping,
)
from zpe_xr.io_utils import write_json
from zpe_xr.outward_workload import (
    CONTACTPOSE_SAMPLE_FILENAME,
    ensure_contactpose_sample,
    evaluate_contactpose_multi_sequence_workload,
    render_contactpose_multi_sequence_markdown,
)
from zpe_xr.runtime_paths import artifact_base_dir, artifact_run_id, resolve_artifact_dir


MIN_CONTACTPOSE_FREE_GIB = 5.0
OBJECT_NAMES = ("mug", "wine_glass", "bowl", "camera", "binoculars")


def _write_markdown(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _disk_headroom_gib(root: Path) -> float:
    return shutil.disk_usage(root).free / (1024**3)


def _cleanup_sample(sample_zip: Path | None) -> Dict[str, Any]:
    cleanup: Dict[str, Any] = {"removed": False, "path": None}
    if sample_zip is None:
        return cleanup

    resolved = sample_zip.resolve()
    cleanup["path"] = str(resolved)
    if resolved.exists() and resolved.name == CONTACTPOSE_SAMPLE_FILENAME:
        resolved.unlink()
        cleanup["removed"] = True
        try:
            resolved.parent.rmdir()
        except OSError:
            pass
    return cleanup


def _workspace_usage(path: Path) -> Dict[str, Any]:
    total_bytes = 0
    for child in path.rglob("*"):
        if child.is_file():
            total_bytes += child.stat().st_size
    return {
        "path": str(path),
        "bytes": total_bytes,
        "megabytes": total_bytes / (1024**2),
    }


def main() -> int:
    run_id = artifact_run_id()
    artifact_dir = resolve_artifact_dir(ROOT)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    experiment = create_experiment(
        name=f"phase5-contactpose-multi-sequence-{run_id}",
        tags=["phase-5", "contactpose", "multi-sequence"],
        parameters={
            "artifact_run_id": run_id,
            "cwd": str(ROOT),
            "git_head": git_head(ROOT),
            "python": sys.executable,
            "objects": list(OBJECT_NAMES),
        },
    )

    experiment_id = experiment_key(experiment)
    free_gib = _disk_headroom_gib(ROOT)
    summary: Dict[str, Any]
    sample_zip: Path | None = None

    if free_gib < MIN_CONTACTPOSE_FREE_GIB:
        summary = {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "artifact_run_id": run_id,
            "artifact_dir": str(artifact_dir),
            "execution_status": "BLOCKED_LOCAL_RESOURCES",
            "reason": "Insufficient free disk headroom for ContactPose execution.",
            "preflight": {
                "disk_headroom_gib": free_gib,
                "min_required_gib": MIN_CONTACTPOSE_FREE_GIB,
            },
            "comet": {
                "enabled": experiment is not None,
                "experiment_key": experiment_id,
                "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
                "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
            },
        }
    elif experiment is None or experiment_id is None:
        summary = {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "artifact_run_id": run_id,
            "artifact_dir": str(artifact_dir),
            "execution_status": "BLOCKED_TELEMETRY",
            "reason": "Comet experiment creation did not return a non-null experiment key.",
            "preflight": {
                "disk_headroom_gib": free_gib,
                "min_required_gib": MIN_CONTACTPOSE_FREE_GIB,
            },
            "comet": {
                "enabled": experiment is not None,
                "experiment_key": experiment_id,
                "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
                "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
            },
        }
    else:
        codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)
        try:
            search_root = ROOT.parent.parent / "artifacts"
            if not search_root.exists():
                search_root = artifact_base_dir(ROOT)
            sample_zip = ensure_contactpose_sample(
                artifact_dir / "downloads" / CONTACTPOSE_SAMPLE_FILENAME,
                search_root=search_root,
            )
            summary = {
                "generated_at_utc": datetime.now(UTC).isoformat(),
                "artifact_run_id": run_id,
                "artifact_dir": str(artifact_dir),
                "execution_status": "EXECUTED",
                "preflight": {
                    "disk_headroom_gib": free_gib,
                    "min_required_gib": MIN_CONTACTPOSE_FREE_GIB,
                },
                "comet": {
                    "enabled": True,
                    "experiment_key": experiment_id,
                    "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
                    "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
                },
                "benchmark": evaluate_contactpose_multi_sequence_workload(
                    sample_zip,
                    codec=codec,
                    object_names=OBJECT_NAMES,
                ),
            }
        except Exception as exc:  # noqa: BLE001
            summary = {
                "generated_at_utc": datetime.now(UTC).isoformat(),
                "artifact_run_id": run_id,
                "artifact_dir": str(artifact_dir),
                "execution_status": "BLOCKED_FETCH_OR_ENVIRONMENT",
                "reason": str(exc),
                "error_type": type(exc).__name__,
                "preflight": {
                    "disk_headroom_gib": free_gib,
                    "min_required_gib": MIN_CONTACTPOSE_FREE_GIB,
                },
                "comet": {
                    "enabled": True,
                    "experiment_key": experiment_id,
                    "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
                    "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
                },
            }
        finally:
            summary["cleanup"] = _cleanup_sample(sample_zip)
            summary["workspace_usage_after_cleanup"] = _workspace_usage(ROOT.parent.parent)

    write_json(artifact_dir / "phase5_multi_sequence_benchmark.json", summary)
    if "benchmark" in summary:
        _write_markdown(
            artifact_dir / "phase5_multi_sequence_benchmark.md",
            render_contactpose_multi_sequence_markdown(summary["benchmark"]),
        )
    log_mapping(experiment, "phase5.multi_sequence", summary)

    append_run_manifest(
        artifact_dir / "comet_run_manifest.json",
        {
            "name": f"phase5-contactpose-multi-sequence-{run_id}",
            "experiment_key": experiment_id,
            "phase": "05",
            "artifact_dir": str(artifact_dir),
            "execution_status": summary["execution_status"],
        },
    )

    for name in [
        "phase5_multi_sequence_benchmark.json",
        "phase5_multi_sequence_benchmark.md",
        "comet_run_manifest.json",
    ]:
        log_asset_if_exists(experiment, artifact_dir / name)

    if experiment is not None:
        try:
            experiment.flush(timeout=30)
        except Exception:  # noqa: BLE001
            pass
        try:
            experiment.end()
        except Exception:  # noqa: BLE001
            pass

    print(f"Phase 5 ContactPose multi-sequence benchmark complete. STATUS={summary['execution_status']}")
    return 0 if summary["execution_status"] == "EXECUTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
