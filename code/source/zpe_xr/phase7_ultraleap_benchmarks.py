"""Phase 07 helpers for local Ultraleap comparison against ZPE-XR."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import platform
from time import perf_counter_ns
from typing import Any, Mapping, Sequence

from .codec import XRCodec
from .contactpose_adapter import (
    annotation_candidates_from_zip,
    build_zpe_frames_from_annotation,
    read_annotation_from_zip,
)
from .constants import FPS, RAW_BYTES_PER_FRAME
from .external_benchmarks import (
    ComparatorMeasurement,
    bytes_per_frame_to_kbytes_per_second,
    ultraleap_vectorhand_measurement,
)
from .io_utils import sha256_of_file
from .metrics import mpjpe_mm, packet_hash_digest, percentile, pose_error_percent
from .models import Frame
from .network import simulate_realtime_packet_map
from .outward_workload import (
    CONTACTPOSE_SAMPLE_FILENAME,
    TARGET_PACKET_LOSS_CASE,
    ensure_contactpose_sample,
    select_contactpose_candidates_for_objects,
)
from .pipeline import evaluate_gate_b, evaluate_packet_loss_resilience
from .runtime_paths import artifact_base_dir, canonical_root
from .synthetic import generate_sequence
from .ultraleap_vectorhand import encode_frame as ultraleap_encode_frame
from .ultraleap_vectorhand import decode_frame as ultraleap_decode_frame

_CONTACTPOSE_OBJECTS = ("mug", "wine_glass", "bowl", "camera", "binoculars")


def host_metadata() -> dict[str, object]:
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
    }


def benchmark_report(
    *,
    root: Path,
    num_frames: int,
    gesture: str,
    seed: int,
    attempt_contactpose: bool,
) -> dict[str, object]:
    frames = generate_sequence(num_frames=num_frames, gesture=gesture, seed=seed)
    synthetic = compare_sequence_rows(frames, measurement=ultraleap_vectorhand_measurement())
    contactpose = (
        compare_contactpose_multi_sequence(root=root, object_names=_CONTACTPOSE_OBJECTS)
        if attempt_contactpose
        else {"status": "skipped"}
    )
    return {
        "host": host_metadata(),
        "canonical_root": str(canonical_root(root)),
        "workload": {
            "kind": "synthetic_frozen_v1",
            "frames": num_frames,
            "gesture": gesture,
            "seed": seed,
            "fps": FPS,
        },
        "synthetic": synthetic,
        "contactpose": contactpose,
        "conclusions": build_conclusions(synthetic=synthetic, contactpose=contactpose),
        "unresolved": [
            "The Ultraleap lane is now same-machine and proxy-measured, but it is still not a full vendor runtime benchmark.",
            "Photon, Unity NGO, and Normcore remain open or reference-only lanes.",
            "A public-incumbent displacement claim still requires the remaining runtime and channel caveats to stay explicit.",
        ],
    }


def compare_sequence_rows(
    frames: Sequence[Frame],
    *,
    measurement: ComparatorMeasurement,
) -> dict[str, object]:
    zpe_row = measure_zpe_row(frames)
    ultraleap_row = measure_ultraleap_row(frames, measurement=measurement)
    return {
        "rows": [zpe_row, ultraleap_row],
        "relative": relative_verdict(zpe_row=zpe_row, incumbent_row=ultraleap_row),
    }


def compare_contactpose_multi_sequence(
    *,
    root: Path,
    object_names: Sequence[str],
    min_frames: int = 45,
    max_frames: int = 90,
) -> dict[str, object]:
    destination = artifact_base_dir(root) / "phase7_contactpose_probe" / "downloads" / CONTACTPOSE_SAMPLE_FILENAME
    sample_zip = ensure_contactpose_sample(destination, search_root=canonical_root(root))
    candidates = annotation_candidates_from_zip(
        sample_zip,
        min_frames=min_frames,
        require_both_hands=True,
    )
    selected_candidates = select_contactpose_candidates_for_objects(candidates, object_names)
    measurement = ultraleap_vectorhand_measurement()

    sequence_results: list[dict[str, object]] = []
    for selected in selected_candidates:
        annotation = read_annotation_from_zip(sample_zip, selected.archive_member)
        frames = build_zpe_frames_from_annotation(annotation, max_frames=max_frames)
        comparison = compare_sequence_rows(frames, measurement=measurement)
        sequence_results.append(
            {
                "archive_member": selected.archive_member,
                "object_name": selected.object_name,
                "frame_count": selected.frame_count,
                "frames_used": len(frames),
                "zpe": comparison["rows"][0],
                "ultraleap": comparison["rows"][1],
                "relative": comparison["relative"],
            }
        )

    return {
        "status": "executed",
        "workload": {
            "dataset": "ContactPose",
            "source_path": str(sample_zip),
            "source_sha256": sha256_of_file(sample_zip),
            "source_bytes": sample_zip.stat().st_size,
            "requested_objects": list(object_names),
            "selected_objects": [candidate.object_name for candidate in selected_candidates],
        },
        "sequence_results": sequence_results,
        "aggregate": {
            "zpe": aggregate_row_metrics(result["zpe"] for result in sequence_results),
            "ultraleap": aggregate_row_metrics(result["ultraleap"] for result in sequence_results),
            "zpe_smaller_on_all_sequences": all(
                bool(result["relative"]["zpe_smaller_on_bytes"]) for result in sequence_results
            ),
            "zpe_lower_latency_on_mean": aggregate_row_metrics(result["zpe"] for result in sequence_results)["latency_ms_mean"]
            < aggregate_row_metrics(result["ultraleap"] for result in sequence_results)["latency_ms_mean"],
            "zpe_lower_mpjpe_on_mean": aggregate_row_metrics(result["zpe"] for result in sequence_results)["mpjpe_mm_mean"]
            < aggregate_row_metrics(result["ultraleap"] for result in sequence_results)["mpjpe_mm_mean"],
        },
    }


def measure_zpe_row(frames: Sequence[Frame]) -> dict[str, object]:
    codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)
    gate_b = evaluate_gate_b(frames, codec)
    packet_loss = evaluate_packet_loss_resilience(
        frames=frames,
        packets=gate_b.packets,
        codec=codec,
        **TARGET_PACKET_LOSS_CASE,
    )
    return {
        "comparator_id": "zpe_xr_root_current",
        "label": "ZPE-XR canonical root codec",
        "evidence_class": "measured_local",
        "fairness_class": "frozen_v1_authority_surface",
        "semantics": "Two hands, 26 joints per hand, deterministic keyframe+delta transport from the canonical root workspace.",
        "source_reference": "local_root_workspace",
        "notes": "Measured locally from the canonical root codec path.",
        "transport": {
            "bytes_per_frame": float(gate_b.compression_metrics["encoded_stats"]["avg_bytes"]),
            "bytes_total": float(gate_b.compression_metrics["encoded_bytes_total"]),
            "compression_ratio_vs_raw": float(gate_b.compression_metrics["compression_ratio_vs_raw"]),
            "kb_per_s_single_remote": bytes_per_frame_to_kbytes_per_second(
                float(gate_b.compression_metrics["encoded_stats"]["avg_bytes"]),
                fps=FPS,
                remote_players=1,
            ),
            "kb_per_s_modeled_4_player_session": bytes_per_frame_to_kbytes_per_second(
                float(gate_b.compression_metrics["encoded_stats"]["avg_bytes"]),
                fps=FPS,
                remote_players=3,
            ),
        },
        "latency": {
            "encode_avg_ms": float(gate_b.latency_metrics["encode_avg_ms"]),
            "decode_avg_ms": float(gate_b.latency_metrics["decode_avg_ms"]),
            "combined_avg_ms": float(gate_b.latency_metrics["combined_avg_ms"]),
            "combined_p95_ms": float(gate_b.latency_metrics["combined_p95_ms"]),
            "combined_p99_ms": float(gate_b.latency_metrics["combined_p99_ms"]),
        },
        "fidelity": {
            "mpjpe_mm": float(gate_b.fidelity_metrics["mpjpe_mm"]),
        },
        "packet_loss": {
            "pose_error_percent": float(packet_loss["pose_error_percent"]),
            "mpjpe_mm": float(packet_loss["mpjpe_mm"]),
            "delivery_stats": dict(packet_loss["delivery_stats"]),
        },
        "packet_digest_sha256": packet_hash_digest(gate_b.packets),
    }


def measure_ultraleap_row(
    frames: Sequence[Frame],
    *,
    measurement: ComparatorMeasurement,
) -> dict[str, object]:
    packets: list[bytes] = []
    decoded_positions: list[list[tuple[float, float, float]]] = []
    encode_ns: list[int] = []
    decode_ns: list[int] = []

    for frame in frames:
        t0 = perf_counter_ns()
        packet = ultraleap_encode_frame(frame)
        t1 = perf_counter_ns()
        decoded = ultraleap_decode_frame(packet, seq=frame.seq, timestamp_ms=frame.timestamp_ms)
        t2 = perf_counter_ns()
        packets.append(packet)
        decoded_positions.append(list(decoded.positions))
        encode_ns.append(t1 - t0)
        decode_ns.append(t2 - t1)

    bytes_total = sum(len(packet) for packet in packets)
    packet_loss = evaluate_ultraleap_packet_loss(
        frames=frames,
        packets=packets,
        **TARGET_PACKET_LOSS_CASE,
    )
    return {
        "comparator_id": "ultraleap_vectorhand_local_proxy",
        "label": "Ultraleap VectorHand local proxy",
        "evidence_class": "proxy_measured_local",
        "fairness_class": measurement.fairness_class,
        "semantics": measurement.semantics,
        "source_reference": measurement.source_reference,
        "notes": (
            "Measured locally with the published VectorHand byte layout and an inferred 4-byte normalized quaternion packing, "
            "not a full vendor runtime path."
        ),
        "transport": transport_metrics(bytes_total=bytes_total, num_frames=len(frames)),
        "latency": latency_metrics(encode_ns=encode_ns, decode_ns=decode_ns),
        "fidelity": {
            "mpjpe_mm": mpjpe_mm(
                [list(frame.positions) for frame in frames],
                decoded_positions,
            ),
        },
        "packet_loss": packet_loss,
        "packet_digest_sha256": packet_hash_digest(packets),
    }


def evaluate_ultraleap_packet_loss(
    *,
    frames: Sequence[Frame],
    packets: Sequence[bytes],
    loss_rate: float,
    jitter_probability: float,
    max_delay_frames: int,
    seed: int,
) -> dict[str, object]:
    packets_by_seq = simulate_realtime_packet_map(
        packets,
        loss_rate=loss_rate,
        jitter_probability=jitter_probability,
        max_delay_frames=max_delay_frames,
        seed=seed,
    )
    decoded_positions: list[list[tuple[float, float, float]]] = []
    last_positions: list[tuple[float, float, float]] | None = None
    concealed_frames = 0

    for frame_index, frame in enumerate(frames):
        packet = packets_by_seq.get(frame_index)
        if packet is None:
            concealed_frames += 1
            positions = last_positions or [(0.0, 0.0, 0.0)] * len(frame.positions)
        else:
            positions = list(
                ultraleap_decode_frame(packet, seq=frame.seq, timestamp_ms=frame.timestamp_ms).positions
            )
        decoded_positions.append(list(positions))
        last_positions = list(positions)

    reference_positions = [list(frame.positions) for frame in frames]
    mpjpe = mpjpe_mm(reference_positions, decoded_positions)
    pose_pct = pose_error_percent(mpjpe, reference_span_mm=120.0)
    return {
        "loss_rate": loss_rate,
        "jitter_probability": jitter_probability,
        "max_delay_frames": max_delay_frames,
        "seed": seed,
        "mpjpe_mm": mpjpe,
        "pose_error_percent": pose_pct,
        "delivery_stats": {
            "provided_packets": len(packets_by_seq),
            "missing_packets": max(len(frames) - len(packets_by_seq), 0),
            "total_frames": len(frames),
        },
        "decoder_stats": {
            "concealed_frames": concealed_frames,
            "backup_recoveries": 0,
            "parse_failures": 0,
        },
    }


def aggregate_row_metrics(rows: Sequence[dict[str, object]] | Any) -> dict[str, float]:
    rows = list(rows)
    return {
        "bytes_per_frame_mean": mean(float(row["transport"]["bytes_per_frame"]) for row in rows),
        "compression_ratio_vs_raw_mean": mean(
            float(row["transport"]["compression_ratio_vs_raw"]) for row in rows
        ),
        "latency_ms_mean": mean(float(row["latency"]["combined_avg_ms"]) for row in rows),
        "mpjpe_mm_mean": mean(float(row["fidelity"]["mpjpe_mm"]) for row in rows),
        "packet_loss_error_pct_mean": mean(
            float(row["packet_loss"]["pose_error_percent"]) for row in rows
        ),
    }


def relative_verdict(*, zpe_row: Mapping[str, object], incumbent_row: Mapping[str, object]) -> dict[str, object]:
    zpe_transport = zpe_row["transport"]
    incumbent_transport = incumbent_row["transport"]
    zpe_latency = zpe_row["latency"]
    incumbent_latency = incumbent_row["latency"]
    zpe_fidelity = zpe_row["fidelity"]
    incumbent_fidelity = incumbent_row["fidelity"]
    return {
        "zpe_smaller_on_bytes": float(zpe_transport["bytes_per_frame"]) < float(incumbent_transport["bytes_per_frame"]),
        "bytes_ratio_incumbent_vs_zpe": float(incumbent_transport["bytes_per_frame"])
        / float(zpe_transport["bytes_per_frame"]),
        "zpe_lower_latency": float(zpe_latency["combined_avg_ms"]) < float(incumbent_latency["combined_avg_ms"]),
        "latency_ratio_incumbent_vs_zpe": float(incumbent_latency["combined_avg_ms"])
        / float(zpe_latency["combined_avg_ms"]),
        "zpe_lower_mpjpe": float(zpe_fidelity["mpjpe_mm"]) < float(incumbent_fidelity["mpjpe_mm"]),
    }


def transport_metrics(*, bytes_total: int, num_frames: int) -> dict[str, float]:
    bytes_per_frame = bytes_total / max(num_frames, 1)
    return {
        "bytes_total": float(bytes_total),
        "bytes_per_frame": float(bytes_per_frame),
        "compression_ratio_vs_raw": float(RAW_BYTES_PER_FRAME / bytes_per_frame),
        "kb_per_s_single_remote": float(
            bytes_per_frame_to_kbytes_per_second(bytes_per_frame, fps=FPS, remote_players=1)
        ),
        "kb_per_s_modeled_4_player_session": float(
            bytes_per_frame_to_kbytes_per_second(bytes_per_frame, fps=FPS, remote_players=3)
        ),
    }


def latency_metrics(*, encode_ns: Sequence[int], decode_ns: Sequence[int]) -> dict[str, float]:
    per_frame_ms = [(encode + decode) / 1_000_000.0 for encode, decode in zip(encode_ns, decode_ns)]
    encode_ms = [value / 1_000_000.0 for value in encode_ns]
    decode_ms = [value / 1_000_000.0 for value in decode_ns]
    return {
        "encode_avg_ms": mean(encode_ms),
        "decode_avg_ms": mean(decode_ms),
        "combined_avg_ms": mean(per_frame_ms),
        "combined_p95_ms": percentile(per_frame_ms, 95),
        "combined_p99_ms": percentile(per_frame_ms, 99),
    }


def render_markdown(report: Mapping[str, object]) -> str:
    synthetic_rows = report["synthetic"]["rows"]
    lines = [
        "# Phase 07 Ultraleap Local Benchmark",
        "",
        "## Host",
        "",
        f"- platform: `{report['host']['platform']} {report['host']['platform_release']}`",
        f"- machine: `{report['host']['machine']}`",
        f"- python: `{report['host']['python_version']}`",
        "",
        "## Synthetic Benchmark",
        "",
        f"- frames: `{report['workload']['frames']}`",
        f"- gesture: `{report['workload']['gesture']}`",
        f"- seed: `{report['workload']['seed']}`",
        "",
        "| Comparator | Evidence | Bytes/frame | Compression vs raw | 4-player KB/s @90 | Combined latency ms | MPJPE mm | 10% loss error % |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in synthetic_rows:
        lines.append(
            f"| {row['label']} | {row['evidence_class']} | "
            f"{row['transport']['bytes_per_frame']:.3f} | "
            f"{row['transport']['compression_ratio_vs_raw']:.3f}x | "
            f"{row['transport']['kb_per_s_modeled_4_player_session']:.3f} | "
            f"{row['latency']['combined_avg_ms']:.3f} | "
            f"{row['fidelity']['mpjpe_mm']:.3f} | "
            f"{row['packet_loss']['pose_error_percent']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Synthetic Relative Read",
            "",
            f"- ZPE smaller on bytes: `{report['synthetic']['relative']['zpe_smaller_on_bytes']}`",
            f"- incumbent/ZPE bytes ratio: `{report['synthetic']['relative']['bytes_ratio_incumbent_vs_zpe']:.3f}x`",
            f"- ZPE lower latency: `{report['synthetic']['relative']['zpe_lower_latency']}`",
            f"- ZPE lower MPJPE: `{report['synthetic']['relative']['zpe_lower_mpjpe']}`",
            "",
        ]
    )

    contactpose = report["contactpose"]
    if contactpose["status"] == "executed":
        lines.extend(
            [
                "## ContactPose Multi-Sequence",
                "",
                f"- sample archive: `{Path(contactpose['workload']['source_path']).name}`",
                f"- selected objects: `{', '.join(contactpose['workload']['selected_objects'])}`",
                "",
                "| Object | ZPE bytes/frame | Ultraleap bytes/frame | ZPE latency ms | Ultraleap latency ms | ZPE MPJPE mm | Ultraleap MPJPE mm |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for result in contactpose["sequence_results"]:
            lines.append(
                f"| {result['object_name']} | "
                f"{result['zpe']['transport']['bytes_per_frame']:.3f} | "
                f"{result['ultraleap']['transport']['bytes_per_frame']:.3f} | "
                f"{result['zpe']['latency']['combined_avg_ms']:.3f} | "
                f"{result['ultraleap']['latency']['combined_avg_ms']:.3f} | "
                f"{result['zpe']['fidelity']['mpjpe_mm']:.3f} | "
                f"{result['ultraleap']['fidelity']['mpjpe_mm']:.3f} |"
            )
        lines.extend(
            [
                "",
                "## ContactPose Aggregate",
                "",
                f"- ZPE mean bytes/frame: `{contactpose['aggregate']['zpe']['bytes_per_frame_mean']:.3f}`",
                f"- Ultraleap mean bytes/frame: `{contactpose['aggregate']['ultraleap']['bytes_per_frame_mean']:.3f}`",
                f"- ZPE mean latency: `{contactpose['aggregate']['zpe']['latency_ms_mean']:.3f} ms`",
                f"- Ultraleap mean latency: `{contactpose['aggregate']['ultraleap']['latency_ms_mean']:.3f} ms`",
                f"- ZPE mean MPJPE: `{contactpose['aggregate']['zpe']['mpjpe_mm_mean']:.3f} mm`",
                f"- Ultraleap mean MPJPE: `{contactpose['aggregate']['ultraleap']['mpjpe_mm_mean']:.3f} mm`",
                f"- ZPE smaller on all sequences: `{contactpose['aggregate']['zpe_smaller_on_all_sequences']}`",
                f"- ZPE lower latency on mean: `{contactpose['aggregate']['zpe_lower_latency_on_mean']}`",
                f"- ZPE lower MPJPE on mean: `{contactpose['aggregate']['zpe_lower_mpjpe_on_mean']}`",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## ContactPose Multi-Sequence",
                "",
                f"- status: `{contactpose['status']}`",
                "",
            ]
        )

    lines.extend(["## Conclusions", ""])
    for conclusion in report["conclusions"]:
        lines.append(f"- {conclusion}")
    return "\n".join(lines) + "\n"


def build_conclusions(*, synthetic: Mapping[str, object], contactpose: Mapping[str, object]) -> list[str]:
    conclusions = []
    if synthetic["relative"]["zpe_smaller_on_bytes"]:
        conclusions.append("ZPE-XR remains smaller than the same-machine Ultraleap local proxy on the frozen synthetic lane.")
    else:
        conclusions.append("ZPE-XR does not beat the same-machine Ultraleap local proxy on synthetic bytes/frame.")
    if synthetic["relative"]["zpe_lower_latency"]:
        conclusions.append("ZPE-XR has lower measured synthetic latency than the local Ultraleap proxy on this Mac.")
    else:
        conclusions.append("The local Ultraleap proxy has lower or equal measured synthetic latency on this Mac.")
    if contactpose.get("status") == "executed":
        if contactpose["aggregate"]["zpe_smaller_on_all_sequences"]:
            conclusions.append("ZPE-XR stays smaller than the local Ultraleap proxy across the executed ContactPose multi-sequence object set.")
        else:
            conclusions.append("ZPE-XR does not stay smaller than the local Ultraleap proxy across every executed ContactPose sequence.")
        conclusions.append(
            "Ultraleap is now a same-machine local proxy-measured incumbent row rather than a transport-only placeholder."
        )
    return conclusions


def mean(values: Sequence[float] | Any) -> float:
    values = list(values)
    if not values:
        return 0.0
    return float(sum(values) / len(values))
