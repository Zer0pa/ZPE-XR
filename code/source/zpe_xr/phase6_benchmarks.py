"""Mac-local comparator benchmark helpers for Phase 6."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import platform
import struct
from time import perf_counter_ns
from typing import Any, Iterable, Mapping, Sequence
import zlib

import numpy as np

from .api import codec_info, decode, encode
from .comparator_catalog import (
    MODERN_PROXY_COMPARATOR_ID,
    MODERN_PROXY_LABEL,
    market_reference_only_rows,
)
from .constants import FPS, RAW_BYTES_PER_FRAME, TOTAL_JOINTS
from .codec import XRCodec
from .external_benchmarks import (
    ComparatorMeasurement,
    bytes_per_frame_to_kbytes_per_second,
    photon_fusion_full_quaternion_measurement,
    photon_fusion_measurement,
    ultraleap_vectorhand_measurement,
)
from .io_utils import sha256_of_file
from .metrics import mpjpe_mm, percentile
from .outward_workload import (
    CONTACTPOSE_SAMPLE_FILENAME,
    ensure_contactpose_sample,
    evaluate_contactpose_multi_sequence_workload,
)
from .runtime_paths import canonical_root
from .synthetic import generate_sequence

_HALF_STRUCT = struct.Struct("<e")
_FLOAT_STRUCT = struct.Struct("<f")
_CONTACTPOSE_OBJECTS = ("mug", "wine_glass", "bowl", "camera", "binoculars")
_REQUIRED_ROOT_MODULES = (
    "constants.py",
    "codec.py",
    "io_utils.py",
    "metrics.py",
    "models.py",
    "pipeline.py",
    "synthetic.py",
)


def host_metadata() -> dict[str, object]:
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
    }


def benchmark_environment(stage_code_root: Path) -> dict[str, object]:
    root = canonical_root(stage_code_root)
    root_package_dir = root / "src" / "zpe_xr"
    missing_root_modules = [
        name for name in _REQUIRED_ROOT_MODULES if not (root_package_dir / name).exists()
    ]
    return {
        "stage_code_root": str(stage_code_root),
        "canonical_root": str(root),
        "root_package_dir": str(root_package_dir),
        "root_execution_surface": {
            "status": "runnable" if not missing_root_modules else "incomplete",
            "missing_modules": missing_root_modules,
        },
        "staged_package_backend": codec_info().get("backend"),
    }


def build_synthetic_frames(
    *,
    num_frames: int,
    gesture: str,
    seed: int,
) -> tuple[object, ...]:
    if num_frames <= 0:
        return ()
    return generate_sequence(num_frames=num_frames, gesture=gesture, seed=seed)


def benchmark_report(
    *,
    stage_code_root: Path,
    num_frames: int,
    gesture: str,
    seed: int,
    iterations: int,
    attempt_contactpose: bool,
) -> dict[str, object]:
    frames = build_synthetic_frames(num_frames=num_frames, gesture=gesture, seed=seed)
    rows = [
        measure_zpe_api_row(frames=frames, iterations=iterations),
        measure_raw_proxy_row(frames=frames, iterations=iterations),
        measure_modern_proxy_row(frames=frames, iterations=iterations),
        build_transport_only_row(
            photon_fusion_measurement(),
            evidence_class="doc_derived_transport_only",
            num_frames=len(frames),
        ),
        build_transport_only_row(
            photon_fusion_full_quaternion_measurement(),
            evidence_class="doc_derived_transport_only",
            num_frames=len(frames),
        ),
        build_transport_only_row(
            ultraleap_vectorhand_measurement(),
            evidence_class="code_derived_transport_only",
            num_frames=len(frames),
        ),
    ]
    zpe_row = rows[0]
    return {
        "host": host_metadata(),
        "execution_surface": benchmark_environment(stage_code_root),
        "workload": {
            "kind": "synthetic_frozen_v1",
            "frames": num_frames,
            "gesture": gesture,
            "seed": seed,
            "fps": FPS,
            "iterations": iterations,
        },
        "rows": rows,
        "market_reference_only": list(market_reference_only_rows()),
        "contactpose_attempt": (
            attempt_contactpose_report(stage_code_root) if attempt_contactpose else {"status": "skipped"}
        ),
        "conclusions": build_conclusions(rows, zpe_row=zpe_row),
        "unresolved": [
            "Photon remains transport-only in this phase; no same-machine runtime benchmark closes displacement.",
            "Ultraleap remains the strongest close-semantics open transport row, but it is still code-derived here rather than locally executed.",
            "Unity NGO and Normcore remain market references only until a runnable same-machine hand-sync benchmark is added inside this folder.",
            "The canonical root execution surface is still incomplete if required root package modules remain missing.",
        ],
    }


def measure_zpe_api_row(*, frames: Sequence[object], iterations: int) -> dict[str, object]:
    if not frames:
        info = codec_info()
        return {
            "comparator_id": "zpe_xr_current_mac",
            "label": "ZPE-XR staged package (local Mac)",
            "evidence_class": "measured_local",
            "fairness_class": "frozen_v1_authority_surface",
            "semantics": "Two hands, 26 joints per hand, deterministic keyframe+delta transport through the staged package API.",
            "source_reference": "local_staged_package_api",
            "notes": f"Measured from the staged package API on this Mac with backend={info.get('backend')}.",
            "transport": _transport_metrics(bytes_total=0, num_frames=0),
            "latency": _latency_metrics(encode_ns=(), decode_ns=(), num_frames=0),
            "fidelity": {"mpjpe_mm": 0.0},
            "backend": info.get("backend"),
        }

    positions = np.asarray([frame.positions for frame in frames], dtype=np.float32)
    reference_positions = positions.tolist()
    info = codec_info()
    encode_ns: list[int] = []
    decode_ns: list[int] = []
    payload: bytes = b""
    decoded = positions

    for _ in range(iterations):
        t0 = perf_counter_ns()
        payload = encode(positions, frame_rate=FPS)
        t1 = perf_counter_ns()
        decoded = decode(payload)
        t2 = perf_counter_ns()
        encode_ns.append(t1 - t0)
        decode_ns.append(t2 - t1)

    bytes_total = len(payload)
    num_frames = len(frames)
    transport = _transport_metrics(bytes_total=bytes_total, num_frames=num_frames)
    fidelity = {
        "mpjpe_mm": mpjpe_mm(reference_positions, decoded.tolist()),
    }
    latency = _latency_metrics(encode_ns=encode_ns, decode_ns=decode_ns, num_frames=num_frames)
    return {
        "comparator_id": "zpe_xr_current_mac",
        "label": "ZPE-XR staged package (local Mac)",
        "evidence_class": "measured_local",
        "fairness_class": "frozen_v1_authority_surface",
        "semantics": "Two hands, 26 joints per hand, deterministic keyframe+delta transport through the staged package API.",
        "source_reference": "local_staged_package_api",
        "notes": f"Measured from the staged package API on this Mac with backend={info.get('backend')}.",
        "transport": transport,
        "latency": latency,
        "fidelity": fidelity,
        "backend": info.get("backend"),
    }


def measure_raw_proxy_row(*, frames: Sequence[object], iterations: int) -> dict[str, object]:
    if not frames:
        return {
            "comparator_id": "raw_openxr_float_stream_local",
            "label": "Raw OpenXR-like float stream (local proxy)",
            "evidence_class": "proxy_measured_local",
            "fairness_class": "frozen_v1_authority_surface",
            "semantics": "Two hands, 26 joints per hand, position xyz plus quaternion xyzw as float32.",
            "source_reference": "local_proxy_measurement",
            "notes": "Measured locally by serializing the full float32 position+rotation stream.",
            "transport": _transport_metrics(bytes_total=0, num_frames=0),
            "latency": _latency_metrics(encode_ns=(), decode_ns=(), num_frames=0),
            "fidelity": {"mpjpe_mm": 0.0},
        }

    positions = np.asarray([frame.positions for frame in frames], dtype=np.float32)
    rotations = np.asarray([frame.rotations for frame in frames], dtype=np.float32)
    combined = np.concatenate((positions, rotations), axis=2).astype(np.float32, copy=False)

    encode_ns: list[int] = []
    decode_ns: list[int] = []
    payload = b""
    decoded_positions = positions

    for _ in range(iterations):
        t0 = perf_counter_ns()
        payload = combined.tobytes(order="C")
        t1 = perf_counter_ns()
        decoded = np.frombuffer(payload, dtype=np.float32).reshape(len(frames), TOTAL_JOINTS, 7)
        decoded_positions = decoded[:, :, :3].copy()
        t2 = perf_counter_ns()
        encode_ns.append(t1 - t0)
        decode_ns.append(t2 - t1)

    return {
        "comparator_id": "raw_openxr_float_stream_local",
        "label": "Raw OpenXR-like float stream (local proxy)",
        "evidence_class": "proxy_measured_local",
        "fairness_class": "frozen_v1_authority_surface",
        "semantics": "Two hands, 26 joints per hand, position xyz plus quaternion xyzw as float32.",
        "source_reference": "local_proxy_measurement",
        "notes": "Measured locally by serializing the full float32 position+rotation stream.",
        "transport": _transport_metrics(bytes_total=len(payload), num_frames=len(frames)),
        "latency": _latency_metrics(encode_ns=encode_ns, decode_ns=decode_ns, num_frames=len(frames)),
        "fidelity": {"mpjpe_mm": mpjpe_mm(positions.tolist(), decoded_positions.tolist())},
    }


def measure_modern_proxy_row(*, frames: Sequence[object], iterations: int) -> dict[str, object]:
    if not frames:
        return {
            "comparator_id": MODERN_PROXY_COMPARATOR_ID,
            "label": MODERN_PROXY_LABEL,
            "evidence_class": "proxy_measured_local",
            "fairness_class": "frozen_v1_authority_surface",
            "semantics": "Two hands, half-float positional deltas plus half-float rotations with zlib compression.",
            "source_reference": "local_proxy_measurement",
            "notes": "Measured locally with the same transport model used by the repo's frozen modern comparator row.",
            "transport": _transport_metrics(bytes_total=0, num_frames=0),
            "latency": _latency_metrics(encode_ns=(), decode_ns=(), num_frames=0),
            "fidelity": {"mpjpe_mm": 0.0},
        }

    encode_ns: list[int] = []
    decode_ns: list[int] = []
    packets: list[bytes] = []
    decoded_positions: list[list[tuple[float, float, float]]] = []

    for _ in range(iterations):
        t0 = perf_counter_ns()
        packets = _modern_proxy_encode_packets(frames)
        t1 = perf_counter_ns()
        decoded_positions = _modern_proxy_decode_packets(packets)
        t2 = perf_counter_ns()
        encode_ns.append(t1 - t0)
        decode_ns.append(t2 - t1)

    total_bytes = sum(len(packet) for packet in packets)
    reference_positions = [[tuple(joint) for joint in frame.positions] for frame in frames]
    return {
        "comparator_id": MODERN_PROXY_COMPARATOR_ID,
        "label": MODERN_PROXY_LABEL,
        "evidence_class": "proxy_measured_local",
        "fairness_class": "frozen_v1_authority_surface",
        "semantics": "Two hands, half-float positional deltas plus half-float rotations with zlib compression.",
        "source_reference": "local_proxy_measurement",
        "notes": "Measured locally with the same transport model used by the repo's frozen modern comparator row.",
        "transport": _transport_metrics(bytes_total=total_bytes, num_frames=len(frames)),
        "latency": _latency_metrics(encode_ns=encode_ns, decode_ns=decode_ns, num_frames=len(frames)),
        "fidelity": {"mpjpe_mm": mpjpe_mm(reference_positions, decoded_positions)},
    }


def build_transport_only_row(
    measurement: ComparatorMeasurement,
    *,
    evidence_class: str,
    num_frames: int,
) -> dict[str, object]:
    bytes_total = int(round(measurement.bytes_per_frame * num_frames))
    transport = _transport_metrics(bytes_total=bytes_total, num_frames=num_frames)
    transport["bytes_per_frame"] = measurement.bytes_per_frame
    transport["bytes_total"] = float(measurement.bytes_per_frame * num_frames)
    return {
        "comparator_id": measurement.comparator_id,
        "label": measurement.label,
        "evidence_class": evidence_class,
        "fairness_class": measurement.fairness_class,
        "semantics": measurement.semantics,
        "source_reference": measurement.source_reference,
        "notes": measurement.notes,
        "transport": transport,
        "latency": None,
        "fidelity": None,
    }


def attempt_contactpose_report(stage_code_root: Path) -> dict[str, object]:
    try:
        search_root = stage_code_root.parent.parent / "artifacts"
        destination = (
            stage_code_root.parent / "proofs" / "artifacts" / "phase6_contactpose_probe" / "downloads" / CONTACTPOSE_SAMPLE_FILENAME
        )
        codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)
        sample_zip = ensure_contactpose_sample(destination, search_root=search_root)
        benchmark = evaluate_contactpose_multi_sequence_workload(
            sample_zip,
            codec=codec,
            object_names=_CONTACTPOSE_OBJECTS,
        )
        return {
            "status": "executed",
            "source_path": str(sample_zip),
            "source_sha256": sha256_of_file(sample_zip),
            "aggregate": benchmark["aggregate"],
            "selected_objects": benchmark["workload"]["selected_objects"],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "blocked",
            "reason": str(exc),
            "error_type": type(exc).__name__,
        }


def render_markdown(report: Mapping[str, object]) -> str:
    rows = report["rows"]
    lines = [
        "# Phase 6 Mac Comparator Benchmark",
        "",
        "## Host",
        "",
        f"- platform: `{report['host']['platform']} {report['host']['platform_release']}`",
        f"- machine: `{report['host']['machine']}`",
        f"- python: `{report['host']['python_version']}`",
        "",
        "## Execution Surface",
        "",
        f"- canonical root: `{report['execution_surface']['canonical_root']}`",
        f"- root execution surface: `{report['execution_surface']['root_execution_surface']['status']}`",
        f"- staged backend: `{report['execution_surface']['staged_package_backend']}`",
        "",
        "## Workload",
        "",
        f"- kind: `{report['workload']['kind']}`",
        f"- frames: `{report['workload']['frames']}`",
        f"- gesture: `{report['workload']['gesture']}`",
        f"- seed: `{report['workload']['seed']}`",
        f"- iterations: `{report['workload']['iterations']}`",
        "",
        "## Comparator Matrix",
        "",
        "| Comparator | Evidence | Bytes/frame | Compression vs raw | 4-player KB/s @90 | Encode avg ms/frame | Decode avg ms/frame | MPJPE mm |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        transport = row["transport"]
        latency = row["latency"]
        fidelity = row["fidelity"]
        lines.append(
            "| "
            f"{row['label']} | "
            f"{row['evidence_class']} | "
            f"{transport['bytes_per_frame']:.3f} | "
            f"{transport['compression_ratio_vs_raw']:.3f}x | "
            f"{transport['kb_per_s_modeled_4_player_session']:.3f} | "
            f"{_md_value(latency, 'encode_avg_ms_per_frame')} | "
            f"{_md_value(latency, 'decode_avg_ms_per_frame')} | "
            f"{_md_value(fidelity, 'mpjpe_mm')} |"
        )

    lines.extend(
        [
            "",
            "## Market References Without Numeric Rows",
            "",
        ]
    )
    for row in report["market_reference_only"]:
        lines.append(f"- `{row['label']}`: {row['notes']} Source: `{row['source_reference']}`")

    lines.extend(["", "## ContactPose Attempt", ""])
    contactpose = report["contactpose_attempt"]
    if contactpose["status"] == "executed":
        aggregate = contactpose["aggregate"]
        lines.extend(
            [
                f"- status: `{contactpose['status']}`",
                f"- mean compression vs raw: `{aggregate['compression_ratio_vs_raw_mean']:.3f}x`",
                f"- mean MPJPE: `{aggregate['mpjpe_mm_mean']:.3f} mm`",
                f"- mean latency: `{aggregate['latency_ms_mean']:.3f} ms`",
                f"- modern comparator passes: `{aggregate['modern_comparator_pass_count']}/{aggregate['sequence_count']}`",
            ]
        )
    else:
        lines.append(f"- status: `{contactpose['status']}`")
        if contactpose["status"] == "blocked":
            lines.append(f"- reason: `{contactpose['error_type']}: {contactpose['reason']}`")

    lines.extend(["", "## Conclusions", ""])
    for conclusion in report["conclusions"]:
        lines.append(f"- {conclusion}")

    lines.extend(["", "## Unresolved", ""])
    for item in report["unresolved"]:
        lines.append(f"- {item}")

    return "\n".join(lines) + "\n"


def build_conclusions(rows: Sequence[Mapping[str, object]], *, zpe_row: Mapping[str, object]) -> list[str]:
    ultraleap = next(row for row in rows if row["comparator_id"] == "ultraleap_vectorhand_open_source")
    photon = next(row for row in rows if row["comparator_id"] == "photon_fusion_xr_hands_doc")
    conclusions = [
        "ZPE-XR now has a same-machine measured Mac row from the staged package surface.",
        "The raw float stream and the internal modern comparator proxy now have same-machine measured proxy rows, so local latency and overhead are no longer purely inherited from historical artifacts.",
    ]
    if zpe_row["transport"]["bytes_per_frame"] < ultraleap["transport"]["bytes_per_frame"]:
        conclusions.append("ZPE-XR is smaller than the code-derived Ultraleap VectorHand row on bytes/frame under the frozen two-hand stream semantics.")
    else:
        conclusions.append("ZPE-XR does not beat the code-derived Ultraleap VectorHand row on bytes/frame under the frozen two-hand stream semantics.")
    if zpe_row["transport"]["bytes_per_frame"] > photon["transport"]["bytes_per_frame"]:
        conclusions.append("Photon remains smaller on the documented compressed transport row, but that row is still narrower in semantics and not a closed head-to-head displacement result.")
    conclusions.append("Market-popular lanes such as Unity NGO and Normcore still need a runnable same-machine benchmark before they can enter the numeric comparison table.")
    return conclusions


def _transport_metrics(*, bytes_total: int, num_frames: int) -> dict[str, float]:
    if num_frames <= 0:
        return {
            "bytes_total": float(bytes_total),
            "bytes_per_frame": 0.0,
            "compression_ratio_vs_raw": 0.0,
            "kb_per_s_single_remote": 0.0,
            "kb_per_s_modeled_4_player_session": 0.0,
        }

    raw_total = RAW_BYTES_PER_FRAME * num_frames
    bytes_per_frame = bytes_total / num_frames
    return {
        "bytes_total": float(bytes_total),
        "bytes_per_frame": float(bytes_per_frame),
        "compression_ratio_vs_raw": float(raw_total / bytes_total) if bytes_total else 0.0,
        "kb_per_s_single_remote": bytes_per_frame_to_kbytes_per_second(bytes_per_frame, fps=FPS, remote_players=1),
        "kb_per_s_modeled_4_player_session": bytes_per_frame_to_kbytes_per_second(
            bytes_per_frame,
            fps=FPS,
            remote_players=3,
        ),
    }


def _latency_metrics(
    *,
    encode_ns: Sequence[int],
    decode_ns: Sequence[int],
    num_frames: int,
) -> dict[str, float]:
    iterations = min(len(encode_ns), len(decode_ns))
    if num_frames <= 0 or iterations <= 0:
        return _zero_latency_metrics()

    encode_ms = [value / 1_000_000.0 for value in encode_ns[:iterations]]
    decode_ms = [value / 1_000_000.0 for value in decode_ns[:iterations]]
    combined_ms = [enc + dec for enc, dec in zip(encode_ms, decode_ms)]
    return {
        "iterations": float(iterations),
        "encode_avg_ms_per_sequence": _avg(encode_ms),
        "encode_p50_ms_per_sequence": percentile(encode_ms, 50),
        "encode_p95_ms_per_sequence": percentile(encode_ms, 95),
        "encode_p99_ms_per_sequence": percentile(encode_ms, 99),
        "decode_avg_ms_per_sequence": _avg(decode_ms),
        "decode_p50_ms_per_sequence": percentile(decode_ms, 50),
        "decode_p95_ms_per_sequence": percentile(decode_ms, 95),
        "decode_p99_ms_per_sequence": percentile(decode_ms, 99),
        "combined_avg_ms_per_sequence": _avg(combined_ms),
        "combined_p50_ms_per_sequence": percentile(combined_ms, 50),
        "combined_p95_ms_per_sequence": percentile(combined_ms, 95),
        "combined_p99_ms_per_sequence": percentile(combined_ms, 99),
        "encode_avg_ms_per_frame": _avg(encode_ms) / num_frames,
        "decode_avg_ms_per_frame": _avg(decode_ms) / num_frames,
        "combined_avg_ms_per_frame": _avg(combined_ms) / num_frames,
        "combined_p95_ms_per_frame": percentile(combined_ms, 95) / num_frames,
        "combined_p99_ms_per_frame": percentile(combined_ms, 99) / num_frames,
    }


def _zero_latency_metrics() -> dict[str, float]:
    return {
        "iterations": 0.0,
        "encode_avg_ms_per_sequence": 0.0,
        "encode_p50_ms_per_sequence": 0.0,
        "encode_p95_ms_per_sequence": 0.0,
        "encode_p99_ms_per_sequence": 0.0,
        "decode_avg_ms_per_sequence": 0.0,
        "decode_p50_ms_per_sequence": 0.0,
        "decode_p95_ms_per_sequence": 0.0,
        "decode_p99_ms_per_sequence": 0.0,
        "combined_avg_ms_per_sequence": 0.0,
        "combined_p50_ms_per_sequence": 0.0,
        "combined_p95_ms_per_sequence": 0.0,
        "combined_p99_ms_per_sequence": 0.0,
        "encode_avg_ms_per_frame": 0.0,
        "decode_avg_ms_per_frame": 0.0,
        "combined_avg_ms_per_frame": 0.0,
        "combined_p95_ms_per_frame": 0.0,
        "combined_p99_ms_per_frame": 0.0,
    }


def _modern_proxy_encode_packets(frames: Sequence[object]) -> list[bytes]:
    packets: list[bytes] = []
    prev_positions: Sequence[tuple[float, float, float]] | None = None

    for frame in frames:
        payload = bytearray()
        for idx, (x, y, z) in enumerate(frame.positions):
            if prev_positions is None:
                dx, dy, dz = x, y, z
            else:
                px, py, pz = prev_positions[idx]
                dx, dy, dz = x - px, y - py, z - pz
            payload.extend(_HALF_STRUCT.pack(dx))
            payload.extend(_HALF_STRUCT.pack(dy))
            payload.extend(_HALF_STRUCT.pack(dz))
        for rx, ry, rz, rw in frame.rotations:
            payload.extend(_HALF_STRUCT.pack(rx))
            payload.extend(_HALF_STRUCT.pack(ry))
            payload.extend(_HALF_STRUCT.pack(rz))
            payload.extend(_HALF_STRUCT.pack(rw))
        packets.append(zlib.compress(bytes(payload), level=6))
        prev_positions = frame.positions
    return packets


def _modern_proxy_decode_packets(packets: Sequence[bytes]) -> list[list[tuple[float, float, float]]]:
    decoded_frames: list[list[tuple[float, float, float]]] = []
    prev_positions: list[tuple[float, float, float]] | None = None
    rotation_block_bytes = TOTAL_JOINTS * 4 * _HALF_STRUCT.size

    for packet in packets:
        payload = zlib.decompress(packet)
        offset = 0
        frame_positions: list[tuple[float, float, float]] = []
        for idx in range(TOTAL_JOINTS):
            dx = _HALF_STRUCT.unpack(payload[offset : offset + _HALF_STRUCT.size])[0]
            offset += _HALF_STRUCT.size
            dy = _HALF_STRUCT.unpack(payload[offset : offset + _HALF_STRUCT.size])[0]
            offset += _HALF_STRUCT.size
            dz = _HALF_STRUCT.unpack(payload[offset : offset + _HALF_STRUCT.size])[0]
            offset += _HALF_STRUCT.size
            if prev_positions is None:
                frame_positions.append((dx, dy, dz))
            else:
                px, py, pz = prev_positions[idx]
                frame_positions.append((px + dx, py + dy, pz + dz))
        offset += rotation_block_bytes
        if offset != len(payload):
            raise ValueError("modern proxy payload length mismatch")
        decoded_frames.append(frame_positions)
        prev_positions = frame_positions
    return decoded_frames


def _avg(values: Iterable[float]) -> float:
    values = tuple(values)
    return sum(values) / len(values) if values else 0.0


def _md_value(payload: Mapping[str, float] | None, key: str) -> str:
    if payload is None:
        return "—"
    return f"{payload[key]:.6f}"
