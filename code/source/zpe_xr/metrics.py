"""Evaluation metrics and comparator utilities."""

from __future__ import annotations

from hashlib import sha256
import math
import struct
from typing import Dict, Iterable, List, Sequence, Tuple
import zlib

from .constants import RAW_BYTES_PER_FRAME
from .models import Frame

_HALF_STRUCT = struct.Struct("<e")


def mpjpe_mm(
    reference_positions: Sequence[Sequence[Tuple[float, float, float]]],
    predicted_positions: Sequence[Sequence[Tuple[float, float, float]]],
) -> float:
    if len(reference_positions) != len(predicted_positions):
        raise ValueError("reference and predicted lengths differ")

    total_error_mm = 0.0
    total_points = 0

    for ref_frame, pred_frame in zip(reference_positions, predicted_positions):
        if len(ref_frame) != len(pred_frame):
            raise ValueError("joint counts differ")
        for (rx, ry, rz), (px, py, pz) in zip(ref_frame, pred_frame):
            dx = rx - px
            dy = ry - py
            dz = rz - pz
            total_error_mm += math.sqrt(dx * dx + dy * dy + dz * dz) * 1000.0
            total_points += 1

    return total_error_mm / max(total_points, 1)


def pose_error_percent(mpjpe_mm_value: float, reference_span_mm: float = 120.0) -> float:
    if reference_span_mm <= 0:
        raise ValueError("reference_span_mm must be > 0")
    return (mpjpe_mm_value / reference_span_mm) * 100.0


def packet_hash_digest(packets: Iterable[bytes]) -> str:
    hasher = sha256()
    for packet in packets:
        hasher.update(packet)
    return hasher.hexdigest()


def raw_stream_bytes(num_frames: int) -> int:
    return num_frames * RAW_BYTES_PER_FRAME


def packet_size_stats(packets: Sequence[bytes]) -> Dict[str, float]:
    sizes = [len(packet) for packet in packets]
    if not sizes:
        return {
            "count": 0,
            "min_bytes": 0,
            "max_bytes": 0,
            "avg_bytes": 0.0,
            "p95_bytes": 0.0,
        }

    sorted_sizes = sorted(sizes)
    p95_index = int(round(0.95 * (len(sorted_sizes) - 1)))
    return {
        "count": len(sizes),
        "min_bytes": float(sorted_sizes[0]),
        "max_bytes": float(sorted_sizes[-1]),
        "avg_bytes": sum(sizes) / len(sizes),
        "p95_bytes": float(sorted_sizes[p95_index]),
    }


def modern_comparator_packet_sizes(frames: Sequence[Frame]) -> List[int]:
    if not frames:
        return []

    prev_positions = None
    sizes: List[int] = []

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

        # Include rotation stream as half-floats to model modern engine quantization.
        for rx, ry, rz, rw in frame.rotations:
            payload.extend(_HALF_STRUCT.pack(rx))
            payload.extend(_HALF_STRUCT.pack(ry))
            payload.extend(_HALF_STRUCT.pack(rz))
            payload.extend(_HALF_STRUCT.pack(rw))

        compressed = zlib.compress(bytes(payload), level=6)
        sizes.append(len(compressed))
        prev_positions = frame.positions

    return sizes


def percentile(values: Sequence[float], p: float) -> float:
    if not values:
        return 0.0
    if p <= 0:
        return float(min(values))
    if p >= 100:
        return float(max(values))
    sorted_values = sorted(values)
    idx = int(round((p / 100.0) * (len(sorted_values) - 1)))
    return float(sorted_values[idx])
