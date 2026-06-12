"""Denominator-clean benchmark accounting for Phase 4."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import time
from typing import Any, Iterable, Mapping, Sequence
import zlib

import numpy as np

from ._stream import pack_packets
from .codec import XRCodec
from .constants import FPS, JOINTS_PER_HAND, TOTAL_JOINTS
from .embodiment_record import (
    EMBODIMENT_RECORD_SCHEMA,
    REAL_HEADSET_CAPTURE_SCHEMA,
    validate_embodiment_record,
)
from .external_benchmarks import photon_fusion_measurement, ultraleap_vectorhand_measurement
from .metadata import KERNEL, VERSION
from .metrics import mpjpe_mm, percentile, pose_error_percent
from .models import Frame
from .network import (
    decode_diagnostics,
    decode_sequence,
    decode_with_realtime_recovery,
    encode_sequence,
    simulate_realtime_packet_map,
)
from .synthetic import generate_sequence

DENOMINATOR_BASELINE_SCHEMA = "zpe-xr-denominator-baseline-1"
PHASE4_GENERATED_AT_UTC = "2026-06-12T00:00:00+00:00"
DEFAULT_FRAMES_PER_SEGMENT = 12
DEFAULT_SEED = 4104
FLOAT32_BYTES = 4
FLOAT16_BYTES = 2
OPENXR_LOCATION_FLAGS_BYTES = 8
OPENXR_RADIUS_BYTES = 4
RAW_21_JOINTS = 21

SEGMENT_ORDER = (
    "static_hold",
    "slow_manipulation",
    "active_reaching",
    "fast_translation",
    "pointing",
    "grasp_release",
    "occlusion_jitter",
    "hand_controller_transition_or_tracking_loss",
)

REQUIRED_MEASURED_ROW_IDS = frozenset(
    {
        "raw_26xyz",
        "raw_26xyzquat",
        "raw_openxr_like_location",
        "float16_zlib_xyz",
        "float16_zlib_xyzquat",
        "zpe_stream_container",
        "zpe_packet_stream",
        "zpe_embodiment_record",
        "photon_xrhands_proxy",
        "ultraleap_vectorhand_proxy",
    }
)


class DenominatorReportValidationError(ValueError):
    """Raised when a Phase 4 benchmark report hides required denominator accounting."""


@dataclass(frozen=True)
class PacketMeasurements:
    packets: tuple[bytes, ...]
    stream: bytes
    encode_ms: float
    decode_ms: float
    decoded_positions: list[list[tuple[float, float, float]]]
    replay_digest_sha256: str
    byte_identical_replay: bool


def build_denominator_report(
    *,
    frames_per_segment: int = DEFAULT_FRAMES_PER_SEGMENT,
    seed: int = DEFAULT_SEED,
    evidence_class: str = "synthetic_openxr_fixture",
    native_capture_status: str = "not_applicable",
) -> dict[str, Any]:
    """Build a deterministic in-silico report with segment-level denominator rows."""

    if frames_per_segment <= 0:
        raise ValueError("frames_per_segment must be > 0")

    report_segments: list[dict[str, Any]] = []
    for segment_index, segment_id in enumerate(SEGMENT_ORDER):
        frames = _segment_frames(
            segment_id=segment_id,
            frames_per_segment=frames_per_segment,
            seed=seed + segment_index * 97,
        )
        report_segments.append(
            _build_segment_report(
                segment_id=segment_id,
                segment_index=segment_index,
                frames=frames,
                evidence_class=evidence_class,
                native_capture_status=native_capture_status,
            )
        )

    report: dict[str, Any] = {
        "schema": DENOMINATOR_BASELINE_SCHEMA,
        "artifact_class": "phase4_denominator_clean_benchmark",
        "generated_at_utc": PHASE4_GENERATED_AT_UTC,
        "phase": "04",
        "evidence_class": evidence_class,
        "native_capture_status": native_capture_status,
        "native_capture_claim": False,
        "source_policy": {
            "source": "deterministic synthetic OpenXR-shaped fixture",
            "native_authority": "not_satisfied",
            "phase5_native_capture": "pending",
            "surrogate_allowed_for": [
                "denominator logic",
                "baseline mechanics",
                "record overhead accounting",
                "replay digest accounting",
                "fail-closed validation",
            ],
            "surrogate_forbidden_for": [
                "native headset capture",
                "provider runtime latency",
                "commercial authority",
                "novelty pass",
            ],
        },
        "orientation_policy": {
            "source_orientation_exists": True,
            "zpe_packet_orientation_policy": "omitted_position_only_codec",
            "full_pose_denominators_required": True,
        },
        "sampling": {
            "sample_rate_hz": FPS,
            "frames_per_segment": frames_per_segment,
            "segment_count": len(report_segments),
        },
        "segments": report_segments,
        "aggregate": _aggregate_segments(report_segments),
        "aggregate_only": False,
        "fail_closed_policy": {
            "ratio_without_denominator": "invalid",
            "surrogate_native_claim": "invalid",
            "crc32_provenance": "invalid",
            "aggregate_only": "invalid",
            "xyz_xyzquat_denominator_mixing": "invalid",
            "adaptive_hybrid_unseparated_bytes": "invalid",
        },
    }
    validate_denominator_report(report)
    return report


def validate_denominator_report(report: Mapping[str, Any]) -> None:
    """Fail closed on denominator, provenance, native-claim, and aggregate-only drift."""

    if report.get("schema") != DENOMINATOR_BASELINE_SCHEMA:
        _fail("schema", f"must be {DENOMINATOR_BASELINE_SCHEMA!r}")

    evidence_class = str(report.get("evidence_class", ""))
    native_status = str(report.get("native_capture_status", ""))
    if report.get("native_capture_claim") is True and (
        evidence_class != "native_device_capture" or native_status != "native_verified"
    ):
        _fail("native_capture_claim", "surrogate or proxy records cannot claim native_capture")

    segments = report.get("segments")
    if not isinstance(segments, Sequence) or isinstance(segments, (str, bytes)) or not segments:
        _fail("segments", "aggregate-only report is invalid")
    if report.get("aggregate_only") is True:
        _fail("aggregate_only", "aggregate-only report is invalid")

    for segment_index, segment_obj in enumerate(segments):
        if not isinstance(segment_obj, Mapping):
            _fail(f"segments[{segment_index}]", "must be an object")
        _validate_segment(segment_obj, segment_index)


def render_denominator_report_markdown(report: Mapping[str, Any]) -> str:
    """Render a compact human-readable receipt from a validated report."""

    validate_denominator_report(report)
    lines = [
        "# Phase 4 Denominator-Clean Benchmark",
        "",
        f"Schema: `{report['schema']}`",
        f"Evidence class: `{report['evidence_class']}`",
        f"Native capture status: `{report['native_capture_status']}`",
        "Native capture claim: `false`",
        "",
        "This is in-silico denominator pressure only. It does not satisfy native headset capture.",
        "",
        "## Segment Rows",
        "",
        "| Segment | Row | Status | Bytes/frame | Total bytes | Denominator |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for segment in report["segments"]:
        for row in segment["denominator_rows"]:
            denominator = row.get("denominator", {})
            denom_label = denominator.get("layout") or denominator.get("policy") or "not_available"
            lines.append(
                "| {segment} | `{row_id}` | {status} | {bpf} | {total} | {denom} |".format(
                    segment=segment["segment_id"],
                    row_id=row["id"],
                    status=row["status"],
                    bpf=_fmt(row.get("bytes_per_frame")),
                    total=_fmt(row.get("bytes_total")),
                    denom=denom_label,
                )
            )

    lines.extend(
        [
            "",
            "## Aggregate Rows",
            "",
            "| Row | Status | Bytes/frame | Total bytes |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in report["aggregate"]["rows"]:
        lines.append(
            "| `{row_id}` | {status} | {bpf} | {total} |".format(
                row_id=row["id"],
                status=row["status"],
                bpf=_fmt(row.get("bytes_per_frame")),
                total=_fmt(row.get("bytes_total")),
            )
        )

    lines.extend(
        [
            "",
            "## Gate Consequence",
            "",
            "- Phase 4 status: denominator-clean measurement pressure exists for synthetic/proxy execution only.",
            "- Phase 5 native capture remains pending.",
            "- Adaptive-hybrid advantage remains unproved; the row is explicitly `not_available` until prior/session/residual bytes are separated.",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_segment_report(
    *,
    segment_id: str,
    segment_index: int,
    frames: tuple[Frame, ...],
    evidence_class: str,
    native_capture_status: str,
) -> dict[str, Any]:
    packet_measurements = _measure_packets(frames)
    positions = _positions_array(frames)
    rotations = _rotations_array(frames)
    frame_count = len(frames)
    ref_positions = [list(frame.positions) for frame in frames]
    error_stats = _error_stats_mm(ref_positions, packet_measurements.decoded_positions)
    loss_metrics = _loss_metrics(frames, packet_measurements.packets)
    packet_stats = _packet_diagnostics(packet_measurements.packets)
    record = _build_segment_embodiment_record(
        segment_id=segment_id,
        segment_index=segment_index,
        frames=frames,
        packet_measurements=packet_measurements,
        evidence_class=evidence_class,
        native_capture_status=native_capture_status,
    )
    validate_embodiment_record(record)
    record_components = _record_components(record, packet_measurements.stream, packet_measurements.packets)
    rows = [
        _raw_21xyz_row(frame_count),
        _raw_26xyz_row(frame_count),
        _raw_26xyzquat_row(frame_count),
        _raw_openxr_like_row(frame_count),
        _float16_zlib_row("float16_zlib_xyz", positions, frame_count, coordinate_channels="xyz"),
        _float16_zlib_row(
            "float16_zlib_xyzquat",
            np.concatenate([positions, rotations], axis=2),
            frame_count,
            coordinate_channels="xyzquat",
        ),
        _zpe_stream_container_row(frame_count, packet_measurements, packet_stats),
        _zpe_packet_stream_row(frame_count, packet_measurements, packet_stats),
        _zpe_record_row(frame_count, record_components),
        _photon_proxy_row(frame_count),
        _ultraleap_proxy_row(frame_count),
        _adaptive_hybrid_row(record_components),
    ]
    return {
        "segment_id": segment_id,
        "segment_index": segment_index,
        "frame_count": frame_count,
        "duration_s": frame_count / FPS,
        "sample_rate_hz": FPS,
        "motion_class_authority": "synthetic_surrogate_not_native",
        "denominator_rows": rows,
        "metrics": {
            "encode_ms_total": packet_measurements.encode_ms,
            "decode_ms_total": packet_measurements.decode_ms,
            "encode_decode_ms_total": packet_measurements.encode_ms + packet_measurements.decode_ms,
            "encode_decode_ms_per_frame": (packet_measurements.encode_ms + packet_measurements.decode_ms)
            / frame_count,
            "mpjpe_mm_mean": error_stats["mean"],
            "mpjpe_mm_p50": error_stats["p50"],
            "mpjpe_mm_p95": error_stats["p95"],
            "mpjpe_mm_p99": error_stats["p99"],
            "mpjpe_mm_max": error_stats["max"],
            "packet_loss_pose_error_pct": loss_metrics,
            "parse_failure_count": decode_diagnostics().get("parse_failures", 0),
            "byte_identical_replay_digest": packet_measurements.replay_digest_sha256,
            "byte_identical_replay": packet_measurements.byte_identical_replay,
            "phase_error_ms": None,
            "phase_error_policy": "not_available_for_synthetic_fixture",
        },
        "histograms": {
            "packet_size_bytes": _histogram([len(packet) for packet in packet_measurements.packets], bucket_size=16),
            "delta_magnitude_mm": packet_stats["delta_magnitude_histogram"],
        },
        "packet_diagnostics": packet_stats,
        "record_accounting": record_components,
    }


def _segment_frames(*, segment_id: str, frames_per_segment: int, seed: int) -> tuple[Frame, ...]:
    gesture_by_segment = {
        "static_hold": "spread",
        "slow_manipulation": "pinch",
        "active_reaching": "mixed",
        "fast_translation": "wave",
        "pointing": "point",
        "grasp_release": "grip",
        "occlusion_jitter": "mixed",
        "hand_controller_transition_or_tracking_loss": "fist",
    }
    return generate_sequence(
        num_frames=frames_per_segment,
        seed=seed,
        gesture=gesture_by_segment.get(segment_id, "mixed"),
    )


def _measure_packets(frames: Sequence[Frame]) -> PacketMeasurements:
    codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)
    encode_start = time.perf_counter()
    packets = tuple(encode_sequence(codec, frames))
    encode_ms = (time.perf_counter() - encode_start) * 1000.0
    stream = pack_packets(packets)

    decode_codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)
    decode_start = time.perf_counter()
    decoded_positions = decode_sequence(decode_codec, packets)
    decode_ms = (time.perf_counter() - decode_start) * 1000.0

    first_digest = _positions_digest(decoded_positions)
    decoded_again = decode_sequence(XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0), packets)
    second_digest = _positions_digest(decoded_again)
    return PacketMeasurements(
        packets=packets,
        stream=stream,
        encode_ms=encode_ms,
        decode_ms=decode_ms,
        decoded_positions=decoded_positions,
        replay_digest_sha256=first_digest,
        byte_identical_replay=first_digest == second_digest,
    )


def _positions_array(frames: Sequence[Frame]) -> np.ndarray:
    return np.asarray([[joint for joint in frame.positions] for frame in frames], dtype=np.float32)


def _rotations_array(frames: Sequence[Frame]) -> np.ndarray:
    return np.asarray([[joint for joint in frame.rotations] for frame in frames], dtype=np.float32)


def _float16_zlib_bytes(values: np.ndarray) -> int:
    payload = np.asarray(values, dtype=np.float16).tobytes()
    return len(zlib.compress(payload, level=9))


def _raw_21xyz_row(frame_count: int) -> dict[str, Any]:
    return {
        "id": "raw_21xyz",
        "status": "not_applicable",
        "bytes_total": None,
        "bytes_per_frame": None,
        "kbps_at_90hz": None,
        "denominator": {
            "policy": "not_applicable_for_26_joint_source_layout",
            "joint_count": RAW_21_JOINTS,
            "coordinate_channels": "xyz",
            "bytes_per_scalar": FLOAT32_BYTES,
        },
        "not_available_reason": "Phase 4 fixture is OpenXR/Unity-shaped 26 joints per hand; 21xyz is listed but not used for ratios.",
        "frame_count": frame_count,
    }


def _raw_26xyz_row(frame_count: int) -> dict[str, Any]:
    bytes_per_frame = TOTAL_JOINTS * 3 * FLOAT32_BYTES
    return _measured_row(
        row_id="raw_26xyz",
        bytes_total=bytes_per_frame * frame_count,
        frame_count=frame_count,
        denominator={
            "layout": "26 joints/hand x 2 hands x xyz float32",
            "joint_count": TOTAL_JOINTS,
            "joints_per_hand": JOINTS_PER_HAND,
            "coordinate_channels": "xyz",
            "scalars_per_joint": 3,
            "bytes_per_scalar": FLOAT32_BYTES,
            "orientation_included": False,
            "formula": "52 * 3 * 4",
        },
    )


def _raw_26xyzquat_row(frame_count: int) -> dict[str, Any]:
    bytes_per_frame = TOTAL_JOINTS * 7 * FLOAT32_BYTES
    return _measured_row(
        row_id="raw_26xyzquat",
        bytes_total=bytes_per_frame * frame_count,
        frame_count=frame_count,
        denominator={
            "layout": "26 joints/hand x 2 hands x xyz+quat float32",
            "joint_count": TOTAL_JOINTS,
            "joints_per_hand": JOINTS_PER_HAND,
            "coordinate_channels": "xyzquat",
            "scalars_per_joint": 7,
            "bytes_per_scalar": FLOAT32_BYTES,
            "orientation_included": True,
            "formula": "52 * (3 + 4) * 4",
        },
    )


def _raw_openxr_like_row(frame_count: int) -> dict[str, Any]:
    bytes_per_frame = TOTAL_JOINTS * (OPENXR_LOCATION_FLAGS_BYTES + 7 * FLOAT32_BYTES + OPENXR_RADIUS_BYTES)
    return _measured_row(
        row_id="raw_openxr_like_location",
        bytes_total=bytes_per_frame * frame_count,
        frame_count=frame_count,
        denominator={
            "layout": "OpenXR-like XrHandJointLocationEXT fields",
            "joint_count": TOTAL_JOINTS,
            "coordinate_channels": "flags_xyzquat_radius",
            "bytes_per_joint": OPENXR_LOCATION_FLAGS_BYTES + 7 * FLOAT32_BYTES + OPENXR_RADIUS_BYTES,
            "orientation_included": True,
            "formula": "52 * (8 byte flags + 7 float32 pose scalars + 4 byte radius)",
        },
    )


def _float16_zlib_row(
    row_id: str,
    values: np.ndarray,
    frame_count: int,
    *,
    coordinate_channels: str,
) -> dict[str, Any]:
    bytes_total = _float16_zlib_bytes(values)
    return _measured_row(
        row_id=row_id,
        bytes_total=bytes_total,
        frame_count=frame_count,
        denominator={
            "layout": f"26 joints/hand x 2 hands x {coordinate_channels} float16 zlib",
            "joint_count": TOTAL_JOINTS,
            "coordinate_channels": coordinate_channels,
            "bytes_per_scalar": FLOAT16_BYTES,
            "compression": "zlib_deflate_level_9",
            "orientation_included": coordinate_channels == "xyzquat",
            "uncompressed_float16_bytes": int(values.size * FLOAT16_BYTES),
        },
    )


def _zpe_stream_container_row(
    frame_count: int,
    measurements: PacketMeasurements,
    packet_stats: Mapping[str, Any],
) -> dict[str, Any]:
    return _measured_row(
        row_id="zpe_stream_container",
        bytes_total=len(measurements.stream),
        frame_count=frame_count,
        denominator={
            "layout": "ZXRS stream container wrapping ZPE packets",
            "coordinate_channels": "xyz",
            "orientation_included": False,
            "zpe_orientation_policy": "omitted_position_only_codec",
            "components": {
                "packet_payload_bytes": sum(len(packet) for packet in measurements.packets),
                "stream_container_overhead_bytes": len(measurements.stream)
                - sum(len(packet) for packet in measurements.packets),
                "packet_count": len(measurements.packets),
            },
        },
        extra={"packet_size_stats": packet_stats["packet_size_stats"]},
    )


def _zpe_packet_stream_row(
    frame_count: int,
    measurements: PacketMeasurements,
    packet_stats: Mapping[str, Any],
) -> dict[str, Any]:
    packet_bytes = sum(len(packet) for packet in measurements.packets)
    return _measured_row(
        row_id="zpe_packet_stream",
        bytes_total=packet_bytes,
        frame_count=frame_count,
        denominator={
            "layout": "ZPE packet payload bytes only",
            "coordinate_channels": "xyz",
            "orientation_included": False,
            "zpe_orientation_policy": "omitted_position_only_codec",
            "packet_count": len(measurements.packets),
        },
        extra={"packet_size_stats": packet_stats["packet_size_stats"]},
    )


def _zpe_record_row(frame_count: int, components: Mapping[str, Any]) -> dict[str, Any]:
    return _measured_row(
        row_id="zpe_embodiment_record",
        bytes_total=int(components["record_total_bytes"]),
        frame_count=frame_count,
        denominator={
            "layout": "EmbodimentRecord JSON plus ZXRS packet stream",
            "coordinate_channels": "xyz",
            "orientation_included": False,
            "zpe_orientation_policy": "record_preserves_orientation_policy_but_packet_codec_omits_orientation",
        },
        extra={"components": dict(components)},
    )


def _photon_proxy_row(frame_count: int) -> dict[str, Any]:
    measurement = photon_fusion_measurement()
    return _measured_row(
        row_id="photon_xrhands_proxy",
        bytes_total=int(round(measurement.bytes_per_frame * frame_count)),
        frame_count=frame_count,
        denominator={
            "layout": "Photon XR Hands doc-derived compressed rotations proxy",
            "coordinate_channels": "rotations_only_proxy",
            "orientation_included": True,
            "evidence_class": "proxy_not_runtime_measured",
            "source_reference": measurement.source_reference,
            "semantics": measurement.semantics,
        },
    )


def _ultraleap_proxy_row(frame_count: int) -> dict[str, Any]:
    measurement = ultraleap_vectorhand_measurement()
    return _measured_row(
        row_id="ultraleap_vectorhand_proxy",
        bytes_total=int(round(measurement.bytes_per_frame * frame_count)),
        frame_count=frame_count,
        denominator={
            "layout": "Ultraleap VectorHand open-source bytes proxy",
            "coordinate_channels": "palm_pose_plus_hand_local_positions_proxy",
            "orientation_included": True,
            "evidence_class": "proxy_not_runtime_measured",
            "source_reference": measurement.source_reference,
            "semantics": measurement.semantics,
        },
    )


def _adaptive_hybrid_row(components: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": "zpe_adaptive_hybrid",
        "status": "not_available",
        "bytes_total": None,
        "bytes_per_frame": None,
        "kbps_at_90hz": None,
        "prior_reference_bytes": None,
        "session_delta_bytes": None,
        "residual_stream_bytes": None,
        "record_metadata_bytes": int(components["record_overhead_bytes"]),
        "heldout_split_metadata": None,
        "phase_timing_metric": None,
        "denominator": {
            "policy": "not_available_until_prior_session_residual_bytes_are_separated",
            "coordinate_channels": "adaptive_hybrid",
        },
        "not_available_reason": (
            "Phase 4 installs the accounting hook only. No adaptive-hybrid row is claim-bearing "
            "until prior, session delta, and residual bytes are measured separately."
        ),
    }


def _measured_row(
    *,
    row_id: str,
    bytes_total: int,
    frame_count: int,
    denominator: Mapping[str, Any],
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    bytes_per_frame = bytes_total / frame_count
    row: dict[str, Any] = {
        "id": row_id,
        "status": "measured",
        "bytes_total": int(bytes_total),
        "bytes_per_frame": bytes_per_frame,
        "kbps_at_90hz": (bytes_per_frame * FPS * 8.0) / 1000.0,
        "frame_count": frame_count,
        "denominator": dict(denominator),
    }
    if extra:
        row.update(extra)
    return row


def _loss_metrics(frames: Sequence[Frame], packets: Sequence[bytes]) -> dict[str, Any]:
    reference = [list(frame.positions) for frame in frames]
    metrics: dict[str, Any] = {}
    for loss_rate in (0.05, 0.10, 0.20):
        packet_map = simulate_realtime_packet_map(
            packets,
            loss_rate=loss_rate,
            jitter_probability=0.0,
            max_delay_frames=0,
            seed=DEFAULT_SEED + int(loss_rate * 1000),
        )
        decoded, stats = decode_with_realtime_recovery(
            XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0),
            packet_map,
            total_frames=len(frames),
        )
        err_mm = mpjpe_mm(reference, decoded)
        key = f"{int(loss_rate * 100)}pct"
        metrics[key] = {
            "mpjpe_mm": err_mm,
            "pose_error_pct": pose_error_percent(err_mm, reference_span_mm=120.0),
            "provided_packets": stats["provided_packets"],
            "missing_packets": stats["missing_packets"],
            "parse_failures": decode_diagnostics().get("parse_failures", 0),
        }
    return metrics


def _error_stats_mm(
    reference_positions: Sequence[Sequence[tuple[float, float, float]]],
    predicted_positions: Sequence[Sequence[tuple[float, float, float]]],
) -> dict[str, float]:
    errors: list[float] = []
    for ref_frame, pred_frame in zip(reference_positions, predicted_positions):
        for (rx, ry, rz), (px, py, pz) in zip(ref_frame, pred_frame):
            errors.append(float(np.linalg.norm(np.asarray((rx - px, ry - py, rz - pz))) * 1000.0))
    return {
        "mean": float(sum(errors) / max(len(errors), 1)),
        "p50": percentile(errors, 50.0),
        "p95": percentile(errors, 95.0),
        "p99": percentile(errors, 99.0),
        "max": float(max(errors) if errors else 0.0),
    }


def _packet_diagnostics(packets: Sequence[bytes]) -> dict[str, Any]:
    codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)
    keyframe_count = 0
    current_entry_counts: list[int] = []
    delta_magnitudes: list[int] = []
    parse_failures = 0
    for packet in packets:
        try:
            parsed = codec.parse_packet(packet)
        except Exception:  # noqa: BLE001 - diagnostics must not hide validation failures.
            parse_failures += 1
            continue
        if parsed.is_keyframe:
            keyframe_count += 1
            current_entry_counts.append(TOTAL_JOINTS)
            continue
        current_entry_counts.append(len(parsed.current_entries))
        for _, dx, dy, dz in parsed.current_entries:
            delta_magnitudes.append(max(abs(dx), abs(dy), abs(dz)))

    packet_sizes = [len(packet) for packet in packets]
    scheduled_keyframes = sum(1 for seq in range(len(packets)) if seq % 45 == 0)
    total_joint_slots = max(len(packets) * TOTAL_JOINTS, 1)
    delta_entries = sum(current_entry_counts)
    return {
        "packet_size_stats": {
            "count": len(packet_sizes),
            "min_bytes": float(min(packet_sizes) if packet_sizes else 0),
            "max_bytes": float(max(packet_sizes) if packet_sizes else 0),
            "mean_bytes": float(sum(packet_sizes) / max(len(packet_sizes), 1)),
            "p95_bytes": percentile([float(size) for size in packet_sizes], 95.0),
        },
        "keyframe_count": keyframe_count,
        "scheduled_keyframe_count": scheduled_keyframes,
        "overflow_keyframe_count": max(keyframe_count - scheduled_keyframes, 0),
        "delta_entry_count_mean": float(delta_entries / max(len(packets), 1)),
        "active_joint_count_mean": float(delta_entries / max(len(packets), 1)),
        "deadband_skip_rate": float(max(total_joint_slots - delta_entries, 0) / total_joint_slots),
        "parse_failure_count": parse_failures,
        "delta_magnitude_histogram": _histogram(delta_magnitudes, bucket_size=4),
    }


def _build_segment_embodiment_record(
    *,
    segment_id: str,
    segment_index: int,
    frames: Sequence[Frame],
    packet_measurements: PacketMeasurements,
    evidence_class: str,
    native_capture_status: str,
) -> dict[str, Any]:
    stream_sha = sha256(packet_measurements.stream).hexdigest()
    packet_hash_chain = [sha256(packet).hexdigest() for packet in packet_measurements.packets]
    record = {
        "schema": EMBODIMENT_RECORD_SCHEMA,
        "record_id": f"phase4-{segment_index:02d}-{segment_id}",
        "created_at_utc": PHASE4_GENERATED_AT_UTC,
        "capture": _capture_manifest(evidence_class, native_capture_status),
        "source_license": {
            "name": "synthetic fixture; no external data license",
            "commercial_use": "not_applicable",
            "url": None,
        },
        "calibration_prior_policy": {
            "population_prior": "not_used_in_phase4_denominator_fixture",
            "session_delta": "not_used_in_phase4_denominator_fixture",
            "residual_stream": "zpe_packet_stream_position_only",
        },
        "frames": [_frame_summary(frame) for frame in frames],
        "packet_stream": {
            "encoding": "zpe_xr_packet_stream_v1",
            "packet_count": len(packet_measurements.packets),
            "packet_sha256": stream_sha,
            "transport_checksum_kind": "crc32",
            "transport_checksums": [
                f"{zlib.crc32(packet) & 0xFFFFFFFF:08x}" for packet in packet_measurements.packets
            ],
        },
        "provenance": {
            "record_digest_alg": "sha256",
            "record_digest_sha256": "0" * 64,
            "packet_hash_chain_alg": "sha256",
            "packet_hash_chain": packet_hash_chain,
        },
        "decoder": {
            "name": "zpe_xr",
            "version": VERSION,
            "kernel": KERNEL,
        },
        "replay": {
            "byte_identical_replay_required": True,
            "replay_digest_alg": "sha256",
            "replay_digest_sha256": packet_measurements.replay_digest_sha256,
            "renderer": "in_silico_decoder_no_runtime_renderer",
        },
        "privacy": {
            "biometric_fields": [
                "hand_joint_positions",
                "hand_joint_orientations",
                "calibration_prior_policy",
                "session_delta_policy",
            ],
            "calibration_window_retention": "not_collected_in_phase4_fixture",
            "session_delta_retention": "not_collected_in_phase4_fixture",
            "deletion_policy": "artifact deletion removes synthetic fixture and derived packet records",
            "external_sharing": "no external human capture data",
        },
    }
    record["provenance"]["record_digest_sha256"] = sha256(_compact_json_bytes(record)).hexdigest()
    return record


def _capture_manifest(evidence_class: str, native_capture_status: str) -> dict[str, Any]:
    return {
        "schema": REAL_HEADSET_CAPTURE_SCHEMA,
        "capture_id": "phase4-denominator-synthetic-openxr-fixture",
        "evidence_class": evidence_class,
        "native_capture_status": native_capture_status,
        "source": {
            "name": "zpe_xr.synthetic.generate_sequence",
            "capture_mode": "deterministic_in_silico_fixture",
            "dataset_id": None,
            "official_url": None,
        },
        "device_runtime": {
            "device_class": "synthetic_openxr_shape",
            "provider": "zpe_xr",
            "runtime": "python",
            "api": "openxr_ext_hand_tracking_shape",
            "sdk_version": None,
        },
        "joint_layout": {
            "standard": "openxr_ext_hand_tracking",
            "hands": ["left", "right"],
            "joints_per_hand": JOINTS_PER_HAND,
            "total_joints": TOTAL_JOINTS,
        },
        "timebase": {
            "sample_rate_hz": FPS,
            "source_timestamp_unit": "ns",
            "frame_index_base": 0,
        },
        "coordinate_frames": {
            "source_frame": "synthetic_world_meters",
            "storage_frame": "synthetic_world_meters",
            "units": "meters",
            "handedness": "right",
        },
        "motion_protocol": {
            "segments": [{"id": segment_id, "duration_s": DEFAULT_FRAMES_PER_SEGMENT / FPS} for segment_id in SEGMENT_ORDER]
        },
        "validity_flags": ["position_valid", "orientation_valid", "tracked"],
    }


def _frame_summary(frame: Frame) -> dict[str, Any]:
    return {
        "frame_index": frame.seq,
        "source_timestamp_ns": int(frame.timestamp_ms * 1_000_000),
        "hands": [
            {
                "handedness": "left",
                "joint_count": JOINTS_PER_HAND,
                "joint_validity_summary": {
                    "position_valid": JOINTS_PER_HAND,
                    "orientation_valid": JOINTS_PER_HAND,
                    "tracked": JOINTS_PER_HAND,
                },
            },
            {
                "handedness": "right",
                "joint_count": JOINTS_PER_HAND,
                "joint_validity_summary": {
                    "position_valid": JOINTS_PER_HAND,
                    "orientation_valid": JOINTS_PER_HAND,
                    "tracked": JOINTS_PER_HAND,
                },
            },
        ],
    }


def _record_components(
    record: Mapping[str, Any],
    packet_stream: bytes,
    packets: Sequence[bytes],
) -> dict[str, Any]:
    record_json_bytes = len(_compact_json_bytes(record))
    packet_payload_bytes = sum(len(packet) for packet in packets)
    packet_stream_container_bytes = len(packet_stream)
    provenance_overhead_bytes = len(_compact_json_bytes(record["provenance"]))
    packet_stream_metadata_bytes = len(_compact_json_bytes(record["packet_stream"]))
    record_total_bytes = record_json_bytes + packet_stream_container_bytes
    record_overhead_bytes = record_total_bytes - packet_stream_container_bytes
    return {
        "packet_payload_bytes": packet_payload_bytes,
        "packet_stream_container_bytes": packet_stream_container_bytes,
        "stream_container_overhead_bytes": packet_stream_container_bytes - packet_payload_bytes,
        "record_json_bytes": record_json_bytes,
        "record_total_bytes": record_total_bytes,
        "record_overhead_bytes": record_overhead_bytes,
        "packet_stream_metadata_bytes": packet_stream_metadata_bytes,
        "provenance_overhead_bytes": provenance_overhead_bytes,
        "record_metadata_overhead_bytes": record_overhead_bytes - packet_stream_metadata_bytes - provenance_overhead_bytes,
        "provenance_digest_alg": record["provenance"]["record_digest_alg"],
        "packet_hash_chain_alg": record["provenance"]["packet_hash_chain_alg"],
    }


def _aggregate_segments(segments: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rows_by_id: dict[str, list[Mapping[str, Any]]] = {}
    total_frames = 0
    for segment in segments:
        total_frames += int(segment["frame_count"])
        for row in segment["denominator_rows"]:
            rows_by_id.setdefault(str(row["id"]), []).append(row)

    aggregate_rows: list[dict[str, Any]] = []
    for row_id, rows in sorted(rows_by_id.items()):
        if all(row.get("status") == "not_available" or row.get("bytes_total") is None for row in rows):
            aggregate_rows.append(
                {
                    "id": row_id,
                    "status": rows[0]["status"],
                    "bytes_total": None,
                    "bytes_per_frame": None,
                    "kbps_at_90hz": None,
                }
            )
            continue
        bytes_total = sum(int(row["bytes_total"]) for row in rows if row.get("bytes_total") is not None)
        bytes_per_frame = bytes_total / total_frames
        aggregate_rows.append(
            {
                "id": row_id,
                "status": "measured",
                "bytes_total": bytes_total,
                "bytes_per_frame": bytes_per_frame,
                "kbps_at_90hz": (bytes_per_frame * FPS * 8.0) / 1000.0,
            }
        )

    return {
        "frame_count": total_frames,
        "segment_count": len(segments),
        "rows": aggregate_rows,
        "policy": "aggregate_is_supplemental_only_segment_rows_are_authority",
    }


def _validate_segment(segment: Mapping[str, Any], segment_index: int) -> None:
    rows = segment.get("denominator_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        _fail(f"segments[{segment_index}].denominator_rows", "must contain segment-level rows")

    row_by_id: dict[str, Mapping[str, Any]] = {}
    for row_index, row_obj in enumerate(rows):
        if not isinstance(row_obj, Mapping):
            _fail(f"segments[{segment_index}].denominator_rows[{row_index}]", "must be an object")
        row_id = str(row_obj.get("id", ""))
        row_by_id[row_id] = row_obj
        _validate_row(row_obj, segment_index, row_index)

    missing = REQUIRED_MEASURED_ROW_IDS - set(row_by_id)
    if missing:
        _fail(f"segments[{segment_index}].denominator_rows", f"missing required rows: {sorted(missing)}")
    _validate_record_overhead(row_by_id.get("zpe_embodiment_record"), segment_index)
    _validate_adaptive_row(row_by_id.get("zpe_adaptive_hybrid"), segment_index)
    _validate_ratio_denominators(row_by_id, segment_index)


def _validate_row(row: Mapping[str, Any], segment_index: int, row_index: int) -> None:
    path = f"segments[{segment_index}].denominator_rows[{row_index}]"
    row_id = str(row.get("id", ""))
    status = row.get("status")
    if not row_id:
        _fail(path, "row id is required")
    if status not in {"measured", "omitted", "not_applicable", "not_available"}:
        _fail(f"{path}.status", "unsupported row status")

    denominator = row.get("denominator")
    if not isinstance(denominator, Mapping):
        _fail(f"{path}.denominator", "denominator is required")

    if status == "measured":
        if row.get("bytes_total") is None or row.get("bytes_per_frame") is None:
            _fail(path, "measured rows require bytes_total and bytes_per_frame")
        if float(row["bytes_per_frame"]) <= 0:
            _fail(f"{path}.bytes_per_frame", "must be > 0")

    if ("ratio" in row or "compression_ratio" in row) and "ratio_denominator_id" not in row:
        _fail(path, "ratio without denominator is invalid")

    if row_id == "zpe_embodiment_record":
        components = row.get("components")
        if not isinstance(components, Mapping):
            _fail(f"{path}.components", "record row must separate packet and record overhead")
        if components.get("provenance_digest_alg") == "crc32" or components.get("packet_hash_chain_alg") == "crc32":
            _fail(f"{path}.components", "CRC32 provenance is invalid")


def _validate_record_overhead(row: Mapping[str, Any] | None, segment_index: int) -> None:
    if row is None:
        _fail(f"segments[{segment_index}].denominator_rows", "missing zpe_embodiment_record row")
    components = row.get("components")
    if not isinstance(components, Mapping):
        _fail(f"segments[{segment_index}].zpe_embodiment_record.components", "components are required")
    required = {
        "packet_payload_bytes",
        "packet_stream_container_bytes",
        "record_total_bytes",
        "record_overhead_bytes",
        "provenance_overhead_bytes",
    }
    missing = required - set(components)
    if missing:
        _fail(f"segments[{segment_index}].zpe_embodiment_record.components", f"missing {sorted(missing)}")
    if int(components["record_overhead_bytes"]) <= 0:
        _fail(f"segments[{segment_index}].zpe_embodiment_record.components", "record overhead must be > 0")
    expected_overhead = int(components["record_total_bytes"]) - int(components["packet_stream_container_bytes"])
    if int(components["record_overhead_bytes"]) != expected_overhead:
        _fail(f"segments[{segment_index}].zpe_embodiment_record.components", "record overhead arithmetic mismatch")


def _validate_adaptive_row(row: Mapping[str, Any] | None, segment_index: int) -> None:
    if row is None:
        return
    fields = {"prior_reference_bytes", "session_delta_bytes", "residual_stream_bytes", "record_metadata_bytes"}
    missing = fields - set(row)
    if missing:
        _fail(f"segments[{segment_index}].zpe_adaptive_hybrid", f"missing {sorted(missing)}")
    if row.get("status") == "not_available":
        if not row.get("not_available_reason"):
            _fail(f"segments[{segment_index}].zpe_adaptive_hybrid", "not_available rows require a reason")
        return
    for field in ("prior_reference_bytes", "session_delta_bytes", "residual_stream_bytes"):
        if row.get(field) is None:
            _fail(f"segments[{segment_index}].zpe_adaptive_hybrid.{field}", "must be separated or not_available")


def _validate_ratio_denominators(row_by_id: Mapping[str, Mapping[str, Any]], segment_index: int) -> None:
    for row_id, row in row_by_id.items():
        base_id = row.get("ratio_denominator_id")
        if base_id is None:
            continue
        base = row_by_id.get(str(base_id))
        if base is None:
            _fail(f"segments[{segment_index}].{row_id}.ratio_denominator_id", "unknown denominator row")
        channels = row.get("denominator", {}).get("coordinate_channels")
        base_channels = base.get("denominator", {}).get("coordinate_channels")
        if channels != base_channels:
            _fail(
                f"segments[{segment_index}].{row_id}.ratio_denominator_id",
                "xyz-vs-xyzquat denominator mixing is invalid",
            )


def _positions_digest(positions: Sequence[Sequence[tuple[float, float, float]]]) -> str:
    return sha256(np.asarray(positions, dtype=np.float32).tobytes()).hexdigest()


def _compact_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _histogram(values: Iterable[int], *, bucket_size: int) -> dict[str, int]:
    buckets: dict[str, int] = {}
    for value in values:
        low = (int(value) // bucket_size) * bucket_size
        high = low + bucket_size - 1
        buckets[f"{low}-{high}"] = buckets.get(f"{low}-{high}", 0) + 1
    return dict(sorted(buckets.items(), key=lambda item: int(item[0].split("-", 1)[0])))


def _fmt(value: Any) -> str:
    if value is None:
        return "not_available"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _fail(path: str, message: str) -> None:
    raise DenominatorReportValidationError(f"{path}: {message}")
