#!/usr/bin/env python3
"""Run the pre-RunPod Phase 2 workflow with Comet logging."""

from __future__ import annotations

from datetime import datetime, UTC
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_xr.comet_utils import (
    append_run_manifest,
    create_experiment,
    experiment_key,
    git_head,
    log_asset_if_exists,
    log_mapping,
)
from zpe_xr.io_utils import read_json, write_json
from zpe_xr.runtime_paths import artifact_run_id, resolve_artifact_dir


def _run_step(name: str, command: List[str], *, env: Dict[str, str]) -> Dict[str, Any]:
    started = datetime.now(UTC).isoformat()
    t0 = perf_counter()
    proc = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True, env=env)
    duration_s = perf_counter() - t0
    return {
        "name": name,
        "command": command,
        "returncode": proc.returncode,
        "duration_s": duration_s,
        "started_at_utc": started,
        "ended_at_utc": datetime.now(UTC).isoformat(),
        "stdout": proc.stdout[-12000:],
        "stderr": proc.stderr[-12000:],
    }


def _load_json_if_exists(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    return read_json(path)


def main() -> int:
    run_id = artifact_run_id()
    artifact_dir = resolve_artifact_dir(ROOT)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env.setdefault("PYTHONHASHSEED", "0")
    env["ZPE_XR_ARTIFACT_RUN_ID"] = run_id
    env["ZPE_XR_PHASE"] = "phase2-pre-runpod"
    existing_pythonpath = env.get("PYTHONPATH", "").strip()
    env["PYTHONPATH"] = str(SRC) if not existing_pythonpath else f"{str(SRC)}:{existing_pythonpath}"

    experiment = create_experiment(
        name=f"phase2-pre-runpod-{run_id}",
        tags=["phase-2", "pre-runpod", "direct-comparator", "runtime-closure"],
        parameters={
            "artifact_run_id": run_id,
            "cwd": str(ROOT),
            "git_head": git_head(ROOT),
            "python": sys.executable,
        },
    )

    steps = [
        ("phase2_direct_comparator", [sys.executable, "scripts/run_phase2_direct_comparator.py"]),
        ("phase2_runtime_closure", [sys.executable, "scripts/run_phase2_runtime_closure.py"]),
        ("phase2_outward_corpus", [sys.executable, "scripts/run_phase2_outward_corpus.py"]),
        ("tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]),
        ("sync_staged_repo", [sys.executable, "scripts/sync_staged_repo.py", "--run-id", run_id]),
    ]

    step_logs: List[Dict[str, Any]] = []
    for name, command in steps:
        result = _run_step(name, command, env=env)
        step_logs.append(result)
        log_mapping(experiment, f"steps.{name}", result)

    write_json(artifact_dir / "phase2_step_logs.json", {"steps": step_logs})

    summary: Dict[str, Any] = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "artifact_run_id": run_id,
        "artifact_dir": str(artifact_dir),
        "all_steps_passed": all(step["returncode"] == 0 for step in step_logs),
        "step_status": {step["name"]: step["returncode"] for step in step_logs},
        "comet": {
            "enabled": experiment is not None,
            "experiment_key": experiment_key(experiment),
            "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
            "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
        },
    }

    for name in [
        "phase2_comparator_matrix.json",
        "phase2_runtime_probe_matrix.json",
        "phase2_outward_corpus_probe.json",
    ]:
        payload = _load_json_if_exists(artifact_dir / name)
        if payload is not None:
            summary[name] = payload
            log_mapping(experiment, name.removesuffix(".json"), payload)

    write_json(artifact_dir / "phase2_execution_summary.json", summary)
    append_run_manifest(
        artifact_dir / "comet_run_manifest.json",
        {
            "name": f"phase2-pre-runpod-{run_id}",
            "experiment_key": experiment_key(experiment),
            "phase": "02",
            "artifact_dir": str(artifact_dir),
            "all_steps_passed": summary["all_steps_passed"],
        },
    )

    for name in [
        "phase2_step_logs.json",
        "phase2_execution_summary.json",
        "phase2_comparator_matrix.json",
        "phase2_comparator_matrix.md",
        "phase2_runtime_probe_matrix.json",
        "phase2_runtime_probe_matrix.md",
        "phase2_outward_corpus_probe.json",
        "phase2_outward_corpus_probe.md",
        "comet_run_manifest.json",
        "staged_sync_report.json",
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

    print(f"Phase 2 pre-RunPod workflow complete. PASS={summary['all_steps_passed']}")
    return 0 if summary["all_steps_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
