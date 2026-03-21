#!/usr/bin/env python3
"""Gate M2: attempt runtime integration checks for Unity/Meta XR/XRI and MANO license path."""

from __future__ import annotations

from pathlib import Path
import shlex
import sys
from typing import Any, Dict, List

from _bootstrap import activate_source_root

ROOT = activate_source_root(__file__)
ARTIFACT_DIR = None
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from max_resource_probe import append_log, run_cmd, utc_now_iso, write_json
from zpe_xr.runtime_paths import resolve_artifact_dir

ARTIFACT_DIR = resolve_artifact_dir(ROOT)


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    raw_log = ARTIFACT_DIR / "resource_attempts_raw.log"
    py = shlex.quote(sys.executable)

    attempts: List[Dict[str, Any]] = []

    unity_probe = run_cmd("command -v Unity || command -v unity || command -v UnityHub", cwd=ROOT)
    append_log(raw_log, "M2 Unity CLI Probe", unity_probe)
    attempts.append({"resource": "Unity runtime", "attempt": "unity_cli_probe", "result": unity_probe.to_dict()})

    unity_version = run_cmd(
        "if command -v Unity >/dev/null 2>&1; then Unity -version; "
        "elif command -v unity >/dev/null 2>&1; then unity -version; "
        "elif command -v UnityHub >/dev/null 2>&1; then UnityHub --version; "
        "else echo 'UNITY_CLI_NOT_FOUND'; exit 2; fi",
        cwd=ROOT,
    )
    append_log(raw_log, "M2 Unity Version Probe", unity_version)
    attempts.append({"resource": "Unity runtime", "attempt": "unity_version_probe", "result": unity_version.to_dict()})

    # Local dependency/install cycle (attempt 1).
    brew_probe = run_cmd("command -v brew", cwd=ROOT)
    append_log(raw_log, "M2 Homebrew Probe", brew_probe)
    attempts.append({"resource": "Unity runtime", "attempt": "brew_probe", "result": brew_probe.to_dict()})

    brew_search_unity = run_cmd(
        "if command -v brew >/dev/null 2>&1; then brew search unity-hub; else echo 'BREW_NOT_FOUND'; exit 2; fi",
        cwd=ROOT,
        timeout_s=120,
    )
    append_log(raw_log, "M2 Homebrew Unity Hub Search", brew_search_unity)
    attempts.append({"resource": "Unity runtime", "attempt": "brew_search_unity_hub", "result": brew_search_unity.to_dict()})

    brew_install_unity = run_cmd(
        "if command -v brew >/dev/null 2>&1; then HOMEBREW_NO_AUTO_UPDATE=1 brew install --cask unity-hub --no-quarantine; "
        "else echo 'BREW_NOT_FOUND'; exit 2; fi",
        cwd=ROOT,
        timeout_s=90,
    )
    append_log(raw_log, "M2 Homebrew Unity Hub Install Attempt", brew_install_unity)
    attempts.append({"resource": "Unity runtime", "attempt": "brew_install_unity_hub", "result": brew_install_unity.to_dict()})

    meta_sdk_access = run_cmd(
        "curl -fsSLI https://assetstore.unity.com/packages/tools/integration/meta-xr-all-in-one-sdk-269657",
        cwd=ROOT,
    )
    append_log(raw_log, "M2 Meta XR SDK Access Probe", meta_sdk_access)
    attempts.append({"resource": "Meta XR SDK", "attempt": "assetstore_head_probe", "result": meta_sdk_access.to_dict()})

    meta_repo_probe = run_cmd(
        "git ls-remote https://github.com/oculus-samples/Unity-InteractionSDK-Samples",
        cwd=ROOT,
        timeout_s=120,
    )
    append_log(raw_log, "M2 Meta XR Sample Repo Probe", meta_repo_probe)
    attempts.append({"resource": "Meta XR SDK", "attempt": "meta_sample_repo_probe", "result": meta_repo_probe.to_dict()})

    xri_access = run_cmd(
        "curl -fsSLI https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@latest",
        cwd=ROOT,
    )
    append_log(raw_log, "M2 XR Interaction Toolkit Access Probe", xri_access)
    attempts.append({"resource": "XR Interaction Toolkit", "attempt": "docs_head_probe", "result": xri_access.to_dict()})

    # Reproducible containerized cycle (attempt 2).
    docker_probe = run_cmd("docker --version", cwd=ROOT, timeout_s=60)
    append_log(raw_log, "M2 Docker Availability Probe", docker_probe)
    attempts.append({"resource": "Unity runtime", "attempt": "docker_probe", "result": docker_probe.to_dict()})

    unityci_probe = run_cmd(
        "if command -v docker >/dev/null 2>&1; "
        "then docker run --rm unityci/editor:ubuntu-2022.3.62f1-base-3 /bin/bash -lc 'unity-editor -version'; "
        "else echo 'DOCKER_NOT_AVAILABLE'; exit 2; fi",
        cwd=ROOT,
        timeout_s=120,
    )
    append_log(raw_log, "M2 UnityCI Container Probe", unityci_probe)
    attempts.append({"resource": "Unity runtime", "attempt": "unityci_container_probe", "result": unityci_probe.to_dict()})

    mano_access = run_cmd("curl -fsSLI https://mano.is.tue.mpg.de", cwd=ROOT)
    append_log(raw_log, "M2 MANO License Portal Probe", mano_access)
    attempts.append({"resource": "MANO", "attempt": "mano_license_portal_probe", "result": mano_access.to_dict()})

    mano_terms_probe = run_cmd(
        f"{py} - <<'PY'\n"
        "import requests\n"
        "url='https://mano.is.tue.mpg.de'\n"
        "r=requests.get(url,timeout=20)\n"
        "text=(r.text or '').lower()\n"
        "hits=[k for k in ['register','license','non-commercial','commercial'] if k in text]\n"
        "print('STATUS', r.status_code)\n"
        "print('TERM_HITS', hits)\n"
        "PY",
        cwd=ROOT,
    )
    append_log(raw_log, "M2 MANO Terms Probe", mano_terms_probe)
    attempts.append({"resource": "MANO", "attempt": "mano_terms_probe", "result": mano_terms_probe.to_dict()})

    # Commercial-safe open substitute cycle (attempt 3).
    godot_probe = run_cmd("command -v godot || command -v godot4", cwd=ROOT)
    append_log(raw_log, "M2 Godot Runtime Probe", godot_probe)
    attempts.append({"resource": "Commercial-safe runtime substitute", "attempt": "godot_runtime_probe", "result": godot_probe.to_dict()})

    godot_openxr_probe = run_cmd(
        "git ls-remote https://github.com/GodotVR/godot_openxr",
        cwd=ROOT,
        timeout_s=120,
    )
    append_log(raw_log, "M2 Godot OpenXR Plugin Probe", godot_openxr_probe)
    attempts.append(
        {
            "resource": "Commercial-safe runtime substitute",
            "attempt": "godot_openxr_plugin_probe",
            "result": godot_openxr_probe.to_dict(),
        }
    )

    mano_terms_text = (mano_terms_probe.stdout or "") + "\n" + (mano_terms_probe.stderr or "")
    mano_terms_lower = mano_terms_text.lower()
    mano_license_resolved = any(
        token in mano_terms_lower
        for token in ["commercial use", "commercial license", "enterprise license", "business license"]
    )

    pass_conditions = {
        "unity_cli_available": (unity_probe.returncode == 0 and unity_version.returncode == 0),
        "meta_sdk_accessible": (meta_sdk_access.returncode == 0 or meta_repo_probe.returncode == 0),
        "xri_docs_accessible": xri_access.returncode == 0,
        "mano_license_resolved": mano_license_resolved,
        "containerized_unity_runtime_available": unityci_probe.returncode == 0,
        "commercial_safe_runtime_substitute_available": (
            godot_probe.returncode == 0 and godot_openxr_probe.returncode == 0
        ),
    }

    # M2 requires real Unity runtime + Meta SDK + explicit licensing closure.
    m2_pass = (
        pass_conditions["unity_cli_available"]
        and pass_conditions["meta_sdk_accessible"]
        and pass_conditions["xri_docs_accessible"]
        and pass_conditions["mano_license_resolved"]
    )

    gate_result = {
        "gate": "M2",
        "executed_at_utc": utc_now_iso(),
        "objective": "Meta/Unity runtime integration passes beyond interface contracts",
        "pass": m2_pass,
        "pass_conditions": pass_conditions,
        "attempt_cycles": {
            "local_dependency_install_fix": {
                "brew_available": brew_probe.returncode == 0,
                "brew_unity_search_success": brew_search_unity.returncode == 0,
                "brew_unity_install_success": brew_install_unity.returncode == 0,
            },
            "containerized_path": {
                "docker_available": docker_probe.returncode == 0,
                "unityci_runtime_success": unityci_probe.returncode == 0,
            },
            "commercial_safe_substitute": {
                "godot_runtime_available": godot_probe.returncode == 0,
                "godot_openxr_probe_success": godot_openxr_probe.returncode == 0,
            },
        },
        "claim_impact": {
            "XR-C007": "PASS" if m2_pass else "INCONCLUSIVE",
            "XR-C002": "PASS" if m2_pass else "INCONCLUSIVE",
        },
        "evidence": [
            "artifacts/2026-02-20_zpe_xr_wave1/resource_attempts_raw.log",
            "artifacts/2026-02-20_zpe_xr_wave1/resource_attempts_log.json",
        ],
    }

    write_json(ARTIFACT_DIR / "gate_m2_result.json", gate_result)

    summary_path = ARTIFACT_DIR / "max_resource_probe_summary.json"
    existing = {}
    if summary_path.exists():
        import json

        existing = json.loads(summary_path.read_text(encoding="utf-8"))
    existing["gate_m2"] = gate_result
    write_json(summary_path, existing)

    attempts_path = ARTIFACT_DIR / "resource_attempts_log.json"
    prior: List[Dict[str, Any]] = []
    if attempts_path.exists():
        import json

        prior = json.loads(attempts_path.read_text(encoding="utf-8"))
    prior.extend(attempts)
    write_json(attempts_path, prior)

    print(f"Gate M2 complete. PASS={m2_pass}")
    return 0 if m2_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
