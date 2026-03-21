#!/usr/bin/env python3
"""Run the Phase 3 packaging and wedge-proof workflow with Comet logging."""

from __future__ import annotations

from datetime import datetime, UTC
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from time import perf_counter
from typing import Any, Dict, List

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
from zpe_xr.package_surface import (
    build_package_surface,
    build_wedge_claims,
    render_package_surface_markdown,
    render_staged_files,
    render_wedge_claims_markdown,
)
from zpe_xr.runtime_paths import artifact_run_id, resolve_artifact_dir, staged_repo_root


def _run_step(name: str, command: List[str], *, cwd: Path, env: Dict[str, str]) -> Dict[str, Any]:
    started = datetime.now(UTC).isoformat()
    t0 = perf_counter()
    proc = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, env=env)
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


def _call_step(name: str, func) -> Dict[str, Any]:
    started = datetime.now(UTC).isoformat()
    t0 = perf_counter()
    try:
        payload = func()
        return {
            "name": name,
            "command": [name],
            "returncode": 0,
            "duration_s": perf_counter() - t0,
            "started_at_utc": started,
            "ended_at_utc": datetime.now(UTC).isoformat(),
            "stdout": json.dumps(payload, indent=2, sort_keys=True)[-12000:],
            "stderr": "",
            "result": payload,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "name": name,
            "command": [name],
            "returncode": 1,
            "duration_s": perf_counter() - t0,
            "started_at_utc": started,
            "ended_at_utc": datetime.now(UTC).isoformat(),
            "stdout": "",
            "stderr": str(exc),
        }


def _parse_pytest_summary(stdout: str) -> str:
    match = re.search(r"(\d+) passed", stdout)
    if match:
        return f"{match.group(1)} passed"
    return "summary unavailable"


def _collect_build_artifacts(dist_dir: Path) -> List[Dict[str, Any]]:
    artifacts = []
    for path in sorted(dist_dir.glob("*")):
        if path.is_file():
            artifacts.append({"name": path.name, "bytes": path.stat().st_size})
    return artifacts


def _build_distributions(dist_dir: Path) -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="zpe_xr_phase3_build_") as tmpdir:
        temp_root = Path(tmpdir)
        venv_dir = temp_root / "venv"
        python_bin = venv_dir / "bin" / "python"
        pip_bin = venv_dir / "bin" / "pip"

        commands = [
            [sys.executable, "-m", "venv", str(venv_dir)],
            [str(pip_bin), "install", "--upgrade", "pip"],
            [str(pip_bin), "install", "build>=1.2,<2"],
            [str(python_bin), "-m", "build", "--sdist", "--wheel", "--outdir", str(dist_dir)],
        ]

        stdout_blobs: List[str] = []
        for command in commands:
            proc = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True, check=False)
            stdout_blobs.append(proc.stdout.strip())
            if proc.returncode != 0:
                raise RuntimeError(f"build step failed for command: {' '.join(command)}\n{proc.stderr}")

        return {
            "passed": True,
            "artifacts": _collect_build_artifacts(dist_dir),
            "commands": commands,
        }


def _install_smoke_check(dist_dir: Path) -> Dict[str, Any]:
    wheel = next(iter(sorted(dist_dir.glob("zpe_xr-*.whl"))), None)
    if wheel is None:
        raise RuntimeError("built wheel not found in dist directory")

    with tempfile.TemporaryDirectory(prefix="zpe_xr_phase3_smoke_") as tmpdir:
        temp_root = Path(tmpdir)
        venv_dir = temp_root / "venv"
        python_bin = venv_dir / "bin" / "python"
        pip_bin = venv_dir / "bin" / "pip"

        commands = [
            [sys.executable, "-m", "venv", str(venv_dir)],
            [str(pip_bin), "install", "--upgrade", "pip"],
            [str(pip_bin), "install", str(wheel)],
            [
                str(python_bin),
                "-c",
                (
                    "import json, zpe_xr; "
                    "print(json.dumps({'package_import': True, 'version': zpe_xr.__version__}, sort_keys=True))"
                ),
            ],
        ]

        stdout_blobs: List[str] = []
        for command in commands:
            proc = subprocess.run(command, capture_output=True, text=True, check=False)
            stdout_blobs.append(proc.stdout.strip())
            if proc.returncode != 0:
                raise RuntimeError(f"install smoke failed for command: {' '.join(command)}\n{proc.stderr}")

        payload = json.loads(stdout_blobs[-1])
        return {
            "passed": True,
            "wheel": wheel.name,
            "version": payload["version"],
            "commands": commands,
        }


def _render_stage_surface(stage_root: Path, surface: Dict[str, Any], claims: Dict[str, Any]) -> Dict[str, Any]:
    rendered = render_staged_files(surface, claims)
    written: List[str] = []
    for rel_path, content in rendered.items():
        target = stage_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content.rstrip() + "\n", encoding="utf-8")
        written.append(rel_path)
    return {"written_files": written}


