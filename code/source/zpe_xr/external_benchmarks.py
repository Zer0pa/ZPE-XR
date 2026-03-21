"""Phase 2 incumbent benchmark helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .constants import FPS


PHOTON_FUSION_FULL_QUATERNION_BYTES_PER_HAND = 386
PHOTON_FUSION_COMPRESSED_BYTES_PER_HAND = 19
ULTRALEAP_VECTORHAND_BYTES_PER_HAND = 86


@dataclass(frozen=True)
class ComparatorMeasurement:
    comparator_id: str
    label: str
    bytes_per_frame: float
    semantics: str
    fairness_class: str
    source_reference: str
    notes: str

    def to_dict(self, *, fps: int = FPS, remote_players: int = 3) -> Dict[str, object]:
        return {
            "comparator_id": self.comparator_id,
            "label": self.label,
            "bytes_per_frame": self.bytes_per_frame,
            "kb_per_s_single_remote": bytes_per_frame_to_kbytes_per_second(self.bytes_per_frame, fps=fps, remote_players=1),
            "kb_per_s_modeled_4_player_session": bytes_per_frame_to_kbytes_per_second(
                self.bytes_per_frame,
                fps=fps,
                remote_players=remote_players,
            ),
            "semantics": self.semantics,
            "fairness_class": self.fairness_class,
            "source_reference": self.source_reference,
            "notes": self.notes,
        }


def bytes_per_frame_to_kbytes_per_second(bytes_per_frame: float, *, fps: int = FPS, remote_players: int = 1) -> float:
    return (bytes_per_frame * fps * remote_players) / 1024.0


def photon_fusion_measurement(*, hands: int = 2) -> ComparatorMeasurement:
    return ComparatorMeasurement(
        comparator_id="photon_fusion_xr_hands_doc",
        label="Photon Fusion XR Hands (doc-derived compressed rotations)",
        bytes_per_frame=float(PHOTON_FUSION_COMPRESSED_BYTES_PER_HAND * hands),
        semantics="Hand-bone rotations only; shared local skeleton reconstructs visual hand state.",
        fairness_class="narrower_semantics_than_frozen_v1",
        source_reference="https://doc.photonengine.com/fusion/current/industries-samples/industries-addons/fusion-industries-addons-xrhandssynchronization",
        notes=(
            "Official Photon documentation states that one hand full bone rotations compress to 19 bytes "
            "instead of 386 bytes for full quaternion transfer."
        ),
    )


def photon_fusion_full_quaternion_measurement(*, hands: int = 2) -> ComparatorMeasurement:
    return ComparatorMeasurement(
        comparator_id="photon_fusion_xr_hands_full_quaternion_doc",
        label="Photon Fusion XR Hands (doc-derived full quaternion transfer)",
        bytes_per_frame=float(PHOTON_FUSION_FULL_QUATERNION_BYTES_PER_HAND * hands),
        semantics="Hand-bone rotations only without Photon compression.",
        fairness_class="narrower_semantics_than_frozen_v1",
        source_reference="https://doc.photonengine.com/fusion/current/industries-samples/industries-addons/fusion-industries-addons-xrhandssynchronization",
        notes="Official Photon documentation states that one hand full bone rotations occupy 386 bytes.",
    )


def ultraleap_vectorhand_measurement(*, hands: int = 2) -> ComparatorMeasurement:
    return ComparatorMeasurement(
        comparator_id="ultraleap_vectorhand_open_source",
        label="Ultraleap VectorHand compressed encoding",
        bytes_per_frame=float(ULTRALEAP_VECTORHAND_BYTES_PER_HAND * hands),
        semantics="Palm pose plus 25 hand-local joint positions per hand in an 86-byte compressed representation.",
        fairness_class="close_transport_semantics",
        source_reference="https://github.com/ultraleap/UnityPlugin/blob/main/Packages/Tracking/Core/Runtime/Scripts/Encoding/VectorHand.cs",
        notes="Open-source Ultraleap VectorHand encoding fixes NUM_BYTES=86 per hand.",
    )

