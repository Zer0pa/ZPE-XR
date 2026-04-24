"""Phase 08 helpers for same-machine Photon-style local comparison against ZPE-XR."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import platform
from time import perf_counter_ns
from typing import Mapping, Sequence

from .contactpose_adapter import (
    annotation_candidates_from_zip,
    build_zpe_frames_from_annotation,
    read_annotation_from_zip,
)
from .external_benchmarks import photon_fusion_measurement
from .io_utils import sha256_of_file
from .metrics import mpjpe_mm, packet_hash_digest, pose_error_percent
from .models import Frame
from .network import simulate_realtime_packet_map
from .outward_workload import (
    CONTACTPOSE_SAMPLE_FILENAME,
    TARGET_PACKET_LOSS_CASE,
    ensure_contactpose_sample,
    select_contactpose_candidates_for_objects,
)
from .phase7_ultraleap_benchmarks import (
    aggregate_row_metrics,
    latency_metrics,
    mean,
    measure_zpe_row,
    relative_verdict,
    transport_metrics,
)
from .photon_hands_proxy import (
    PHOTON_COMPRESSED_BYTES_PER_HAND,
    calibrate_sequence,
    decode_frame as photon_decode_frame,
    encode_frame as photon_encode_frame,
)
from .runtime_paths import artifact_base_dir, canonical_root

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
    synthetic_frames: Sequence[Frame],
    attempt_contactpose: bool,
) -> dict[str, object]:
    synthetic = compare_sequence_rows(synthetic_frames)
    contactpose = (
        compare_contactpose_multi_sequence(root=root, object_names=_CONTACTPOSE_OBJECTS)
        if attempt_contactpose
        else {"status": "skipped"}
    )
    return {
        "host": host_metadata(),
        "canonical_root": str(canonical_root(root)),
        "workload": {
            "kind": "same_machine_photon_articulation_proxy",
            "fps": 90,
            "synthetic_frames": len(synthetic_frames),
        },
        "synthetic": synthetic,
        "contactpose": contactpose,
        "conclusions": build_conclusions(synthetic=synthetic, contactpose=contactpose),
        "unresolved": [
            "The Photon lane is now same-machine and proxy-measured, but it still relies on shared per-frame hand-root pose side input.",
            "The executed row is not the vendor runtime path and does not close public Photon displacement by itself.",
            "The governing multi-sequence modern-comparator public gate remains unchanged from Phase 5.",
        ],
    }


def compare_sequence_rows(frames: Sequence[Frame]) -> dict[str, object]:
    calibration = calibrate_sequence(frames)
    zpe_row = measure_zpe_row(frames)
    photon_row = measure_photon_row(frames, calibration=calibration)
    return {
        "rows": [zpe_row, photon_row],
        "relative": relative_verdict(zpe_row=zpe_row, incumbent_row=photon_row),
    }


def compare_contactpose_multi_sequence(
    *,
    root: Path,
    object_names: Sequence[str],
    min_frames: int = 45,
    max_frames: int = 90,
) -> dict[str, object]:
    destination = artifact_base_dir(root) / "phase8_contactpose_probe" / "downloads" / CONTACTPOSE_SAMPLE_FILENAME
    sample_zip = ensure_contactpose_sample(destination, search_root=canonical_root(root))
    candidates = annotation_candidates_from_zip(
        sample_zip,
        min_frames=min_frames,
        require_both_hands=True,
    )
    selected_candidates = select_contactpose_candidates_for_objects(candidates, object_names)

    sequence_results: list[dict[str, object]] = []
    for selected in selected_candidates:
        annotation = read_annotation_from_zip(sample_zip, selected.archive_member)
        frames = build_zpe_frames_from_annotation(annotation, max_frames=max_frames)
        comparison = compare_sequence_rows(frames)
        sequence_results.append(
            {
                "archive_member": selected.archive_member,
                "object_name": selected.object_name,
                "frame_count": selected.frame_count,
                "frames_used": len(frames),
                "zpe": comparison["rows"][0],
                "photon": comparison["rows"][1],
                "relative": comparison["relative"],
            }
        )

    zpe_aggregate = aggregate_row_metrics(result["zpe"] for result in sequence_results)
    photon_aggregate = aggregate_row_metrics(result["photon"] for result in sequence_results)
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
            "zpe": zpe_aggregate,
            "photon": photon_aggregate,
            "zpe_smaller_on_all_sequences": all(
                bool(result["relative"]["zpe_smaller_on_bytes"]) for result in sequence_results
            ),
            "zpe_lower_latency_on_mean": zpe_aggregate["latency_ms_mean"] < photon_aggregate["latency_ms_mean"],
            "zpe_lower_mpjpe_on_mean": zpe_aggregate["mpjpe_mm_mean"] < photon_aggregate["mpjpe_mm_mean"],
        },
    }


def measure_photon_row(
    frames: Sequence[Frame],
    *,
    calibration=None,
) -> dict[str, object]:
    measurement = photon_fusion_measurement()
    calibration = calibration or calibrate_sequence(frames)

    packets: list[bytes] = []
    decoded_positions: list[list[tuple[float, float, float]]] = []
    encode_ns: list[int] = []
    decode_ns: list[int] = []

    for frame in frames:
        t0 = perf_counter_ns()
        packet = photon_encode_frame(frame, calibration)
        t1 = perf_counter_ns()
        decoded = photon_decode_frame(
            packet,
            calibration=calibration,
            root_frame=frame,
            seq=frame.seq,
            timestamp_ms=frame.timestamp_ms,
        )
        t2 = perf_counter_ns()
        packets.append(packet)
        decoded_positions.append(list(decoded.positions))
        encode_ns.append(t1 - t0)
        decode_ns.append(t2 - t1)

    bytes_total = sum(len(packet) for packet in packets)
    packet_loss = evaluate_photon_packet_loss(
        frames=frames,
        packets=packets,
        calibration=calibration,
        **TARGET_PACKET_LOSS_CASE,
    )
    return {
        "comparator_id": "photon_fusion_local_articulation_proxy",
        "label": "Photon Fusion XR Hands local articulation proxy",
        "evidence_class": "proxy_measured_local",
        "fairness_class": "narrower_semantics_than_frozen_v1",
        "semantics": (
            "Finger-bone articulation only at the published 19-byte-per-hand budget, "
            "with shared per-frame hand-root pose and fixed local bone positions treated as side input."
        ),
        "source_reference": measurement.source_reference,
        "notes": (
            "Measured locally from a 19-byte-per-hand articulation proxy that preserves the published Photon byte budget "
            "but does not execute the vendor runtime or meter the shared hand-root pose."
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


def evaluate_photon_packet_loss(
    *,
    frames: Sequence[Frame],
    packets: Sequence[bytes],
    calibration,
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
    last_packet: bytes | None = None
    concealed_frames = 0

    for frame_index, frame in enumerate(frames):
        packet = packets_by_seq.get(frame_index)
        if packet is None:
            concealed_frames += 1
            packet = last_packet

        if packet is None:
            positions = [(0.0, 0.0, 0.0)] * len(frame.positions)
        else:
            positions = list(
                photon_decode_frame(
                    packet,
                    calibration=calibration,
                    root_frame=frame,
                    seq=frame.seq,
                    timestamp_ms=frame.timestamp_ms,
                ).positions
            )
            last_packet = packet

        decoded_positions.append(list(positions))

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


def render_markdown(report: Mapping[str, object]) -> str:
    synthetic_rows = report["synthetic"]["rows"]
    lines = [
        "# Phase 08 Photon Local Benchmark",
        "",
        "## Host",
        "",
        f"- platform: `{report['host']['platform']} {report['host']['platform_release']}`",
        f"- machine: `{report['host']['machine']}`",
        f"- python: `{report['host']['python_version']}`",
        "",
        "## Synthetic Benchmark",
        "",
        f"- synthetic frames: `{report['workload']['synthetic_frames']}`",
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
                "| Object | ZPE bytes/frame | Photon bytes/frame | ZPE latency ms | Photon latency ms | ZPE MPJPE mm | Photon MPJPE mm |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for result in contactpose["sequence_results"]:
            lines.append(
                f"| {result['object_name']} | "
                f"{result['zpe']['transport']['bytes_per_frame']:.3f} | "
                f"{result['photon']['transport']['bytes_per_frame']:.3f} | "
                f"{result['zpe']['latency']['combined_avg_ms']:.3f} | "
                f"{result['photon']['latency']['combined_avg_ms']:.3f} | "
                f"{result['zpe']['fidelity']['mpjpe_mm']:.3f} | "
                f"{result['photon']['fidelity']['mpjpe_mm']:.3f} |"
            )
        lines.extend(
            [
                "",
                "## ContactPose Aggregate",
                "",
                f"- ZPE mean bytes/frame: `{contactpose['aggregate']['zpe']['bytes_per_frame_mean']:.3f}`",
                f"- Photon mean bytes/frame: `{contactpose['aggregate']['photon']['bytes_per_frame_mean']:.3f}`",
                f"- ZPE mean latency: `{contactpose['aggregate']['zpe']['latency_ms_mean']:.3f} ms`",
                f"- Photon mean latency: `{contactpose['aggregate']['photon']['latency_ms_mean']:.3f} ms`",
                f"- ZPE mean MPJPE: `{contactpose['aggregate']['zpe']['mpjpe_mm_mean']:.3f} mm`",
                f"- Photon mean MPJPE: `{contactpose['aggregate']['photon']['mpjpe_mm_mean']:.3f} mm`",
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
        conclusions.append("ZPE-XR is smaller than the Photon articulation proxy on synthetic bytes/frame, which would contradict the published byte budget and needs scrutiny.")
    else:
        conclusions.append("Photon remains smaller on bytes/frame than ZPE-XR because the articulation proxy meters only the 19-byte-per-hand finger stream.")
    if synthetic["relative"]["zpe_lower_latency"]:
        conclusions.append("ZPE-XR has lower measured synthetic latency than the local Photon articulation proxy on this Mac.")
    else:
        conclusions.append("The local Photon articulation proxy has lower or equal measured synthetic latency on this Mac.")
    if contactpose.get("status") == "executed":
        conclusions.append(
            "Photon is now a same-machine proxy-measured incumbent row rather than a doc-only transport placeholder."
        )
        if contactpose["aggregate"]["zpe_lower_mpjpe_on_mean"]:
            conclusions.append("ZPE-XR retains lower mean ContactPose MPJPE than the local Photon articulation proxy.")
        else:
            conclusions.append("The local Photon articulation proxy reaches lower or equal mean ContactPose MPJPE, which would need deeper scrutiny.")
    conclusions.append(
        "This Phase 08 row stays narrower than the frozen full-position stream because shared per-frame hand-root pose remains outside the metered payload."
    )
    return conclusions
