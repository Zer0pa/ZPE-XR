#!/usr/bin/env python3
"""Run the Phase 4 ContactPose outward-safe benchmark with Comet logging."""

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
    evaluate_contactpose_workload,
    render_contactpose_benchmark_markdown,
)
from zpe_xr.runtime_paths import artifact_base_dir, artifact_run_id, resolve_artifact_dir


MIN_CONTACTPOSE_FREE_GIB = 5.0


def _write_markdown(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _disk_headroom_gib(root: Path) -> float:
    return shutil.disk_usage(root).free / (1024**3)


def _blocked_markdown(summary: Dict[str, Any]) -> str:
    preflight = summary.get("preflight", {})
    preflight_lines = []
    if "disk_headroom_gib" in preflight and "min_required_gib" in preflight:
        preflight_lines.extend(
            [
                "## Preflight",
                "",
                f"- free disk headroom: `{preflight['disk_headroom_gib']:.2f} GiB`",
                f"- minimum required: `{preflight['min_required_gib']:.2f} GiB`",
                "",
            ]
        )
    error_type = summary.get("error_type")
    error_line = f"- error_type: `{error_type}`\n" if error_type else ""
    return f"""# Phase 4 ContactPose Benchmark

## Execution Status

- status: `{summary['execution_status']}`
- reason: `{summary['reason']}`
{error_line}

{chr(10).join(preflight_lines).rstrip()}

## Verdict

- outward-safe benchmark verdict: `{summary['benchmark_verdict']}`
"""


def _cleanup_download(sample_zip: Path | None, download_dir: Path) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"removed": False, "path": None}
    if sample_zip is None:
        return payload

    resolved_sample = sample_zip.resolve()
    payload["path"] = str(resolved_sample)
    if resolved_sample.is_relative_to(download_dir.resolve()) and resolved_sample.exists():
        resolved_sample.unlink()
        payload["removed"] = True

    try:
        download_dir.rmdir()
    except OSError:
        pass
    return payload


def main() -> int:
    run_id = artifact_run_id()
    artifact_dir = resolve_artifact_dir(ROOT)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    experiment = create_experiment(
        name=f"phase4-contactpose-{run_id}",
        tags=["phase-4", "contactpose", "outward-safe"],
        parameters={
            "artifact_run_id": run_id,
            "cwd": str(ROOT),
            "git_head": git_head(ROOT),
            "python": sys.executable,
        },
    )

    free_gib = _disk_headroom_gib(ROOT)
    summary: Dict[str, Any]
    if free_gib < MIN_CONTACTPOSE_FREE_GIB:
        summary = {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "artifact_run_id": run_id,
            "artifact_dir": str(artifact_dir),
            "execution_status": "BLOCKED_LOCAL_RESOURCES",
            "reason": "Insufficient free disk headroom for the ContactPose sample download.",
            "benchmark_verdict": "INCONCLUSIVE",
            "preflight": {
                "disk_headroom_gib": free_gib,
                "min_required_gib": MIN_CONTACTPOSE_FREE_GIB,
            },
            "comet": {
                "enabled": experiment is not None,
                "experiment_key": experiment_key(experiment),
                "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
                "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
            },
        }
    else:
        download_dir = artifact_dir / "downloads"
        download_dir.mkdir(parents=True, exist_ok=True)
        codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)
        sample_zip: Path | None = None
        try:
            sample_zip = ensure_contactpose_sample(
                download_dir / CONTACTPOSE_SAMPLE_FILENAME,
                search_root=artifact_base_dir(ROOT),
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
                    "enabled": experiment is not None,
                    "experiment_key": experiment_key(experiment),
                    "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
                    "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
                },
                "benchmark": evaluate_contactpose_workload(sample_zip, codec=codec),
            }
        except Exception as exc:  # noqa: BLE001
            summary = {
                "generated_at_utc": datetime.now(UTC).isoformat(),
                "artifact_run_id": run_id,
                "artifact_dir": str(artifact_dir),
                "execution_status": "BLOCKED_FETCH_OR_ENVIRONMENT",
                "reason": str(exc),
                "error_type": type(exc).__name__,
                "benchmark_verdict": "INCONCLUSIVE",
                "preflight": {
                    "disk_headroom_gib": free_gib,
                    "min_required_gib": MIN_CONTACTPOSE_FREE_GIB,
                },
                "comet": {
                    "enabled": experiment is not None,
                    "experiment_key": experiment_key(experiment),
                    "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
                    "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
                },
            }
        finally:
            summary["cleanup"] = _cleanup_download(sample_zip, download_dir)

    write_json(artifact_dir / "phase4_contactpose_benchmark.json", summary)
    if "benchmark" in summary:
        _write_markdown(
            artifact_dir / "phase4_contactpose_benchmark.md",
            render_contactpose_benchmark_markdown(summary["benchmark"]),
        )
    else:
        _write_markdown(artifact_dir / "phase4_contactpose_benchmark.md", _blocked_markdown(summary))
    log_mapping(experiment, "phase4.contactpose", summary)

    verdict = summary.get("benchmark", {}).get("acceptance", {}).get(
        "sovereign_verdict",
        summary.get("benchmark_verdict", "INCONCLUSIVE"),
    )

    append_run_manifest(
        artifact_dir / "comet_run_manifest.json",
        {
            "name": f"phase4-contactpose-{run_id}",
            "experiment_key": experiment_key(experiment),
            "phase": "04",
            "artifact_dir": str(artifact_dir),
            "verdict": verdict,
        },
    )

    for name in [
        "phase4_contactpose_benchmark.json",
        "phase4_contactpose_benchmark.md",
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

    print(f"Phase 4 ContactPose benchmark complete. VERDICT={verdict}")
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
