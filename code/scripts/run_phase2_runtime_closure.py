#!/usr/bin/env python3
"""Build a bounded Phase 2 runtime-closure matrix."""

from __future__ import annotations

from datetime import datetime, UTC
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, Iterable
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_xr.io_utils import write_json
from zpe_xr.runtime_paths import resolve_artifact_dir

ARTIFACT_DIR = resolve_artifact_dir(ROOT)

META_README_URL = (
    "https://raw.githubusercontent.com/oculus-samples/Unity-InteractionSDK-Samples/main/README.md"
)
META_PROJECT_VERSION_URL = (
    "https://raw.githubusercontent.com/oculus-samples/Unity-InteractionSDK-Samples/main/ProjectSettings/ProjectVersion.txt"
)
META_MANIFEST_URL = (
    "https://raw.githubusercontent.com/oculus-samples/Unity-InteractionSDK-Samples/main/Packages/manifest.json"
)


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    readme = _fetch_text(META_README_URL)
    project_version = _fetch_text(META_PROJECT_VERSION_URL)
    manifest = json.loads(_fetch_text(META_MANIFEST_URL))
    unity_requirement = _extract_unity_requirement(readme)
    local_runtime = _local_runtime_probe()

    blockers = []
    if not local_runtime["unity_cli_available"]:
        blockers.append("UNITY_EDITOR_NOT_INSTALLED")
    if not local_runtime["disk_headroom_meets_editor_budget"]:
        blockers.append("DISK_HEADROOM_BELOW_PRACTICAL_UNITY_EDITOR_BUDGET")
    if not local_runtime["quest_or_vision_device_trace_available"]:
        blockers.append("REAL_DEVICE_TRACE_MISSING")
    if not local_runtime["mano_license_resolved"]:
        blockers.append("MANO_LICENSE_UNRESOLVED")

    output = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "gate": "P2-RUNTIME",
        "official_meta_surface": {
            "sample_repo_readme": META_README_URL,
            "sample_project_version_file": META_PROJECT_VERSION_URL,
            "sample_manifest": META_MANIFEST_URL,
            "unity_requirement": unity_requirement,
            "sample_project_version": project_version.strip(),
            "package_dependencies": {
                key: value
                for key, value in manifest.get("dependencies", {}).items()
                if key.startswith("com.meta") or key.startswith("com.unity.xr")
            },
        },
        "local_runtime_probe": local_runtime,
        "blockers": blockers,
        "xr_c007_status_candidate": "PAUSED_EXTERNAL" if blockers else "READY_FOR_DEVICE_EXECUTION",
        "verdict": (
            "Runtime closure remains blocked locally, but the blocker set is now concrete: editor/device/license headroom, not a vague probe failure."
        ),
    }
    write_json(ARTIFACT_DIR / "phase2_runtime_probe_matrix.json", output)

    lines = [
        "# Phase 2 Runtime Closure Matrix",
        "",
        f"- Generated: `{output['generated_at_utc']}`",
        f"- Official Meta sample requirement: `{unity_requirement}`",
        f"- Official sample project version: `{project_version.strip()}`",
        "",
        "## Local Read",
        f"- Unity CLI available: `{local_runtime['unity_cli_available']}`",
        f"- Unity Hub detected: `{local_runtime['unity_hub_detected']}`",
        f"- Disk headroom GiB: `{local_runtime['disk_headroom_gib']:.2f}`",
        f"- Disk headroom meets practical editor budget: `{local_runtime['disk_headroom_meets_editor_budget']}`",
        f"- Device trace available: `{local_runtime['quest_or_vision_device_trace_available']}`",
        f"- MANO license resolved: `{local_runtime['mano_license_resolved']}`",
        "",
        "## Blockers",
    ]
    if blockers:
        for blocker in blockers:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- `NONE`")
    (ARTIFACT_DIR / "phase2_runtime_probe_matrix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Phase 2 runtime closure matrix complete.")
    return 0


def _fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="ignore")


def _extract_unity_requirement(readme: str) -> str:
    match = re.search(r"Unity version \*\*(.+?)\*\*", readme)
    if match:
        return match.group(1)
    return "Unity 2022.3 LTS or above (unparsed fallback)"


def _local_runtime_probe() -> Dict[str, Any]:
    total, used, free = shutil.disk_usage(ROOT)
    free_gib = free / (1024**3)
    unity_cli_path = _first_existing_command(["Unity", "unity", "UnityHub"])
    unity_hub_detected = any(
        Path(path).exists()
        for path in [
            "/Applications/Unity Hub.app",
            "/Applications/Unity/Hub/Unity Hub.app",
            "/Applications/Unity Hub.app/Contents/MacOS/Unity Hub",
        ]
    ) or unity_cli_path == "UnityHub"

    installed_editors = []
    editors_root = Path("/Applications/Unity/Hub/Editor")
    if editors_root.exists():
        installed_editors = sorted(path.name for path in editors_root.iterdir() if path.is_dir())

    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "unity_cli_available": bool(unity_cli_path),
        "unity_cli_path": unity_cli_path,
        "unity_hub_detected": unity_hub_detected,
        "installed_editor_versions": installed_editors,
        "disk_headroom_gib": free_gib,
        "disk_headroom_meets_editor_budget": free_gib >= 20.0,
        "quest_or_vision_device_trace_available": _device_trace_present(),
        "mano_license_resolved": False,
    }


def _device_trace_present() -> bool:
    trace_candidates: Iterable[Path] = [
        ROOT / "data" / "device_traces",
        ROOT / "fixtures" / "device_traces",
        ROOT / "artifacts" / "device_traces",
    ]
    return any(path.exists() and any(path.iterdir()) for path in trace_candidates if path.exists())


def _first_existing_command(names: list[str]) -> str | None:
    for name in names:
        proc = subprocess.run(
            ["bash", "-lc", f"command -v {name}"],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            env=dict(os.environ),
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    return None


if __name__ == "__main__":
    raise SystemExit(main())

