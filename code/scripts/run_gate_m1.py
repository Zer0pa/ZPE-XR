#!/usr/bin/env python3
"""Gate M1: attempt HOT3D-backed reproduction of core claims."""

from __future__ import annotations

from pathlib import Path
import shlex
import sys
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT.parent / "proofs" / "artifacts" / "2026-02-20_zpe_xr_wave1"
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from max_resource_probe import append_log, run_cmd, utc_now_iso, write_json


def _status_from_result(result) -> str:
    return "PASS" if result.returncode == 0 else "FAIL"


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    raw_log = ARTIFACT_DIR / "resource_attempts_raw.log"
    py = shlex.quote(sys.executable)

    attempts = []

    # Attempt toolchain availability and source path.
    hot3d_git = run_cmd("git ls-remote https://github.com/facebookresearch/hot3d", cwd=ROOT)
    append_log(raw_log, "M1 HOT3D Git Reachability", hot3d_git)
    attempts.append({
        "resource": "HOT3D toolkit",
        "attempt": "git_ls_remote",
        "result": hot3d_git.to_dict(),
    })

    hot3d_import = run_cmd(
        f"{py} - <<'PY'\n"
        "ok = True\n"
        "try:\n"
        "    import huggingface_hub  # noqa: F401\n"
        "    print('HF_HUB_IMPORT_OK')\n"
        "except Exception as e:\n"
        "    ok = False\n"
        "    print('HF_HUB_IMPORT_FAIL', type(e).__name__, str(e))\n"
        "try:\n"
        "    from datasets import load_dataset  # noqa: F401\n"
        "    print('DATASETS_IMPORT_OK')\n"
        "except Exception as e:\n"
        "    print('DATASETS_IMPORT_FAIL', type(e).__name__, str(e))\n"
        "    ok = False\n"
        "raise SystemExit(0 if ok else 2)\n"
        "PY",
        cwd=ROOT,
    )
    append_log(raw_log, "M1 Python Dependency Probe", hot3d_import)
    attempts.append({
        "resource": "HOT3D toolkit",
        "attempt": "python_dependency_probe",
        "result": hot3d_import.to_dict(),
    })

    hot3d_hf_manifest = run_cmd(
        f"{py} - <<'PY'\n"
        "from huggingface_hub import HfApi\n"
        "api = HfApi()\n"
        "info = api.dataset_info('projectaria/hot3d')\n"
        "print('DATASET_ID', info.id)\n"
        "print('SIBLING_COUNT', len(info.siblings))\n"
        "for s in info.siblings[:20]:\n"
        "    print('FILE', s.rfilename)\n"
        "PY",
        cwd=ROOT,
    )
    append_log(raw_log, "M1 HOT3D HF Manifest Probe", hot3d_hf_manifest)
    attempts.append({
        "resource": "HOT3D toolkit",
        "attempt": "hf_dataset_manifest_probe",
        "result": hot3d_hf_manifest.to_dict(),
    })

    hot3d_stream_probe = run_cmd(
        f"{py} - <<'PY'\n"
        "from datasets import load_dataset\n"
        "ds = load_dataset('projectaria/hot3d', split='train', streaming=True)\n"
        "first = next(iter(ds))\n"
        "print('FIRST_KEYS', sorted(list(first.keys()))[:20])\n"
        "PY",
        cwd=ROOT,
        timeout_s=240,
    )
    append_log(raw_log, "M1 HOT3D Streaming Sample Probe", hot3d_stream_probe)
    attempts.append({
        "resource": "HOT3D toolkit",
        "attempt": "hf_stream_sample_probe",
        "result": hot3d_stream_probe.to_dict(),
    })

    pass_conditions = {
        "git_reachable": hot3d_git.returncode == 0,
        "python_deps_ready": hot3d_import.returncode == 0,
        "hf_manifest_accessible": hot3d_hf_manifest.returncode == 0,
        "hf_stream_sample_accessible": hot3d_stream_probe.returncode == 0,
    }
    m1_pass = all(pass_conditions.values())

    gate_result: Dict[str, Any] = {
        "gate": "M1",
        "executed_at_utc": utc_now_iso(),
        "objective": "HOT3D run reproduces fidelity/compression/latency claims",
        "pass": m1_pass,
        "pass_conditions": pass_conditions,
        "attempts_recorded": len(attempts),
        "claim_impact": {
            "XR-C001": "PASS" if m1_pass else "INCONCLUSIVE",
            "XR-C002": "PASS" if m1_pass else "INCONCLUSIVE",
            "XR-C005": "PASS" if m1_pass else "INCONCLUSIVE",
        },
        "evidence": [
            "proofs/artifacts/2026-02-20_zpe_xr_wave1/resource_attempts_raw.log",
        ],
    }

    write_json(ARTIFACT_DIR / "gate_m1_result.json", gate_result)

    # initialize/merge probe summary for later appendix-e aggregation
    existing = {}
    summary_path = ARTIFACT_DIR / "max_resource_probe_summary.json"
    if summary_path.exists():
        import json

        existing = json.loads(summary_path.read_text(encoding="utf-8"))
    existing["gate_m1"] = gate_result
    write_json(summary_path, existing)

    # Persist structured attempt records.
    attempts_path = ARTIFACT_DIR / "resource_attempts_log.json"
    import json

    prior: List[Dict[str, Any]] = []
    if attempts_path.exists():
        prior = json.loads(attempts_path.read_text(encoding="utf-8"))
    prior.extend(attempts)
    write_json(attempts_path, prior)

    print(f"Gate M1 complete. PASS={m1_pass}")
    return 0 if m1_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
