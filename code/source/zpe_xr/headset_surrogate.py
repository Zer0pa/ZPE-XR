"""Headset-surrogate dataset taxonomy for Phase 3 planning and tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .embodiment_record import CAPTURE_EVIDENCE_CLASSES


@dataclass(frozen=True)
class HeadsetSurrogateSpec:
    dataset_id: str
    label: str
    evidence_class: str
    authority_status: str
    license_posture: str
    modality: str
    official_url: str
    allowed_phase3_use: str
    forbidden_use: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "label": self.label,
            "evidence_class": self.evidence_class,
            "authority_status": self.authority_status,
            "license_posture": self.license_posture,
            "modality": self.modality,
            "official_url": self.official_url,
            "allowed_phase3_use": self.allowed_phase3_use,
            "forbidden_use": self.forbidden_use,
        }


HEADSET_SURROGATE_SPECS: tuple[HeadsetSurrogateSpec, ...] = (
    HeadsetSurrogateSpec(
        dataset_id="synthetic_openxr_fixture",
        label="Synthetic OpenXR Fixture",
        evidence_class="synthetic_openxr_fixture",
        authority_status="engineering_fixture_only",
        license_posture="internal_generated",
        modality="generated 26-joint-per-hand OpenXR-shaped metadata",
        official_url="repo/code/fixtures/embodiment_record_valid_surrogate_v1.json",
        allowed_phase3_use="Schema, validator, replay, and hash-chain tests.",
        forbidden_use="Native capture, provider latency, or commercial authority claims.",
    ),
    HeadsetSurrogateSpec(
        dataset_id="kine_adl_be_uji",
        label="KINE-ADL BE-UJI",
        evidence_class="green_movement_prior",
        authority_status="movement_prior_after_structural_sample_check",
        license_posture="phase1_green_lane",
        modality="temporal hand/body activity of daily living movement prior",
        official_url="GPD/phases/01-data-authority-lock/01-SUMMARY.md",
        allowed_phase3_use="Movement-form prior policy and surrogate calibration planning.",
        forbidden_use="Native headset capture claims.",
    ),
    HeadsetSurrogateSpec(
        dataset_id="holoassist",
        label="HoloAssist",
        evidence_class="headset_proxy_permissive",
        authority_status="headset_proxy",
        license_posture="CDLA-v2-per-official-data-links",
        modality="egocentric assistance with head, hand, depth, and annotation streams",
        official_url="https://holoassist.github.io/",
        allowed_phase3_use="Schema pressure for head/hand/depth/action metadata.",
        forbidden_use="Native project runtime closure.",
    ),
    HeadsetSurrogateSpec(
        dataset_id="ho_cap",
        label="HO-Cap",
        evidence_class="headset_proxy_permissive",
        authority_status="headset_proxy_with_toolkit_license_risk",
        license_posture="dataset-cc-by-4-toolkit-gpl-risk",
        modality="HoloLens plus RGB-D hand-object capture",
        official_url="https://irvlutd.github.io/HOCap/",
        allowed_phase3_use="Proxy hand/object schema pressure while isolating toolkit code.",
        forbidden_use="Toolkit reuse without GPL review or native project capture claims.",
    ),
    HeadsetSurrogateSpec(
        dataset_id="hot3d",
        label="HOT3D",
        evidence_class="headset_proxy_restricted",
        authority_status="restricted_realism_reference",
        license_posture="custom_separate_agreement",
        modality="Project Aria and Quest 3 egocentric multi-view hand-object data",
        official_url="https://www.projectaria.com/datasets/hot3D",
        allowed_phase3_use="Internal realism and schema-pressure reference if terms allow.",
        forbidden_use="Commercial authority without legal review.",
    ),
    HeadsetSurrogateSpec(
        dataset_id="egodex",
        label="EgoDex",
        evidence_class="headset_proxy_restricted",
        authority_status="restricted_realism_reference",
        license_posture="cc-by-nc-nd",
        modality="Apple Vision Pro dexterous manipulation with paired hand/finger tracking",
        official_url="https://github.com/apple/ml-egodex",
        allowed_phase3_use="Internal realism reference only.",
        forbidden_use="Commercial authority or derivative dataset use.",
    ),
    HeadsetSurrogateSpec(
        dataset_id="openego",
        label="OpenEgo",
        evidence_class="headset_proxy_restricted",
        authority_status="aggregate_terms_unresolved",
        license_posture="constituent_dataset_terms_required",
        modality="standardized egocentric manipulation with hand-pose annotations and action primitives",
        official_url="https://github.com/ahadjawaid/openego",
        allowed_phase3_use="Research reference for standard layouts and action primitives.",
        forbidden_use="Unified commercial authority without constituent license review.",
    ),
    HeadsetSurrogateSpec(
        dataset_id="egoemg",
        label="EgoEMG",
        evidence_class="headset_proxy_restricted",
        authority_status="future_neuromotor_lane",
        license_posture="official_access_lock_required",
        modality="wrist EMG, IMU, egocentric RGB, external RGB-D, and mocap-derived hand motion",
        official_url="arXiv:2605.05712",
        allowed_phase3_use="Future intention/occlusion-prior research direction.",
        forbidden_use="Current Phase 3 authority without official access/license lock.",
    ),
)


def headset_surrogate_specs() -> tuple[HeadsetSurrogateSpec, ...]:
    return HEADSET_SURROGATE_SPECS


def build_headset_surrogate_manifest() -> dict[str, Any]:
    datasets = [spec.to_dict() for spec in headset_surrogate_specs()]
    return {
        "artifact_class": "phase3_surrogate_strategy",
        "native_capture_status": "pending",
        "evidence_classes": list(CAPTURE_EVIDENCE_CLASSES),
        "datasets": datasets,
        "native_capture_gate": (
            "Only native_device_capture may become native_verified; all synthetic, "
            "movement-prior, and headset-proxy lanes remain non-sovereign."
        ),
    }


def classify_surrogate_dataset(dataset_id: str) -> HeadsetSurrogateSpec:
    for spec in headset_surrogate_specs():
        if spec.dataset_id == dataset_id:
            return spec
    raise KeyError(f"Unknown headset surrogate dataset: {dataset_id}")