def _write_markdown(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    run_id = artifact_run_id()
    artifact_dir = resolve_artifact_dir(ROOT)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    dist_dir = artifact_dir / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env.setdefault("PYTHONHASHSEED", "0")
    env["ZPE_XR_ARTIFACT_RUN_ID"] = run_id
    existing_pythonpath = env.get("PYTHONPATH", "").strip()
    env["PYTHONPATH"] = str(SRC) if not existing_pythonpath else f"{str(SRC)}:{existing_pythonpath}"

    experiment = create_experiment(
        name=f"phase3-packaging-{run_id}",
        tags=["phase-3", "packaging", "wedge-proof"],
        parameters={
            "artifact_run_id": run_id,
            "cwd": str(ROOT),
            "git_head": git_head(ROOT),
            "python": sys.executable,
        },
    )

    steps: List[Dict[str, Any]] = []

    command_steps = [
        ("pytest", [sys.executable, "-m", "pytest", "-q"]),
        ("sync_staged_repo", [sys.executable, "scripts/sync_staged_repo.py", "--run-id", run_id]),
    ]

    pytest_result = _run_step(command_steps[0][0], command_steps[0][1], cwd=ROOT, env=env)
    steps.append(pytest_result)
    log_mapping(experiment, "steps.pytest", pytest_result)

    build_step = _call_step("build", lambda: _build_distributions(dist_dir))
    steps.append(build_step)
    log_mapping(experiment, "steps.build", build_step)

    for name, command in command_steps[1:]:
        result = _run_step(name, command, cwd=ROOT, env=env)
        steps.append(result)
        log_mapping(experiment, f"steps.{name}", result)

    install_smoke_step = _call_step("install_smoke", lambda: _install_smoke_check(dist_dir))
    steps.append(install_smoke_step)
    log_mapping(experiment, "steps.install_smoke", install_smoke_step)

    build_artifacts = _collect_build_artifacts(dist_dir)
    build_summary = build_step.get("result", {"passed": False, "artifacts": build_artifacts})
    pytest_step = next(step for step in steps if step["name"] == "pytest")
    test_summary = {
        "passed": pytest_step["returncode"] == 0,
        "summary": _parse_pytest_summary(pytest_step["stdout"]),
    }
    install_smoke = install_smoke_step.get("result", {"passed": False})

    stage_root = staged_repo_root(ROOT)
    surface = build_package_surface(
        ROOT,
        build_summary=build_summary,
        install_smoke=install_smoke,
        test_summary=test_summary,
        stage_verify={"passed": False},
    )
    claims = build_wedge_claims(ROOT)

    render_step = _call_step("render_staged_surface", lambda: _render_stage_surface(stage_root, surface, claims))
    steps.append(render_step)
    log_mapping(experiment, "steps.render_staged_surface", render_step)
    if "result" in render_step:
        write_json(artifact_dir / "phase3_staged_surface_files.json", render_step["result"])

    stage_verify_step = _run_step(
        "stage_verify",
        [sys.executable, "executable/verify.py"],
        cwd=stage_root,
        env=env,
    )
    steps.append(stage_verify_step)
    log_mapping(experiment, "steps.stage_verify", stage_verify_step)

    final_stage_verify = {
        "passed": stage_verify_step["returncode"] == 0,
        "summary": "stage verify passed" if stage_verify_step["returncode"] == 0 else "stage verify failed",
    }
    final_surface = build_package_surface(
        ROOT,
        build_summary=build_summary,
        install_smoke=install_smoke,
        test_summary=test_summary,
        stage_verify=final_stage_verify,
    )
    rendered_claims = build_wedge_claims(ROOT)

    write_json(artifact_dir / "phase3_step_logs.json", {"steps": steps})
    write_json(artifact_dir / "phase3_package_surface.json", final_surface)
    write_json(artifact_dir / "phase3_wedge_claims.json", rendered_claims)
    _write_markdown(artifact_dir / "phase3_package_surface.md", render_package_surface_markdown(final_surface))
    _write_markdown(artifact_dir / "phase3_wedge_claims.md", render_wedge_claims_markdown(rendered_claims))

    summary: Dict[str, Any] = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "artifact_run_id": run_id,
        "artifact_dir": str(artifact_dir),
        "all_steps_passed": all(step["returncode"] == 0 for step in steps),
        "step_status": {step["name"]: step["returncode"] for step in steps},
        "comet": {
            "enabled": experiment is not None,
            "experiment_key": experiment_key(experiment),
            "workspace": os.getenv("COMET_WORKSPACE", "zer0pa"),
            "project": os.getenv("COMET_PROJECT_NAME", "zpe-xr"),
        },
        "package_surface": final_surface,
        "wedge_claims_summary": {
            "allowed": len(rendered_claims["allowed_claims"]),
            "open": len(rendered_claims["open_claims"]),
            "forbidden": len(rendered_claims["forbidden_claims"]),
        },
    }
    write_json(artifact_dir / "phase3_execution_summary.json", summary)

    append_run_manifest(
        artifact_dir / "comet_run_manifest.json",
        {
            "name": f"phase3-packaging-{run_id}",
            "experiment_key": experiment_key(experiment),
            "phase": "03",
            "artifact_dir": str(artifact_dir),
            "all_steps_passed": summary["all_steps_passed"],
        },
    )

    for name in [
        "phase3_step_logs.json",
        "phase3_execution_summary.json",
        "phase3_package_surface.json",
        "phase3_package_surface.md",
        "phase3_wedge_claims.json",
        "phase3_wedge_claims.md",
        "phase3_staged_surface_files.json",
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

    print(f"Phase 3 packaging workflow complete. PASS={summary['all_steps_passed']}")
    return 0 if summary["all_steps_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
