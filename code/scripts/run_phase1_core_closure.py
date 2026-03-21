#!/usr/bin/env python3
"""Run the phase-1 frozen v1 closure workflow with Comet logging."""

from __future__ import annotations

from datetime import datetime, UTC
import json
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


def _normalize_root_artifacts(artifact_dir: Path, root: Path) -> Dict[str, Any]:
    legacy_lane_root = "/Users/prinivenpillay/ZPE Multimodality/ZPE XR"

    updated_files = 0
    for path in artifact_dir.rglob("*"):
        if not path.is_file() or path.suffix not in {".json", ".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        rewritten = text.replace(legacy_lane_root, str(root))
        if rewritten != text:
            path.write_text(rewritten, encoding="utf-8")
            updated_files += 1

    report = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "artifact_dir": str(artifact_dir),
        "legacy_lane_root": legacy_lane_root,
        "current_lane_root": str(root),
        "updated_files": updated_files,
    }
    write_json(artifact_dir / "artifact_path_normalization.json", report)
    return report


def _write_regression_results(artifact_dir: Path, step_result: Dict[str, Any]) -> None:
    content = step_result["stdout"]
    if step_result["stderr"]:
        if content and not content.endswith("\n"):
            content += "\n"
        content += step_result["stderr"]
    (artifact_dir / "regression_results.txt").write_text(content, encoding="utf-8")


def _write_gate_execution_matrix(artifact_dir: Path, step_logs: List[Dict[str, Any]]) -> None:
    artifact_ref = f"artifacts/{artifact_dir.name}"
    by_name = {step["name"]: step["returncode"] for step in step_logs}
    matrix = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "gates": [
            {
                "gate": "A",
                "status": "PASS"
                if by_name.get("lock_resources") == 0 and by_name.get("generate_fixtures") == 0
                else "FAIL",
                "evidence": [
                    "fixtures/resource_lock.json",
                    "fixtures/synthetic_hot3d_snapshot_v1.json",
                    "fixtures/benchmark_config.json",
                ],
            },
            {
                "gate": "B",
                "status": "PASS" if by_name.get("gate_b") == 0 else "FAIL",
                "evidence": [
                    f"{artifact_ref}/xr_compression_benchmark.json",
                    f"{artifact_ref}/xr_fidelity_eval.json",
                    f"{artifact_ref}/xr_latency_benchmark.json",
                ],
            },
            {
                "gate": "C",
                "status": "PASS" if by_name.get("gate_c") == 0 else "FAIL",
                "evidence": [
                    f"{artifact_ref}/xr_packet_loss_resilience.json",
                    f"{artifact_ref}/xr_gesture_eval.json",
                    f"{artifact_ref}/xr_bandwidth_eval.json",
                ],
            },
            {
                "gate": "D",
                "status": "PASS" if by_name.get("gate_d") == 0 else "FAIL",
                "evidence": [
                    f"{artifact_ref}/gate_d_summary.json",
                    f"{artifact_ref}/falsification_results.md",
                ],
            },
            {
                "gate": "E-base",
                "status": "PASS" if by_name.get("gate_e") == 0 else "FAIL",
                "evidence": [
                    f"{artifact_ref}/handoff_manifest.json",
                    f"{artifact_ref}/quality_gate_scorecard.json",
                ],
            },
        ],
    }
    write_json(artifact_dir / "gate_execution_matrix.json", matrix)


