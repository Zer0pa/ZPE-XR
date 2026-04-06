#!/usr/bin/env python3
"""Run the Phase 6 Mac-local comparator benchmark."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import os
import sys
from typing import Any, Dict

from _bootstrap import activate_source_root

ROOT = activate_source_root(__file__)

from zpe_xr.comet_utils import (
    append_run_manifest,
    create_experiment,
    experiment_key,
    git_head,
    log_asset_if_exists,
    log_mapping,
)
from zpe_xr.io_utils import write_json
from zpe_xr.phase6_benchmarks import benchmark_report, render_markdown
from zpe_xr.runtime_paths import artifact_run_id, resolve_artifact_dir


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=90)
    parser.add_argument("--gesture", default="mixed")
    parser.add_argument("--seed", type=int, default=6607)
    parser.add_argument("--iterations", type=int, default=60)
    parser.add_argument("--attempt-contactpose", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    run_id = artifact_run_id()
    artifact_dir = resolve_artifact_dir(ROOT)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    experiment = create_experiment(
        name=f"phase6-mac-comparator-{run_id}",
        tags=["phase-6", "mac-local", "comparator"],
        parameters={
            "artifact_run_id": run_id,
            "cwd": str(ROOT),
            "git_head": git_head(ROOT),
            "python": sys.executable,
            "frames": args.frames,
            "gesture": args.gesture,
            "seed": args.seed,
            "iterations": args.iterations,
            "attempt_contactpose": args.attempt_contactpose,
        },
    )
    experiment_id = experiment_key(experiment) if experiment is not None else None

    summary: Dict[str, Any]
    if experiment is None or experiment_id is None:
        summary = {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "artifact_run_id": run_id,
            "artifact_dir": str(artifact_dir),
            "execution_status": "BLOCKED_TELEMETRY",
            "reason": "Comet experiment creation did not return a non-null experiment key.",
            "comet": {
                "enabled": experiment is not None,
                "experiment_key": experiment_id,
                "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
                "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
            },
        }
    else:
        try:
            summary = {
                "generated_at_utc": datetime.now(UTC).isoformat(),
                "artifact_run_id": run_id,
                "artifact_dir": str(artifact_dir),
                "execution_status": "EXECUTED",
                "comet": {
                    "enabled": True,
                    "experiment_key": experiment_id,
                    "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
                    "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
                },
                "benchmark": benchmark_report(
                    stage_code_root=ROOT,
                    num_frames=args.frames,
                    gesture=args.gesture,
                    seed=args.seed,
                    iterations=args.iterations,
                    attempt_contactpose=args.attempt_contactpose,
                ),
            }
        except Exception as exc:  # noqa: BLE001
            summary = {
                "generated_at_utc": datetime.now(UTC).isoformat(),
                "artifact_run_id": run_id,
                "artifact_dir": str(artifact_dir),
                "execution_status": "FAILED_EXECUTION",
                "reason": str(exc),
                "error_type": type(exc).__name__,
                "comet": {
                    "enabled": True,
                    "experiment_key": experiment_id,
                    "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
                    "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
                },
            }

    write_json(artifact_dir / "phase6_mac_comparator_benchmark.json", summary)
    if "benchmark" in summary:
        (artifact_dir / "phase6_mac_comparator_benchmark.md").write_text(
            render_markdown(summary["benchmark"]),
            encoding="utf-8",
        )
        log_mapping(experiment, "phase6.mac_comparator", summary["benchmark"])

    append_run_manifest(
        artifact_dir / "comet_run_manifest.json",
        {
            "name": f"phase6-mac-comparator-{run_id}",
            "experiment_key": experiment_id,
            "phase": "06",
            "artifact_dir": str(artifact_dir),
            "execution_status": summary["execution_status"],
        },
    )

    for name in [
        "phase6_mac_comparator_benchmark.json",
        "phase6_mac_comparator_benchmark.md",
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

    print(f"Phase 6 Mac comparator benchmark complete. STATUS={summary['execution_status']}")
    return 0 if summary["execution_status"] == "EXECUTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
