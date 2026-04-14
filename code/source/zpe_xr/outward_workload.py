"""Outward-safe workload helpers for Phase 4."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Sequence
import zipfile

from .codec import XRCodec
from .contactpose_adapter import (
    ContactPoseSequenceMeta,
    annotation_candidates_from_zip,
    build_zpe_frames_from_annotation,
    download_contactpose_sample_zip,
    read_annotation_from_zip,
)
from .io_utils import sha256_of_file
from .metrics import packet_hash_digest
from .network import encode_sequence
from .pipeline import evaluate_gate_b, evaluate_packet_loss_resilience


CONTACTPOSE_SAMPLE_FILENAME = "contactpose_sample.zip"
TARGET_PACKET_LOSS_CASE = {
    "loss_rate": 0.10,
    "jitter_probability": 0.20,
    "max_delay_frames": 1,
    "seed": 4409,
}


def ensure_contactpose_sample(destination: Path, *, search_root: Path | None = None) -> Path:
    destination = destination.resolve()
    if _is_valid_contactpose_archive(destination):
        return destination
    if destination.exists():
        destination.unlink()

    reusable_search_root = search_root if search_root is not None else destination.parent.parent.parent
    reusable = find_reusable_contactpose_sample(reusable_search_root, exclude=destination)
    if reusable is not None:
        return reusable

    return download_contactpose_sample_zip(destination)


def find_reusable_contactpose_sample(search_root: Path, *, exclude: Path | None = None) -> Path | None:
    search_root = search_root.resolve()
    excluded = exclude.resolve() if exclude is not None else None
    candidates = sorted(
        search_root.glob(f"**/{CONTACTPOSE_SAMPLE_FILENAME}"),
        key=lambda path: (path.stat().st_mtime, path.stat().st_size),
        reverse=True,
    )
    for candidate in candidates:
        resolved = candidate.resolve()
        if excluded is not None and resolved == excluded:
            continue
        if _is_valid_contactpose_archive(resolved):
            return resolved
    return None


def _is_valid_contactpose_archive(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0 and zipfile.is_zipfile(path)


def select_best_contactpose_candidate(
    candidates: Sequence[ContactPoseSequenceMeta],
) -> ContactPoseSequenceMeta:
    if not candidates:
        raise ValueError("no ContactPose candidates available")

    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.frame_count,
            len(candidate.valid_hands),
            candidate.object_name,
            candidate.archive_member,
        ),
        reverse=True,
    )[0]


def select_contactpose_candidates_for_objects(
    candidates: Sequence[ContactPoseSequenceMeta],
    object_names: Sequence[str],
) -> list[ContactPoseSequenceMeta]:
    if not object_names:
        raise ValueError("object_names must not be empty")

    by_object: dict[str, ContactPoseSequenceMeta] = {}
    for candidate in candidates:
        key = candidate.object_name.lower()
        incumbent = by_object.get(key)
        if incumbent is None or candidate.frame_count > incumbent.frame_count:
            by_object[key] = candidate

    selected: list[ContactPoseSequenceMeta] = []
    selected_keys: set[str] = set()
    for object_name in object_names:
        candidate = by_object.get(object_name.lower())
        if candidate is None:
            continue
        selected.append(candidate)
        selected_keys.add(candidate.object_name.lower())

    if len(selected) < len(object_names):
        remaining = sorted(
            (
                candidate
                for key, candidate in by_object.items()
                if key not in selected_keys
            ),
            key=lambda candidate: (candidate.frame_count, candidate.object_name, candidate.archive_member),
            reverse=True,
        )
        for candidate in remaining:
            selected.append(candidate)
            if len(selected) == len(object_names):
                break

    if len(selected) < len(object_names):
        raise ValueError(
            f"insufficient ContactPose objects in sample: requested {len(object_names)}, found {len(selected)}"
        )
    return selected


def evaluate_contactpose_workload(
    sample_zip: Path,
    *,
    codec: XRCodec,
    min_frames: int = 45,
    max_frames: int = 90,
) -> dict[str, Any]:
    sample_zip = sample_zip.resolve()
    candidates = annotation_candidates_from_zip(
        sample_zip,
        min_frames=min_frames,
        require_both_hands=True,
    )
    selected = select_best_contactpose_candidate(candidates)
    annotation = read_annotation_from_zip(sample_zip, selected.archive_member)
    frames = build_zpe_frames_from_annotation(annotation, max_frames=max_frames)

    gate_b = evaluate_gate_b(frames, codec)
    packets = encode_sequence(codec, frames)
    packet_loss = evaluate_packet_loss_resilience(
        frames=frames,
        packets=packets,
        codec=codec,
        **TARGET_PACKET_LOSS_CASE,
    )
    acceptance = build_outward_acceptance(
        compression_metrics=gate_b.compression_metrics,
        fidelity_metrics=gate_b.fidelity_metrics,
        latency_metrics=gate_b.latency_metrics,
        packet_loss_metrics=packet_loss,
    )

    return {
        "workload": {
            "dataset": "ContactPose",
            "source_path": str(sample_zip),
            "source_sha256": sha256_of_file(sample_zip),
            "source_bytes": sample_zip.stat().st_size,
            "selected_sequence": asdict(selected),
            "frames_used": len(frames),
        },
        "codec": {
            "keyframe_interval": codec.keyframe_interval,
            "deadband_mm": codec.deadband_mm,
            "quant_step_mm": codec.quant_step_mm,
        },
        "compression_metrics": gate_b.compression_metrics,
        "fidelity_metrics": gate_b.fidelity_metrics,
        "latency_metrics": gate_b.latency_metrics,
        "packet_loss_metrics": packet_loss,
        "packet_digest_sha256": packet_hash_digest(packets),
        "acceptance": acceptance,
    }


def evaluate_contactpose_multi_sequence_workload(
    sample_zip: Path,
    *,
    codec: XRCodec,
    object_names: Sequence[str],
    min_frames: int = 45,
    max_frames: int = 90,
) -> dict[str, Any]:
    sample_zip = sample_zip.resolve()
    candidates = annotation_candidates_from_zip(
        sample_zip,
        min_frames=min_frames,
        require_both_hands=True,
    )
    selected_candidates = select_contactpose_candidates_for_objects(candidates, object_names)

    sequence_results: list[dict[str, Any]] = []
    for selected in selected_candidates:
        annotation = read_annotation_from_zip(sample_zip, selected.archive_member)
        frames = build_zpe_frames_from_annotation(annotation, max_frames=selected.frame_count)
        gate_b = evaluate_gate_b(frames, codec)
        packets = encode_sequence(codec, frames)
        packet_loss = evaluate_packet_loss_resilience(
            frames=frames,
            packets=packets,
            codec=codec,
            **TARGET_PACKET_LOSS_CASE,
        )
        acceptance = build_outward_acceptance(
            compression_metrics=gate_b.compression_metrics,
            fidelity_metrics=gate_b.fidelity_metrics,
            latency_metrics=gate_b.latency_metrics,
            packet_loss_metrics=packet_loss,
        )
        sequence_results.append(
            {
                "archive_member": selected.archive_member,
                "object_name": selected.object_name,
                "frame_count": selected.frame_count,
                "frames_used": len(frames),
                "compression_ratio_vs_raw": gate_b.compression_metrics["compression_ratio_vs_raw"],
                "mpjpe_mm": gate_b.fidelity_metrics["mpjpe_mm"],
                "latency_ms": gate_b.latency_metrics["combined_avg_ms"],
                "packet_loss_error_pct": packet_loss["pose_error_percent"],
                "modern_comparator_ratio_vs_zpe": gate_b.compression_metrics["modern_comparator"]["ratio_vs_zpe"],
                "sovereign_pass": acceptance["sovereign_pass"],
                "modern_comparator_beaten": acceptance["secondary_checks"]["modern_comparator_beaten"],
                "packet_digest_sha256": packet_hash_digest(packets),
            }
        )

    comparator_pass_count = sum(
        1 for result in sequence_results if result["modern_comparator_ratio_vs_zpe"] > 1.0
    )
    aggregate = {
        "sequence_count": len(sequence_results),
        "compression_ratio_vs_raw_mean": sum(result["compression_ratio_vs_raw"] for result in sequence_results)
        / len(sequence_results),
        "mpjpe_mm_mean": sum(result["mpjpe_mm"] for result in sequence_results) / len(sequence_results),
        "latency_ms_mean": sum(result["latency_ms"] for result in sequence_results) / len(sequence_results),
        "packet_loss_error_pct_mean": sum(result["packet_loss_error_pct"] for result in sequence_results)
        / len(sequence_results),
        "modern_comparator_pass_count": comparator_pass_count,
        "modern_comparator_requirement_met": comparator_pass_count >= 3,
        "all_sovereign_checks_passed": all(result["sovereign_pass"] for result in sequence_results),
    }
    return {
        "workload": {
            "dataset": "ContactPose",
            "source_path": str(sample_zip),
            "source_sha256": sha256_of_file(sample_zip),
            "source_bytes": sample_zip.stat().st_size,
            "requested_objects": list(object_names),
            "selected_objects": [candidate.object_name for candidate in selected_candidates],
        },
        "codec": {
            "keyframe_interval": codec.keyframe_interval,
            "deadband_mm": codec.deadband_mm,
            "quant_step_mm": codec.quant_step_mm,
        },
        "sequence_results": sequence_results,
        "aggregate": aggregate,
        "acceptance": {
            "verdict": "PASS" if aggregate["all_sovereign_checks_passed"] else "FAIL",
            "modern_comparator_requirement_met": aggregate["modern_comparator_requirement_met"],
        },
    }


def build_outward_acceptance(
    *,
    compression_metrics: dict[str, Any],
    fidelity_metrics: dict[str, Any],
    latency_metrics: dict[str, Any],
    packet_loss_metrics: dict[str, Any],
) -> dict[str, Any]:
    order_of_magnitude_vs_raw = compression_metrics["compression_ratio_vs_raw"] >= 10.0
    fidelity_floor = bool(fidelity_metrics["pass"])
    latency_floor = bool(latency_metrics["pass"])
    packet_loss_floor = bool(packet_loss_metrics["pass"])
    modern_comparator_beaten = compression_metrics["modern_comparator"]["ratio_vs_zpe"] > 1.0
    sovereign_pass = all(
        [
            order_of_magnitude_vs_raw,
            fidelity_floor,
            latency_floor,
            packet_loss_floor,
        ]
    )
    return {
        "sovereign_checks": {
            "order_of_magnitude_vs_raw": order_of_magnitude_vs_raw,
            "fidelity_floor": fidelity_floor,
            "latency_floor": latency_floor,
            "packet_loss_floor": packet_loss_floor,
        },
        "secondary_checks": {
            "modern_comparator_beaten": modern_comparator_beaten,
        },
        "verdict": "PASS" if sovereign_pass else "FAIL",
        "sovereign_pass": sovereign_pass,
    }


def render_contactpose_benchmark_markdown(summary: dict[str, Any]) -> str:
    workload = summary["workload"]
    compression = summary["compression_metrics"]
    fidelity = summary["fidelity_metrics"]
    latency = summary["latency_metrics"]
    packet_loss = summary["packet_loss_metrics"]
    acceptance = summary["acceptance"]
    return f"""# Phase 4 ContactPose Benchmark