def _log_file_outputs(experiment: Any | None, artifact_dir: Path) -> None:
    for name in [
        "phase1_execution_summary.json",
        "phase1_step_logs.json",
        "artifact_path_normalization.json",
        "comet_run_manifest.json",
        "xr_compression_benchmark.json",
        "xr_fidelity_eval.json",
        "xr_latency_benchmark.json",
        "xr_packet_loss_resilience.json",
        "xr_gesture_eval.json",
        "xr_bandwidth_eval.json",
        "gate_d_summary.json",
        "claim_status_delta.md",
        "integration_readiness_contract.json",
        "quality_gate_scorecard.json",
        "handoff_manifest.json",
        "staged_sync_report.json",
    ]:
        log_asset_if_exists(experiment, artifact_dir / name)


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
    env["ZPE_XR_PHASE"] = "base"

    experiment = create_experiment(
        name=f"phase1-core-closure-{run_id}",
        tags=["phase-1", "frozen-v1", "core-closure"],
        parameters={
            "artifact_run_id": run_id,
            "cwd": str(ROOT),
            "git_head": git_head(ROOT),
            "python": sys.executable,
        },
    )

    steps = [
        ("lock_resources", [sys.executable, "scripts/lock_resources.py"]),
        ("generate_fixtures", [sys.executable, "scripts/generate_fixtures.py"]),
        ("tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]),
        ("gate_b", [sys.executable, "scripts/run_gate_b.py"]),
        ("gate_c", [sys.executable, "scripts/run_gate_c.py"]),
        ("gate_d", [sys.executable, "scripts/run_gate_d.py"]),
        ("gate_e", [sys.executable, "scripts/run_gate_e.py"]),
    ]

    step_logs: List[Dict[str, Any]] = []
    for name, command in steps:
        result = _run_step(name, command, env=env)
        step_logs.append(result)
        log_mapping(experiment, f"steps.{name}", result)
        if name == "tests":
            _write_regression_results(artifact_dir, result)

    _write_gate_execution_matrix(artifact_dir, step_logs)

    normalization = _normalize_root_artifacts(artifact_dir, ROOT)
    log_mapping(experiment, "artifact_normalization", normalization)

    sync_result = _run_step("sync_staged_repo", [sys.executable, "scripts/sync_staged_repo.py", "--run-id", run_id], env=env)
    step_logs.append(sync_result)
    log_mapping(experiment, "steps.sync_staged_repo", sync_result)

    write_json(artifact_dir / "phase1_step_logs.json", {"steps": step_logs})

    summary: Dict[str, Any] = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "artifact_run_id": run_id,
        "artifact_dir": str(artifact_dir),
        "all_steps_passed": all(step["returncode"] == 0 for step in step_logs),
        "step_status": {step["name"]: step["returncode"] for step in step_logs},
    }

    for name in [
        "xr_compression_benchmark.json",
        "xr_fidelity_eval.json",
        "xr_latency_benchmark.json",
        "xr_packet_loss_resilience.json",
        "xr_gesture_eval.json",
        "xr_bandwidth_eval.json",
        "gate_d_summary.json",
        "quality_gate_scorecard.json",
        "gate_execution_matrix.json",
        "handoff_manifest.json",
    ]:
        payload = _load_json_if_exists(artifact_dir / name)
        if payload is not None:
            summary[name] = payload
            log_mapping(experiment, name.removesuffix(".json"), payload)

    summary["comet"] = {
        "enabled": experiment is not None,
        "experiment_key": experiment_key(experiment),
        "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
        "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
    }
    write_json(artifact_dir / "phase1_execution_summary.json", summary)

    append_run_manifest(
        artifact_dir / "comet_run_manifest.json",
        {
            "name": f"phase1-core-closure-{run_id}",
            "experiment_key": experiment_key(experiment),
            "phase": "01",
            "artifact_dir": str(artifact_dir),
            "all_steps_passed": summary["all_steps_passed"],
        },
    )

    _log_file_outputs(experiment, artifact_dir)

    if experiment is not None:
        experiment.log_asset(str(artifact_dir / "phase1_step_logs.json"))
        experiment.log_asset(str(artifact_dir / "phase1_execution_summary.json"))
        experiment.flush()
        experiment.end()

    print(f"Phase 1 core closure run complete. PASS={summary['all_steps_passed']}")
    return 0 if summary["all_steps_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
