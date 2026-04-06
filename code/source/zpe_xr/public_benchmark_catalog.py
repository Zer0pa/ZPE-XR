"""Public hand-dataset benchmark scaffolding for Phase 09.1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contactpose_adapter import CONTACTPOSE_SAMPLE_PAGE


CONTACTPOSE_MIN_FREE_GIB = 5.0
PUBLIC_BENCHMARK_ARTIFACT_CLASS = "planning_scaffold_only"


@dataclass(frozen=True)
class PublicDatasetSpec:
    dataset_id: str
    label: str
    homepage: str
    access: str
    adapter_status: str
    benchmark_status: str
    recommended_cache_path: str
    expected_layout: tuple[str, ...]
    scripts_requiring_data: tuple[str, ...]
    tests_requiring_data: tuple[str, ...]
    disk_notes: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "label": self.label,
            "homepage": self.homepage,
            "access": self.access,
            "adapter_status": self.adapter_status,
            "benchmark_status": self.benchmark_status,
            "recommended_cache_path": self.recommended_cache_path,
            "expected_layout": list(self.expected_layout),
            "scripts_requiring_data": list(self.scripts_requiring_data),
            "tests_requiring_data": list(self.tests_requiring_data),
            "disk_notes": self.disk_notes,
            "notes": self.notes,
            "artifact_class": PUBLIC_BENCHMARK_ARTIFACT_CLASS,
        }


PUBLIC_HAND_DATASET_SPECS: tuple[PublicDatasetSpec, ...] = (
    PublicDatasetSpec(
        dataset_id="contactpose",
        label="ContactPose",
        homepage=CONTACTPOSE_SAMPLE_PAGE,
        access="google_drive_sample",
        adapter_status="runnable",
        benchmark_status="existing_authority_anchor",
        recommended_cache_path="proofs/artifacts/datasets/contactpose/contactpose_sample.zip",
        expected_layout=(
            "ContactPose sample data/grasps.zip",
            "grasps/full28_use/<object>.zip",
            "<object>/annotations.json",
        ),
        scripts_requiring_data=(
            "code/scripts/run_phase4_contactpose_benchmark.py",
            "code/scripts/run_phase5_contactpose_multi_sequence.py",
            "code/scripts/run_phase6_mac_comparator_benchmark.py --attempt-contactpose",
        ),
        tests_requiring_data=(),
        disk_notes=f"Benchmark runners require at least {CONTACTPOSE_MIN_FREE_GIB:.1f} GiB free before fetching.",
        notes="The only dataset lane currently runnable in the nested repo. The exported scaffold points at the established Phase 4 and Phase 5 authority anchors.",
    ),
    PublicDatasetSpec(
        dataset_id="interhand26m",
        label="InterHand2.6M",
        homepage="https://mks0601.github.io/InterHand2.6M/",
        access="official_project_page",
        adapter_status="planned",
        benchmark_status="not_run",
        recommended_cache_path="proofs/artifacts/datasets/interhand26m/InterHand2.6M/",
        expected_layout=(
            "annotations/",
            "images/",
        ),
        scripts_requiring_data=(),
        tests_requiring_data=(),
        disk_notes="Large multi-subject corpus; confirm size and splits at the official project page before download.",
        notes="Useful multi-hand interaction candidate. No adapter or measured benchmark exists in this repo yet.",
    ),
    PublicDatasetSpec(
        dataset_id="freihand",
        label="FreiHAND",
        homepage="https://lmb.informatik.uni-freiburg.de/projects/freihand/",
        access="official_dataset_download",
        adapter_status="planned",
        benchmark_status="not_run",
        recommended_cache_path="proofs/artifacts/datasets/freihand/FreiHAND_pub_v2/",
        expected_layout=(
            "training/",
            "evaluation/",
        ),
        scripts_requiring_data=(),
        tests_requiring_data=(),
        disk_notes="Check current dataset package and annotation split on the official download page before caching.",
        notes="Single-hand articulation benchmark candidate. Repo support is planning-only today.",
    ),
    PublicDatasetSpec(
        dataset_id="ho3d",
        label="HO-3D",
        homepage="https://github.com/shreyashampali/ho3d",
        access="project_repo_and_docs",
        adapter_status="planned",
        benchmark_status="not_run",
        recommended_cache_path="proofs/artifacts/datasets/ho3d/HO3D_v3/",
        expected_layout=(
            "train/",
            "evaluation/",
        ),
        scripts_requiring_data=(),
        tests_requiring_data=(),
        disk_notes="Hand-object sequences are substantially larger than ContactPose; inspect the project docs before fetching.",
        notes="Useful manipulation-context benchmark candidate. No adapter or measured benchmark exists in this repo yet.",
    ),
    PublicDatasetSpec(
        dataset_id="dexycb",
        label="DexYCB",
        homepage="https://dex-ycb.github.io/",
        access="official_site_google_drive",
        adapter_status="planned",
        benchmark_status="not_run",
        recommended_cache_path="proofs/artifacts/datasets/dexycb/",
        expected_layout=(
            "20200709-subject-01/",
            "calibration/",
            "models/",
        ),
        scripts_requiring_data=(),
        tests_requiring_data=(),
        disk_notes="Official site offers a 119G combined archive or per-subject archives; do not fetch casually on a tight disk budget.",
        notes="Dexterous grasping benchmark candidate with official toolkit support. Repo support is planning-only today.",
    ),
    PublicDatasetSpec(
        dataset_id="oakink",
        label="OakInk",
        homepage="https://oakink.net/",
        access="huggingface_plus_google_form",
        adapter_status="planned",
        benchmark_status="not_run",
        recommended_cache_path="proofs/artifacts/datasets/oakink/zipped/",
        expected_layout=(
            "OakBase.zip",
            "image/anno_v2.1.zip",
            "shape/oakink_shape_v2.zip",
        ),
        scripts_requiring_data=(),
        tests_requiring_data=(),
        disk_notes="Official guidance requires zipped dataset files plus an annotation download gate; confirm storage before fetch.",
        notes="Intent-aware hand-object benchmark candidate. Repo support is planning-only today.",
    ),
)


def public_hand_dataset_specs() -> tuple[PublicDatasetSpec, ...]:
    return PUBLIC_HAND_DATASET_SPECS


def build_dataset_status(spec: PublicDatasetSpec) -> dict[str, Any]:
    payload = spec.to_dict()
    payload["status_file"] = f"{spec.dataset_id}_status.json"
    if spec.dataset_id == "contactpose":
        payload["current_authority_anchor"] = (
            "proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/"
            "phase5_multi_sequence_benchmark.json"
        )
        payload["scaffold_status"] = "baseline_available"
    else:
        payload["current_authority_anchor"] = None
        payload["scaffold_status"] = "not_run"
    return payload


def build_public_benchmark_manifest() -> dict[str, Any]:
    datasets = [build_dataset_status(spec) for spec in public_hand_dataset_specs()]
    return {
        "artifact_class": PUBLIC_BENCHMARK_ARTIFACT_CLASS,
        "recommended_cache_root": "proofs/artifacts/datasets",
        "notes": [
            "Only ContactPose is currently runnable in the nested repo.",
            "The additional datasets are scaffold surfaces only and carry no measured benchmark claims.",
            "Use DATA_SETUP.md before attempting any large dataset fetch.",
        ],
        "datasets": datasets,
    }
