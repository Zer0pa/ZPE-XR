"""Comparator triage helpers for Phase 09.1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .external_benchmarks import photon_fusion_measurement, ultraleap_vectorhand_measurement


COMPARATOR_TRIAGE_WARNING = (
    "The exact five public comparator tests are not fully defined in proofs/FINAL_STATUS.md; "
    "this triage ranks only the currently instrumented comparator lanes in the nested repo."
)


@dataclass(frozen=True)
class ComparatorTriageCandidate:
    comparator_id: str
    label: str
    priority: str
    executable_now: bool
    authority_alignment: str
    requires_gpu: bool
    blockers: tuple[str, ...]
    next_step: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "comparator_id": self.comparator_id,
            "label": self.label,
            "priority": self.priority,
            "executable_now": self.executable_now,
            "authority_alignment": self.authority_alignment,
            "requires_gpu": self.requires_gpu,
            "blockers": list(self.blockers),
            "next_step": self.next_step,
        }


def comparator_triage_candidates() -> tuple[ComparatorTriageCandidate, ...]:
    photon = photon_fusion_measurement()
    ultraleap = ultraleap_vectorhand_measurement()
    return (
        ComparatorTriageCandidate(
            comparator_id="modern_float16_delta_plus_zlib_local",
            label="Modern float16+zlib proxy (local)",
            priority="first_target",
            executable_now=True,
            authority_alignment="closest currently instrumented lane to the frozen two-hand stream semantics",
            requires_gpu=False,
            blockers=(
                "still a local proxy rather than the fully surfaced public decision procedure",
                "needs a fresh targeted rerun before any closure claim changes",
            ),
            next_step=(
                "treat this as the first CPU-local closure candidate and pair any rerun with frame-level pathology traces "
                "instead of new public-release rhetoric"
            ),
        ),
        ComparatorTriageCandidate(
            comparator_id=ultraleap.comparator_id,
            label=ultraleap.label,
            priority="secondary_context",
            executable_now=True,
            authority_alignment="useful same-machine incumbent context, but not the sovereign public gate",
            requires_gpu=False,
            blockers=(
                "not the failed modern comparator gate itself",
                "public staged repo still needs truthful mirroring of the stronger root-side lane",
            ),
            next_step="keep as secondary incumbent context after the modern proxy lane is re-attacked",
        ),
        ComparatorTriageCandidate(
            comparator_id=photon.comparator_id,
            label=photon.label,
            priority="defer",
            executable_now=False,
            authority_alignment="semantically narrower than the frozen full-position stream",
            requires_gpu=False,
            blockers=(
                "doc-derived in the nested repo authority surface",
                "shared hand-root side input keeps semantics narrower than the frozen stream",
            ),
            next_step="only revisit after the staged repo mirrors the local proxy lane and preserves the side-input caveat",
        ),
        ComparatorTriageCandidate(
            comparator_id="unity_ngo",
            label="Unity Netcode for GameObjects",
            priority="blocked",
            executable_now=False,
            authority_alignment="market reference only until a runnable hand-sync harness exists",
            requires_gpu=False,
            blockers=(
                "no runnable same-machine hand-sync benchmark exists in this repo",
                "no apples-to-apples byte and latency contract is surfaced locally",
            ),
            next_step="build a local proxy or runtime harness before treating NGO as a numeric comparator",
        ),
        ComparatorTriageCandidate(
            comparator_id="normcore",
            label="Normcore VR/AR",
            priority="blocked",
            executable_now=False,
            authority_alignment="market reference only until a runnable hand-sync harness exists",
            requires_gpu=False,
            blockers=(
                "no runnable same-machine hand-sync benchmark exists in this repo",
                "no apples-to-apples byte and latency contract is surfaced locally",
            ),
            next_step="build a local proxy or runtime harness before treating Normcore as a numeric comparator",
        ),
    )


def build_comparator_triage_report() -> dict[str, Any]:
    candidates = [candidate.to_dict() for candidate in comparator_triage_candidates()]
    first_target = next(
        candidate["comparator_id"]
        for candidate in candidates
        if candidate["priority"] == "first_target"
    )
    return {
        "artifact_class": "planning_scaffold_only",
        "warning": COMPARATOR_TRIAGE_WARNING,
        "first_target": first_target,
        "notes": [
            "This triage is a worklist for currently instrumented lanes, not a replacement for the governing proof boundary.",
            "Blocked rows remain blocked until new runnable comparator surfaces exist inside this repo.",
        ],
        "candidates": candidates,
    }
