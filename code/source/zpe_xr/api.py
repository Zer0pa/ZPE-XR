"""Install-time package API for the XR codec."""

from __future__ import annotations

import os
from typing import Iterable, Mapping, Sequence

import numpy as np

from ._stream import pack_packets, unpack_packets
from .codec import EncoderState, XRCodec
from .constants import FPS, TOTAL_JOINTS
from .gesture import classify_gesture
from .metadata import (
    COMPRESSION_RATIO_CLAIM,
    ENCODING_BASIS,
    KERNEL,
    PHASE4_COLD_START_COMET_KEY,
    PHASE5_MULTI_SEQUENCE_COMET_KEY,
    PRIMITIVE_COUNT,
    VERSION,
)
from .models import Frame
from .network import decode_sequence as decode_packet_sequence

try:
    from . import _kernel
except ImportError:  # pragma: no cover - exercised by fallback path only
    _kernel = None


def encode(joints: object, frame_rate: float = FPS) -> bytes:
    positions = _normalize_positions(joints)
    if _kernel is not None:
        return _kernel.encode_sequence(
            positions.tolist(),
            float(frame_rate),
            45,
            1,
            1.0,
            True,
        )
    return _encode_fallback(positions, frame_rate=float(frame_rate))


def decode(data: bytes | bytearray | memoryview) -> np.ndarray:
    payload = _normalize_bytes(data)
    if _kernel is not None:
        return np.asarray(_kernel.decode_sequence(payload, 1.0), dtype=np.float32)
    return np.asarray(_decode_fallback(payload), dtype=np.float32)


def gesture_match(
    data: bytes | bytearray | memoryview,
    vocabulary: Sequence[str] | Mapping[str, object] | None = None,
) -> tuple[str, float]:
    positions = decode(data)
    frames = _frames_from_positions(positions, frame_rate=FPS)
    allowed = _normalize_vocabulary(vocabulary)
    label, confidence = classify_gesture(frames, vocabulary=allowed)
    return label, float(confidence)


def codec_info() -> dict[str, object]:
    phase5_key = os.getenv("ZPE_XR_PHASE5_COMET_KEY", PHASE5_MULTI_SEQUENCE_COMET_KEY)
    phase4_key = PHASE4_COLD_START_COMET_KEY
    info: dict[str, object] = {
        "backend": "rust" if _kernel is not None else "python",
        "kernel": KERNEL,
        "encoding_basis": ENCODING_BASIS,
        "primitive_count": PRIMITIVE_COUNT,
        "version": VERSION,
        "compression_ratio_claim": COMPRESSION_RATIO_CLAIM,
        "comet_evidence": phase5_key or None,
    }
    if phase5_key:
        info["comet_phase5_multi_sequence"] = phase5_key
    if phase4_key:
        info["comet_phase4_cold_start"] = phase4_key
    return info


def _normalize_positions(joints: object) -> np.ndarray:
    positions = np.asarray(joints, dtype=np.float32)
    if positions.ndim != 3:
        raise ValueError("joints must have shape (frames, joints, xyz)")
    if positions.shape[1:] != (TOTAL_JOINTS, 3):
        raise ValueError(f"joints must have shape (frames, {TOTAL_JOINTS}, 3)")
    if not np.isfinite(positions).all():
        raise ValueError("joints contain non-finite values")
    return positions


def _normalize_bytes(data: bytes | bytearray | memoryview) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return bytes(data)
    if isinstance(data, memoryview):
        return data.tobytes()
    raise TypeError("data must be bytes-like")


def _normalize_vocabulary(
    vocabulary: Sequence[str] | Mapping[str, object] | None,
) -> tuple[str, ...] | None:
    if vocabulary is None:
        return None
    if isinstance(vocabulary, Mapping):
        labels = tuple(str(label) for label in vocabulary.keys())
    else:
        labels = tuple(str(label) for label in vocabulary)
    return labels or None


def _encode_fallback(positions: np.ndarray, *, frame_rate: float) -> bytes:
    codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)
    state = EncoderState()
    packets: list[bytes] = []
    for frame in _frames_from_positions(positions, frame_rate=frame_rate):
        packets.append(codec.encode_frame(frame, state))
    return pack_packets(packets)


def _decode_fallback(data: bytes) -> list[list[tuple[float, float, float]]]:
    codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)
    return decode_packet_sequence(codec, unpack_packets(data))


def _frames_from_positions(positions: np.ndarray, *, frame_rate: float) -> tuple[Frame, ...]:
    if frame_rate <= 0:
        raise ValueError("frame_rate must be > 0")

    rotations = ((0.0, 0.0, 0.0, 1.0),) * TOTAL_JOINTS
    frames = []
    for seq, frame_positions in enumerate(positions):
        timestamp_ms = int(round((1000.0 / frame_rate) * seq))
        frames.append(
            Frame(
                seq=seq,
                timestamp_ms=timestamp_ms,
                positions=tuple(tuple(float(value) for value in joint) for joint in frame_positions),
                rotations=rotations,
            )
        )
    return tuple(frames)
