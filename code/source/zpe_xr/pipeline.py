"""Gate evaluation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter_ns
from typing import Dict, List, Sequence, Tuple

from .codec import EncoderState, ParsedPacket, XRCodec
from .constants import FPS, RAW_BYTES_PER_FRAME
from .metrics import (
    modern_comparator_packet_sizes,
    mpjpe_mm,
    packet_size_stats,
    percentile,
    pose_error_percent,
    raw_stream_bytes,
)
from .models import Frame
from .network import (
    decode_diagnostics,
    decode_sequence,
    decode_with_realtime_recovery,
    encode_sequence,
    simulate_realtime_packet_map,
)
from .unity import UnityBridge

QPosFrame = List[Tuple[float, float, float]]


@dataclass
class GateBResult:
    packets: List[bytes]
    decoded_positions: List[QPosFrame]
    compression_metrics: Dict[str, object]
    fidelity_metrics: Dict[str, object]
    latency_metrics: Dict[str, object]


def evaluate_gate_b(frames: Sequence[Frame], codec: XRCodec) -> GateBResult:
    packets = encode_sequence(codec, frames)
    decoded_positions = decode_sequence(codec, packets)

    reference_positions = [list(frame.positions) for frame in frames]

    raw_total = raw_stream_bytes(len(frames))
    encoded_total = sum(len(packet) for packet in packets)

    modern_sizes = modern_comparator_packet_sizes(frames)
    modern_total = sum(modern_sizes)

    compression_metrics = {
        "num_frames": len(frames),
        "raw_bytes_total": raw_total,
        "encoded_bytes_total": encoded_total,
        "raw_bytes_per_frame": RAW_BYTES_PER_FRAME,
        "encoded_stats": packet_size_stats(packets),
        "compression_ratio_vs_raw": raw_total / encoded_total,
        "modern_comparator": {
            "bytes_total": modern_total,
            "avg_bytes_per_frame": (modern_total / len(modern_sizes)) if modern_sizes else 0.0,
            "ratio_vs_raw": (raw_total / modern_total) if modern_total else 0.0,
            "ratio_vs_zpe": (modern_total / encoded_total) if encoded_total else 0.0,
        },
    }

    fidelity_mpjpe = mpjpe_mm(reference_positions, decoded_positions)
    fidelity_metrics = {
        "num_frames": len(frames),
        "mpjpe_mm": fidelity_mpjpe,
        "pass_threshold_mm": 2.0,
        "pass": fidelity_mpjpe <= 2.0,
    }

    latency_metrics = _benchmark_latency(frames, codec)

    return GateBResult(
        packets=packets,
        decoded_positions=decoded_positions,
        compression_metrics=compression_metrics,
        fidelity_metrics=fidelity_metrics,
        latency_metrics=latency_metrics,
    )


def evaluate_packet_loss_resilience(
    *,
    frames: Sequence[Frame],
    packets: Sequence[bytes],
    codec: XRCodec,
    loss_rate: float,
    jitter_probability: float,
    max_delay_frames: int,
    seed: int,
) -> Dict[str, object]:
    packet_map = simulate_realtime_packet_map(
        packets,
        loss_rate=loss_rate,
        jitter_probability=jitter_probability,
        max_delay_frames=max_delay_frames,
        seed=seed,
    )

    reconstructed, delivery_stats = decode_with_realtime_recovery(
        codec,
        packet_map,
        total_frames=len(frames),
    )

    reference_positions = [list(frame.positions) for frame in frames]
    mpjpe = mpjpe_mm(reference_positions, reconstructed)
    pose_pct = pose_error_percent(mpjpe, reference_span_mm=120.0)

    stats = decode_diagnostics()
    result = {
        "loss_rate": loss_rate,
        "jitter_probability": jitter_probability,
        "max_delay_frames": max_delay_frames,
        "seed": seed,
        "mpjpe_mm": mpjpe,
        "pose_error_percent": pose_pct,
        "pass_threshold_percent": 5.0,
        "pass": pose_pct < 5.0,
        "delivery_stats": delivery_stats,
        "decoder_stats": stats,
    }
    return result


def evaluate_bandwidth(
    *,
    packets: Sequence[bytes],
    fps: int = FPS,
    remote_players: int = 3,
) -> Dict[str, object]:
    if not packets:
        return {
            "avg_packet_bytes": 0.0,
            "kbps_for_4_player_session": 0.0,
            "pass": True,
            "pass_threshold_kbps": 40.0,
        }

    avg_packet_bytes = sum(len(packet) for packet in packets) / len(packets)
    kb_per_sec_total = (avg_packet_bytes * fps * remote_players) / 1024.0

    return {
        "avg_packet_bytes": avg_packet_bytes,
        "fps": fps,
        "remote_players": remote_players,
        "kbps_for_4_player_session": kb_per_sec_total,
        "pass_threshold_kbps": 40.0,
        "pass": kb_per_sec_total <= 40.0,
    }


def evaluate_unity_roundtrip(frames: Sequence[Frame], codec: XRCodec) -> Dict[str, object]:
    encoder_state = EncoderState()
    received_packets: List[bytes] = []

    for frame in frames:
        packet = codec.encode_frame(frame, encoder_state)
        envelope = UnityBridge.serialize_packet(
            seq=frame.seq,
            timestamp_ms=frame.timestamp_ms,
            packet=packet,
        )
        recovered_packet = UnityBridge.deserialize_packet(envelope)
        received_packets.append(recovered_packet)

    decoded_positions = decode_sequence(codec, received_packets)
    reference_positions = [list(frame.positions) for frame in frames]
    mpjpe = mpjpe_mm(reference_positions, decoded_positions)

    return {
        "num_frames": len(frames),
        "mpjpe_mm": mpjpe,
        "pass_threshold_mm": 2.0,
        "pass": mpjpe <= 2.0,
        "unity_schema_version": UnityBridge.SCHEMA_VERSION,
    }


def _benchmark_latency(frames: Sequence[Frame], codec: XRCodec) -> Dict[str, object]:
    encoder_state = EncoderState()
    decode_prev_q = None

    per_frame_ms: List[float] = []
    encode_ms: List[float] = []
    decode_ms: List[float] = []

    for frame in frames:
        t0 = perf_counter_ns()
        packet = codec.encode_frame(frame, encoder_state)
        t1 = perf_counter_ns()

        parsed: ParsedPacket = codec.parse_packet(packet)
        if parsed.is_keyframe:
            decode_prev_q = parsed.keyframe_q
        else:
            if decode_prev_q is None:
                decode_prev_q = [(0, 0, 0)] * len(frame.positions)
            decode_prev_q = codec.apply_entries(decode_prev_q, parsed.current_entries)

        t2 = perf_counter_ns()

        e_ms = (t1 - t0) / 1_000_000.0
        d_ms = (t2 - t1) / 1_000_000.0
        encode_ms.append(e_ms)
        decode_ms.append(d_ms)
        per_frame_ms.append(e_ms + d_ms)

    combined_avg = sum(per_frame_ms) / len(per_frame_ms)
    combined_p95 = percentile(per_frame_ms, 95)
    combined_p99 = percentile(per_frame_ms, 99)

    return {
        "num_frames": len(frames),
        "encode_avg_ms": sum(encode_ms) / len(encode_ms),
        "decode_avg_ms": sum(decode_ms) / len(decode_ms),
        "combined_avg_ms": combined_avg,
        "combined_p95_ms": combined_p95,
        "combined_p99_ms": combined_p99,
        "pass_threshold_ms": 1.0,
        "pass": combined_avg <= 1.0 and combined_p95 <= 1.0,
    }
