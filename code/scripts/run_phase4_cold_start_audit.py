#!/usr/bin/env python3
"""Run the Phase 4 cold-start staged package and claim audit."""

from __future__ import annotations

from datetime import UTC, datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_xr.cold_start_audit import audit_outward_claims, copy_staged_snapshot
from zpe_xr.comet_utils import (
    append_run_manifest,
    create_experiment,
    experiment_key,
    git_head,
    log_asset_if_exists,
    log_mapping,
)
from zpe_xr.io_utils import write_json
from zpe_xr.runtime_paths import artifact_run_id, resolve_artifact_dir, staged_repo_root


def _run_step(name: str, command: List[str], *, cwd: Path) -> Dict[str, Any]:
    proc = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True)
    return {
        "name": name,
        "command": command,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-12000:],
        "stderr": proc.stderr[-12000:],
    }


def _install_smoke(snapshot_root: Path) -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="zpe_xr_phase4_cold_smoke_") as tmpdir:
        temp_root = Path(tmpdir)
        venv_dir = temp_root / "venv"
        python_bin = venv_dir / "bin" / "python"
        pip_bin = venv_dir / "bin" / "pip"
        commands = [
            [sys.executable, "-m", "venv", str(venv_dir)],
            [str(pip_bin), "install", "--upgrade", "pip"],
            [str(pip_bin), "install", str(snapshot_root / "code")],
            [
                str(python_bin),
                "-c",
                (
                    "import json, zpe_xr; "
                    "print(json.dumps({'package_import': True, 'version': zpe_xr.__version__}, sort_keys=True))"
                ),
            ],
        ]
        payload: Dict[str, Any] = {"commands": commands}
        for command in commands:
            proc = subprocess.run(command, capture_output=True, text=True, check=False)
            payload["last_stdout"] = proc.stdout[-12000:]
            payload["last_stderr"] = proc.stderr[-12000:]
            if proc.returncode != 0:
                payload["passed"] = False
                payload["returncode"] = proc.returncode
                return payload
        payload["passed"] = True
        payload["returncode"] = 0
        payload["result"] = json.loads(payload["last_stdout"])
        return payload


def main() -> int:
    run_id = artifact_run_id()
    artifact_dir = resolve_artifact_dir(ROOT)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    snapshot_root = artifact_dir / "cold_snapshot" / "ZPE-XR"
    stage_root = staged_repo_root(ROOT)
    experiment = create_experiment(
        name=f"phase4-cold-start-{run_id}",
        tags=["phase-4", "cold-start", "claim-audit"],
        parameters={
            "artifact_run_id": run_id,
            "cwd": str(ROOT),
            "git_head": git_head(ROOT),
            "python": sys.executable,
        },
    )

    copy_staged_snapshot(stage_root, snapshot_root)
    verify_step = _run_step("stage_verify", [sys.executable, "executable/verify.py"], cwd=snapshot_root)
    install_smoke = _install_smoke(snapshot_root)
    claim_audit = audit_outward_claims(snapshot_root)

    summary: Dict[str, Any] = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "artifact_run_id": run_id,
        "artifact_dir": str(artifact_dir),
        "snapshot_root": str(snapshot_root),
        "comet": {
            "enabled": experiment is not None,
            "experiment_key": experiment_key(experiment),
            "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
            "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
        },
        "stage_verify": verify_step,
        "install_smoke": install_smoke,
        "claim_audit": claim_audit,
        "verdict": (
            "PASS"
            if verify_step["returncode"] == 0 and install_smoke["passed"] and claim_audit["pass"]
            else "FAIL"
        ),
    }
    write_json(artifact_dir / "phase4_cold_start_audit.json", summary)

    log_mapping(experiment, "phase4.cold_start", summary)
    append_run_manifest(
        artifact_dir / "comet_run_manifest.json",
        {
            "name": f"phase4-cold-start-{run_id}",
            "experiment_key": experiment_key(experiment),
            "phase": "04",
            "artifact_dir": str(artifact_dir),
            "verdict": summary["verdict"],
        },
    )
    for name in ["phase4_cold_start_audit.json", "comet_run_manifest.json"]:
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

    print(f"Phase 4 cold-start audit complete. VERDICT={summary['verdict']}")
    return 0 if summary["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
