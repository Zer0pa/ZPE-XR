"""Packet delivery simulation and reconstruction routines."""

from __future__ import annotations

import random
from typing import Dict, List, Sequence, Tuple

from .codec import PacketDecodeError, XRCodec
from .constants import NO_BACKUP_SEQ, TOTAL_JOINTS
from .models import Frame

QVec3 = Tuple[int, int, int]


def encode_sequence(codec: XRCodec, frames: Sequence[Frame]) -> List[bytes]:
    from .codec import EncoderState

    state = EncoderState()
    packets: List[bytes] = []
    for frame in frames:
        packets.append(codec.encode_frame(frame, state))
    return packets


def decode_sequence(codec: XRCodec, packets: Sequence[bytes]) -> List[List[Tuple[float, float, float]]]:
    decoded_q = _decode_q_sequence(codec=codec, packets_by_seq={i: p for i, p in enumerate(packets)}, total_frames=len(packets))
    return [codec.dequantize_positions(frame_q) for frame_q in decoded_q]


def simulate_realtime_packet_map(
    packets: Sequence[bytes],
    *,
    loss_rate: float,
    jitter_probability: float,
    max_delay_frames: int,
    seed: int,
) -> Dict[int, bytes]:
    rng = random.Random(seed)
    on_time: Dict[int, bytes] = {}

    for seq, packet in enumerate(packets):
        if rng.random() < loss_rate:
            continue

        delay = 0
        if max_delay_frames > 0 and rng.random() < jitter_probability:
            delay = rng.randint(1, max_delay_frames)

        # Real-time path treats late packets as unusable for target frame.
        if delay == 0:
            on_time[seq] = packet

    return on_time


def decode_with_realtime_recovery(
    codec: XRCodec,
    packets_by_seq: Dict[int, bytes],
    *,
    total_frames: int,
) -> Tuple[List[List[Tuple[float, float, float]]], Dict[str, int]]:
    decoded_q = _decode_q_sequence(codec=codec, packets_by_seq=packets_by_seq, total_frames=total_frames)
    decoded_positions = [codec.dequantize_positions(frame_q) for frame_q in decoded_q]

    stats = {
        "provided_packets": len(packets_by_seq),
        "missing_packets": max(total_frames - len(packets_by_seq), 0),
        "total_frames": total_frames,
    }
    return decoded_positions, stats


def _decode_q_sequence(
    *,
    codec: XRCodec,
    packets_by_seq: Dict[int, bytes],
    total_frames: int,
) -> List[List[QVec3]]:
    decoded_by_seq: Dict[int, List[QVec3]] = {}

    concealed_frames = 0
    backup_recoveries = 0
    parse_failures = 0

    for seq in range(total_frames):
        packet = packets_by_seq.get(seq)
        parsed = None

        if packet is not None:
            try:
                parsed = codec.parse_packet(packet)
            except PacketDecodeError:
                parsed = None
                parse_failures += 1

        if parsed is None:
            prev = decoded_by_seq.get(seq - 1)
            prev_prev = decoded_by_seq.get(seq - 2)
            if prev is None and prev_prev is None:
                decoded_by_seq[seq] = [(0, 0, 0)] * TOTAL_JOINTS
            elif prev is None:
                decoded_by_seq[seq] = list(prev_prev)  # type: ignore[arg-type]
            else:
                decoded_by_seq[seq] = codec.conceal_next(prev, prev_prev)
            concealed_frames += 1
            continue

        if parsed.is_keyframe:
            assert parsed.keyframe_q is not None
            decoded_by_seq[seq] = list(parsed.keyframe_q)
            continue

        base_prev = decoded_by_seq.get(seq - 1)

        # If the immediate prior packet was missing, prefer explicit backup entries over
        # a concealed previous pose when backup information is present.
        if parsed.backup_seq == seq - 1 and parsed.backup_seq != NO_BACKUP_SEQ:
            prev_prev = decoded_by_seq.get(seq - 2)
            prior_missing_on_wire = (seq - 1) not in packets_by_seq
            if prev_prev is not None and (base_prev is None or prior_missing_on_wire):
                recovered = codec.apply_entries(prev_prev, parsed.backup_entries)
                decoded_by_seq[seq - 1] = recovered
                base_prev = recovered
                backup_recoveries += 1

        if base_prev is None:
            prev_prev = decoded_by_seq.get(seq - 2)
            if prev_prev is not None:
                concealed_prev = codec.conceal_next(prev_prev, decoded_by_seq.get(seq - 3))
                decoded_by_seq[seq - 1] = concealed_prev
                base_prev = concealed_prev
            else:
                base_prev = [(0, 0, 0)] * TOTAL_JOINTS

        try:
            decoded_by_seq[seq] = codec.apply_entries(base_prev, parsed.current_entries)
        except PacketDecodeError:
            decoded_by_seq[seq] = codec.conceal_next(base_prev, decoded_by_seq.get(seq - 2))
            parse_failures += 1

    # Ensure no gaps remain.
    ordered: List[List[QVec3]] = []
    for seq in range(total_frames):
        frame_q = decoded_by_seq.get(seq)
        if frame_q is None:
            prev = ordered[-1] if ordered else [(0, 0, 0)] * TOTAL_JOINTS
            prev_prev = ordered[-2] if len(ordered) > 1 else None
            frame_q = codec.conceal_next(prev, prev_prev)
            concealed_frames += 1
        ordered.append(frame_q)

    # attach diagnostics for caller scripts through function attributes
    _decode_q_sequence.last_stats = {
        "concealed_frames": concealed_frames,
        "backup_recoveries": backup_recoveries,
        "parse_failures": parse_failures,
    }
    return ordered


def decode_diagnostics() -> Dict[str, int]:
    return getattr(_decode_q_sequence, "last_stats", {})
