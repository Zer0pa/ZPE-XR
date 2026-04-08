"""Benchmark helpers for InterHand2.6M sequence selection and reporting."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .codec import XRCodec
from .interhand_adapter import (
    InterHandAnnotations,
    InterHandSequenceMeta,
    build_zpe_frames_from_interhand_sequence,
    collect_interhand_sequences,
    load_interhand_joint_annotations,
)
from .pipeline import evaluate_gate_b


def benchmark_interhand_paths(
    paths_by_split: Mapping[str, Path],
    *,
    min_frames: int = 90,
    max_sequences: int = 3,
    max_frames_per_sequence: int | None = None,
) -> dict[str, Any]:
    annotations_by_split: dict[str, InterHandAnnotations] = {}
    sequences_by_split: dict[str, list[InterHandSequenceMeta]] = {}

    for split, path in paths_by_split.items():
        if not path.exists():
            continue
        annotations = load_interhand_joint_annotations(path)
        annotations_by_split[split] = annotations
        sequences_by_split[split] = collect_interhand_sequences(
            annotations,
            split=split,
            min_frames=min_frames,
            require_full_valid=True,
        )

    selected = select_interhand_sequences(sequences_by_split, max_sequences=max_sequences)
    codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)

    sequence_results = []
    total_frames = 0
    for sequence in selected:
        annotations = annotations_by_split[sequence.split]
        frames = build_zpe_frames_from_interhand_sequence(
            annotations,
            sequence,
            max_frames=max_frames_per_sequence,
        )
        gate_b = evaluate_gate_b(frames, codec)
        total_frames += len(frames)
        sequence_results.append(
            {
                "split": sequence.split,
                "capture_id": sequence.capture_id,
                "seq_id": sequence.seq_id,
                "source_frame_count": sequence.frame_count,
                "frames_used": len(frames),
                "compression_ratio_vs_raw": gate_b.compression_metrics["compression_ratio_vs_raw"],
                "mpjpe_mm": gate_b.fidelity_metrics["mpjpe_mm"],
                "combined_latency_ms": gate_b.latency_metrics["combined_avg_ms"],
                "quality_pass": bool(gate_b.fidelity_metrics["pass"]),
                "latency_pass": bool(gate_b.latency_metrics["pass"]),
            }
        )

    if not sequence_results:
        raise RuntimeError("no InterHand sequences satisfied the requested benchmark constraints")

    return {
        "dataset": "InterHand2.6M",
        "splits_used": [row["split"] for row in sequence_results],
        "sequence_results": sequence_results,
        "aggregate": {
            "sequence_count": len(sequence_results),
            "frame_count_total": total_frames,
            "compression_ratio_vs_raw_mean": _mean(row["compression_ratio_vs_raw"] for row in sequence_results),
            "mpjpe_mm_mean": _mean(row["mpjpe_mm"] for row in sequence_results),
            "combined_latency_ms_mean": _mean(row["combined_latency_ms"] for row in sequence_results),
            "all_quality_passed": all(row["quality_pass"] for row in sequence_results),
            "all_latency_passed": all(row["latency_pass"] for row in sequence_results),
        },
    }


def render_interhand_benchmark_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Phase 3 InterHand2.6M Benchmark",
        "",
        f"- dataset: `{report['dataset']}`",
        f"- splits: `{', '.join(report['splits_used'])}`",
        f"- total frames: `{report['aggregate']['frame_count_total']}`",
        "",
        "| Split | Capture | Sequence | Frames | Ratio | MPJPE (mm) | Combined latency (ms) |",
        "|-------|---------|----------|--------|-------|------------|-----------------------|",
    ]
    for row in report["sequence_results"]:
        lines.append(
            f"| {row['split']} | {row['capture_id']} | {row['seq_id']} | {row['frames_used']} | "
            f"{row['compression_ratio_vs_raw']:.3f}x | {row['mpjpe_mm']:.3f} | {row['combined_latency_ms']:.3f} |"
        )

    aggregate = report["aggregate"]
    lines.extend(
        [
            "",
            "## Aggregate",
            "",
            f"- mean compression vs raw: `{aggregate['compression_ratio_vs_raw_mean']:.3f}x`",
            f"- mean MPJPE: `{aggregate['mpjpe_mm_mean']:.3f} mm`",
            f"- mean combined latency: `{aggregate['combined_latency_ms_mean']:.3f} ms`",
            f"- quality pass: `{aggregate['all_quality_passed']}`",
            f"- latency pass: `{aggregate['all_latency_passed']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def select_interhand_sequences(
    sequences_by_split: Mapping[str, list[InterHandSequenceMeta]],
    *,
    max_sequences: int = 3,
) -> list[InterHandSequenceMeta]:
    preferred_order = ("train", "val", "test")
    selected: list[InterHandSequenceMeta] = []
    used_keys: set[tuple[str, str, str]] = set()

    for split in preferred_order:
        candidates = sequences_by_split.get(split, [])
        if not candidates:
            continue
        choice = candidates[0]
        selected.append(choice)
        used_keys.add((choice.split, choice.capture_id, choice.seq_id))
        if len(selected) >= max_sequences:
            return selected

    remainder = []
    for split, candidates in sequences_by_split.items():
        for candidate in candidates:
            key = (candidate.split, candidate.capture_id, candidate.seq_id)
            if key in used_keys:
                continue
            remainder.append(candidate)
    remainder.sort(key=lambda item: (-item.frame_count, item.split, item.capture_id, item.seq_id))

    for candidate in remainder:
        selected.append(candidate)
        if len(selected) >= max_sequences:
            break
    return selected


def _mean(values: Any) -> float:
    values = list(values)
    return float(sum(values) / len(values))