## Workload

- dataset: `{workload['dataset']}`
- sample archive: `{Path(workload['source_path']).name}`
- selected member: `{workload['selected_sequence']['archive_member']}`
- object: `{workload['selected_sequence']['object_name']}`
- frames used: `{workload['frames_used']}`

## Metrics

- compression vs raw: `{compression['compression_ratio_vs_raw']:.3f}x`
- MPJPE: `{fidelity['mpjpe_mm']:.3f} mm`
- combined latency: `{latency['combined_avg_ms']:.3f} ms`
- pose error at 10% loss: `{packet_loss['pose_error_percent']:.3f}%`
- modern comparator ratio vs ZPE: `{compression['modern_comparator']['ratio_vs_zpe']:.3f}x`

## Acceptance

- sovereign verdict: `{acceptance['verdict']}`
- order of magnitude vs raw: `{acceptance['sovereign_checks']['order_of_magnitude_vs_raw']}`
- fidelity floor: `{acceptance['sovereign_checks']['fidelity_floor']}`
- latency floor: `{acceptance['sovereign_checks']['latency_floor']}`
- packet-loss floor: `{acceptance['sovereign_checks']['packet_loss_floor']}`
- secondary modern-comparator check: `{acceptance['secondary_checks']['modern_comparator_beaten']}`
"""


def render_contactpose_multi_sequence_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Phase 5 ContactPose Multi-Sequence Benchmark",
        "",
        "## Workload",
        "",
        f"- dataset: `{summary['workload']['dataset']}`",
        f"- sample archive: `{Path(summary['workload']['source_path']).name}`",
        f"- selected objects: `{', '.join(summary['workload']['selected_objects'])}`",
        "",
        "## Sequence Results",
        "",
        "| Object | Compression vs raw | MPJPE (mm) | Latency (ms) | Packet-loss error (%) | Modern comparator ratio vs ZPE |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for result in summary["sequence_results"]:
        lines.append(
            f"| {result['object_name']} | {result['compression_ratio_vs_raw']:.3f}x | "
            f"{result['mpjpe_mm']:.3f} | {result['latency_ms']:.3f} | "
            f"{result['packet_loss_error_pct']:.3f} | {result['modern_comparator_ratio_vs_zpe']:.3f}x |"
        )

    aggregate = summary["aggregate"]
    lines.extend(
        [
            "",
            "## Aggregate",
            "",
            f"- sequence count: `{aggregate['sequence_count']}`",
            f"- mean compression vs raw: `{aggregate['compression_ratio_vs_raw_mean']:.3f}x`",
            f"- mean MPJPE: `{aggregate['mpjpe_mm_mean']:.3f} mm`",
            f"- mean latency: `{aggregate['latency_ms_mean']:.3f} ms`",
            f"- mean packet-loss error: `{aggregate['packet_loss_error_pct_mean']:.3f}%`",
            f"- modern comparator passes: `{aggregate['modern_comparator_pass_count']}` of `{aggregate['sequence_count']}`",
            f"- comparator requirement met: `{aggregate['modern_comparator_requirement_met']}`",
            f"- sovereign verdict: `{summary['acceptance']['verdict']}`",
        ]
    )
    return "\n".join(lines) + "\n"
