#!/usr/bin/env python3
"""Probe the outward-safe external-corpus path for Phase 2."""

from __future__ import annotations

from datetime import datetime, UTC
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any, Dict, List
from urllib.request import Request, urlopen

from _bootstrap import activate_source_root

ROOT = activate_source_root(__file__)

from zpe_xr.contactpose_adapter import CONTACTPOSE_SAMPLE_PAGE
from zpe_xr.io_utils import write_json
from zpe_xr.runtime_paths import resolve_artifact_dir

ARTIFACT_DIR = resolve_artifact_dir(ROOT)

CONTACTPOSE_README_URL = "https://raw.githubusercontent.com/facebookresearch/ContactPose/main/README.md"
CONTACTPOSE_DOC_URL = "https://raw.githubusercontent.com/facebookresearch/ContactPose/main/docs/doc.md"
CONTACTPOSE_DATASET_URL = "https://raw.githubusercontent.com/facebookresearch/ContactPose/main/utilities/dataset.py"
EGO4D_HO_README_URL = "https://raw.githubusercontent.com/EGO4D/hands-and-objects/main/README.md"


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    contactpose_readme = _fetch_text(CONTACTPOSE_README_URL)
    contactpose_docs = _fetch_text(CONTACTPOSE_DOC_URL)
    contactpose_dataset = _fetch_text(CONTACTPOSE_DATASET_URL)
    ego4d_readme = _fetch_text(EGO4D_HO_README_URL)
    sample_page = _fetch_text(CONTACTPOSE_SAMPLE_PAGE)
    free_gib = shutil.disk_usage(ROOT).free / (1024**3)

    contactpose = {
        "status": "READY_FOR_LOCAL_INTAKE",
        "license": _extract_contactpose_license(contactpose_readme),
        "sample_data_reachable": "ContactPose sample data.zip" in sample_page,
        "sample_data_size": _extract_size(sample_page),
        "sequence_support": _supports_contactpose_sequences(
            contactpose_readme,
            contactpose_docs,
            contactpose_dataset,
        ),
        "joint_topology": "21-joint OpenPose hand format",
        "adapter_required": "21-to-26 joint topology bridge for the frozen ZPE-XR lane",
        "source_urls": [
            CONTACTPOSE_README_URL,
            CONTACTPOSE_DOC_URL,
            CONTACTPOSE_DATASET_URL,
            CONTACTPOSE_SAMPLE_PAGE,
        ],
    }

    ego4d = {
        "status": "CONTEXT_ONLY_FALLBACK",
        "license": _extract_ego4d_license(ego4d_readme),
        "direct_3d_hand_pose_benchmark": False,
        "reason": "Official Hands & Objects benchmark is interaction/object-state oriented, not a direct 3D hand-pose transport benchmark.",
        "source_urls": [EGO4D_HO_README_URL],
    }

    exact_prd_gap = {
        "resource_id": "egocentric_100k_exact_prd_surface",
        "status": "UNRESOLVED",
        "reason": "The exact PRD-named egocentric corpus was not concretely locatable as an official directly executable 3D hand-pose source during this phase.",
    }

    output: Dict[str, Any] = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "gate": "P2-CORPUS",
        "disk_headroom_gib": free_gib,
        "contactpose": contactpose,
        "ego4d_hands_objects": ego4d,
        "exact_prd_gap": exact_prd_gap,
        "verdict": (
            "ContactPose is the strongest outward-safe freely reachable corpus lane available now; the exact PRD egocentric corpus remains unresolved, and Ego4D Hands & Objects is not a direct pose-equivalent benchmark."
        ),
    }
    write_json(ARTIFACT_DIR / "phase2_outward_corpus_probe.json", output)

    lines = [
        "# Phase 2 Outward-Safe Corpus Probe",
        "",
        f"- Generated: `{output['generated_at_utc']}`",
        f"- Disk headroom GiB: `{free_gib:.2f}`",
        "",
        "## ContactPose",
        f"- Status: `{contactpose['status']}`",
        f"- License: `{contactpose['license']}`",
        f"- Sample data reachable: `{contactpose['sample_data_reachable']}`",
        f"- Sample data size: `{contactpose['sample_data_size']}`",
        f"- Joint topology: `{contactpose['joint_topology']}`",
        "",
        "## Ego4D Hands & Objects",
        f"- Status: `{ego4d['status']}`",
        f"- License: `{ego4d['license']}`",
        f"- Direct 3D hand-pose benchmark: `{ego4d['direct_3d_hand_pose_benchmark']}`",
        f"- Reason: {ego4d['reason']}",
        "",
        "## Exact PRD Gap",
        f"- `{exact_prd_gap['resource_id']}`: {exact_prd_gap['reason']}",
        "",
        "## Verdict",
        f"- {output['verdict']}",
    ]
    (ARTIFACT_DIR / "phase2_outward_corpus_probe.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Phase 2 outward-safe corpus probe complete.")
    return 0


def _fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="ignore")


def _extract_size(text: str) -> str:
    match = re.search(r"ContactPose sample data\.zip</a> \(([^)]+)\)", text)
    return match.group(1) if match else "unknown"


def _extract_contactpose_license(readme: str) -> str:
    match = re.search(r"All other data:\s*\[([^\]]+)\]", readme)
    return match.group(1) if match else "unparsed"


def _supports_contactpose_sequences(readme: str, docs: str, dataset_source: str) -> bool:
    readme_lower = readme.lower()
    docs_lower = docs.lower()
    dataset_lower = dataset_source.lower()
    return all(
        marker in blob
        for marker, blob in [
            ("images, poses, and calibration data", docs_lower),
            ("number of rgb-d time frames", dataset_lower),
            ("ann['frames']", dataset_source),
            ("_n_frames", dataset_source),
            ("rgb-d images", docs_lower),
            ("contactpose dataset api", docs_lower),
            ("download grasps", docs_lower),
            ("download rgb-d images", docs_lower),
            ("mit license", readme_lower),
        ]
    )


def _extract_ego4d_license(readme: str) -> str:
    match = re.search(r"### License\s+Ego4D is released under the ([^.]+)\.", readme)
    return match.group(1) if match else "unparsed"


if __name__ == "__main__":
    raise SystemExit(main())
