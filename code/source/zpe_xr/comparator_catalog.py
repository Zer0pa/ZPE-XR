"""Shared comparator-lane metadata for Phase 6 and triage surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


MODERN_PROXY_COMPARATOR_ID = "modern_float16_delta_plus_zlib_local"
MODERN_PROXY_LABEL = "Modern float16+zlib proxy (local)"


@dataclass(frozen=True)
class MarketReferenceLane:
    comparator_id: str
    label: str
    source_reference: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "comparator_id": self.comparator_id,
            "label": self.label,
            "evidence_class": "market_reference_only",
            "source_reference": self.source_reference,
            "notes": self.notes,
        }


UNITY_NGO_REFERENCE = MarketReferenceLane(
    comparator_id="unity_ngo",
    label="Unity Netcode for GameObjects",
    source_reference="https://docs.unity3d.com/kr/6000.0/Manual/com.unity.netcode.gameobjects.html",
    notes="Mainstream networking surface, but no official apples-to-apples XR hand-sync transport or latency row was found.",
)

NORMCORE_REFERENCE = MarketReferenceLane(
    comparator_id="normcore",
    label="Normcore VR/AR",
    source_reference="https://normcore.io/solutions/vr-ar",
    notes="Major VR/AR multiplayer product, but no official hand-sync byte or latency table was found.",
)


def market_reference_only_rows() -> tuple[dict[str, Any], ...]:
    return (
        UNITY_NGO_REFERENCE.to_dict(),
        NORMCORE_REFERENCE.to_dict(),
    )
