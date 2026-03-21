"""Deterministic hand-pose codec with bounded packet parser and backup deltas."""

from __future__ import annotations

from dataclasses import dataclass, field
import struct
from typing import List, Optional, Sequence, Tuple
import zlib

from .constants import (
    DEFAULT_DEADBAND_MM,
    DEFAULT_KEYFRAME_INTERVAL,
    FORMAT_VERSION,
    MAGIC,
    MM_PER_METER,
    NO_BACKUP_SEQ,
    TOTAL_JOINTS,
)
from .models import Frame

QVec3 = Tuple[int, int, int]
DeltaEntry = Tuple[int, int, int, int]

_HEADER_STRUCT = struct.Struct("<3sBBHHIBB")
_ENTRY_STRUCT = struct.Struct("<Bbbb")
_QVEC_STRUCT = struct.Struct("<hhh")
_CHECKSUM_STRUCT = struct.Struct("<I")

_FLAG_KEYFRAME = 0x01


class PacketDecodeError(ValueError):
    """Raised when packet parsing fails validation."""


@dataclass
class ParsedPacket:
    seq: int
    timestamp_ms: int
    is_keyframe: bool
    keyframe_q: Optional[List[QVec3]]
    current_entries: List[DeltaEntry]
    backup_seq: int
    backup_entries: List[DeltaEntry]


@dataclass
class EncoderState:
    reference_q: Optional[List[QVec3]] = None
    last_primary_entries: List[DeltaEntry] = field(default_factory=list)
    last_primary_seq: int = NO_BACKUP_SEQ


@dataclass
class DecoderState:
    decoded_q: dict[int, List[QVec3]] = field(default_factory=dict)


class XRCodec:
    """Quantized delta codec for dual-hand joint positions."""

    def __init__(
        self,
        *,
        keyframe_interval: int = DEFAULT_KEYFRAME_INTERVAL,
        deadband_mm: int = DEFAULT_DEADBAND_MM,
        quant_step_mm: float = 1.0,
        enable_backup: bool = True,
    ) -> None:
        if keyframe_interval <= 0:
            raise ValueError("keyframe_interval must be > 0")
        if deadband_mm < 0:
            raise ValueError("deadband_mm must be >= 0")
        if quant_step_mm <= 0:
            raise ValueError("quant_step_mm must be > 0")

        self.keyframe_interval = keyframe_interval
        self.deadband_mm = deadband_mm
        self.quant_step_mm = quant_step_mm
        self.enable_backup = enable_backup

    def encode_frame(self, frame: Frame, state: EncoderState) -> bytes:
        q_actual = self.quantize_positions(frame.positions)

        force_keyframe = (
            state.reference_q is None
            or frame.seq % self.keyframe_interval == 0
            or len(q_actual) != TOTAL_JOINTS
        )

        if force_keyframe:
            state.reference_q = list(q_actual)
            state.last_primary_entries = []
            state.last_primary_seq = NO_BACKUP_SEQ
            return self._build_keyframe_packet(frame.seq, frame.timestamp_ms, q_actual)

        assert state.reference_q is not None
        entries, updated_ref, overflow = self._compute_delta_entries(
            q_actual, state.reference_q
        )

        if overflow:
            # Hard reset on large divergence.
            state.reference_q = list(q_actual)
            state.last_primary_entries = []
            state.last_primary_seq = NO_BACKUP_SEQ
            return self._build_keyframe_packet(frame.seq, frame.timestamp_ms, q_actual)

        if self.enable_backup:
            backup_seq = state.last_primary_seq
            backup_entries = list(state.last_primary_entries)
        else:
            backup_seq = NO_BACKUP_SEQ
            backup_entries = []

        packet = self._build_delta_packet(
            seq=frame.seq,
            timestamp_ms=frame.timestamp_ms,
            current_entries=entries,
            backup_seq=backup_seq,
            backup_entries=backup_entries,
        )

        state.reference_q = updated_ref
        state.last_primary_entries = list(entries)
        state.last_primary_seq = frame.seq
        return packet

    def parse_packet(self, packet: bytes) -> ParsedPacket:
        if len(packet) < _HEADER_STRUCT.size + _CHECKSUM_STRUCT.size:
            raise PacketDecodeError("Packet too short")

        payload = packet[:-_CHECKSUM_STRUCT.size]
        supplied_checksum = _CHECKSUM_STRUCT.unpack(packet[-_CHECKSUM_STRUCT.size :])[0]
        calc_checksum = zlib.crc32(payload) & 0xFFFFFFFF
        if calc_checksum != supplied_checksum:
            raise PacketDecodeError("Checksum mismatch")

        (
            magic,
            version,
            flags,
            seq,
            backup_seq,
            timestamp_ms,
            current_count,
            backup_count,
        ) = _HEADER_STRUCT.unpack(payload[: _HEADER_STRUCT.size])

        if magic != MAGIC:
            raise PacketDecodeError("Bad packet magic")
        if version != FORMAT_VERSION:
            raise PacketDecodeError("Unsupported packet version")

        cursor = _HEADER_STRUCT.size
        body = payload[cursor:]
        is_keyframe = bool(flags & _FLAG_KEYFRAME)

        if is_keyframe:
            expected_len = TOTAL_JOINTS * _QVEC_STRUCT.size
            if len(body) != expected_len:
                raise PacketDecodeError("Keyframe body length mismatch")
            keyframe_q: List[QVec3] = []
            for idx in range(TOTAL_JOINTS):
                start = idx * _QVEC_STRUCT.size
                keyframe_q.append(_QVEC_STRUCT.unpack(body[start : start + _QVEC_STRUCT.size]))
            return ParsedPacket(
                seq=seq,
                timestamp_ms=timestamp_ms,
                is_keyframe=True,
                keyframe_q=keyframe_q,
                current_entries=[],
                backup_seq=NO_BACKUP_SEQ,
                backup_entries=[],
            )

        expected_len = (current_count + backup_count) * _ENTRY_STRUCT.size
        if len(body) != expected_len:
            raise PacketDecodeError("Delta body length mismatch")

        current_entries = self._parse_entries(body, 0, current_count)
        backup_entries = self._parse_entries(body, current_count, backup_count)

        return ParsedPacket(
            seq=seq,
            timestamp_ms=timestamp_ms,
            is_keyframe=False,
            keyframe_q=None,
            current_entries=current_entries,
            backup_seq=backup_seq,
            backup_entries=backup_entries,
        )

    def quantize_positions(self, positions: Sequence[Tuple[float, float, float]]) -> List[QVec3]:
        scale = MM_PER_METER / self.quant_step_mm
        quantized: List[QVec3] = []
        for x, y, z in positions:
            quantized.append((int(round(x * scale)), int(round(y * scale)), int(round(z * scale))))
        return quantized

    def dequantize_positions(self, q_positions: Sequence[QVec3]) -> List[Tuple[float, float, float]]:
        scale = self.quant_step_mm / MM_PER_METER
        return [(x * scale, y * scale, z * scale) for x, y, z in q_positions]

    @staticmethod
    def apply_entries(base_q: Sequence[QVec3], entries: Sequence[DeltaEntry]) -> List[QVec3]:
        updated = list(base_q)
        for joint_index, dx, dy, dz in entries:
            if joint_index < 0 or joint_index >= len(updated):
                raise PacketDecodeError("Joint index out of range")
            x, y, z = updated[joint_index]
            updated[joint_index] = (x + dx, y + dy, z + dz)
        return updated

    @staticmethod
    def conceal_next(prev_q: Sequence[QVec3], prev_prev_q: Optional[Sequence[QVec3]]) -> List[QVec3]:
        if prev_prev_q is None:
            return list(prev_q)

        concealed: List[QVec3] = []
        for (x1, y1, z1), (x0, y0, z0) in zip(prev_q, prev_prev_q):
            dx = max(min(x1 - x0, 8), -8)
            dy = max(min(y1 - y0, 8), -8)
            dz = max(min(z1 - z0, 8), -8)
            concealed.append((x1 + dx, y1 + dy, z1 + dz))
        return concealed

    def _compute_delta_entries(
        self,
        q_actual: Sequence[QVec3],
        q_ref: Sequence[QVec3],
    ) -> Tuple[List[DeltaEntry], List[QVec3], bool]:
        entries: List[DeltaEntry] = []
        updated_ref = list(q_ref)
        overflow = False

        for idx, (qa, qr) in enumerate(zip(q_actual, q_ref)):
            dx = qa[0] - qr[0]
            dy = qa[1] - qr[1]
            dz = qa[2] - qr[2]
            if max(abs(dx), abs(dy), abs(dz)) <= self.deadband_mm:
                continue

            if max(abs(dx), abs(dy), abs(dz)) > 127:
                overflow = True
                break

            entry = (idx, dx, dy, dz)
            entries.append(entry)
            updated_ref[idx] = (qr[0] + dx, qr[1] + dy, qr[2] + dz)

        return entries, updated_ref, overflow

    @staticmethod
    def _parse_entries(body: bytes, start_idx: int, count: int) -> List[DeltaEntry]:
        entries: List[DeltaEntry] = []
        for local_idx in range(count):
            global_idx = start_idx + local_idx
            offset = global_idx * _ENTRY_STRUCT.size
            entry = _ENTRY_STRUCT.unpack(body[offset : offset + _ENTRY_STRUCT.size])
            entries.append(entry)
        return entries

    def _build_keyframe_packet(self, seq: int, timestamp_ms: int, q_positions: Sequence[QVec3]) -> bytes:
        header = _HEADER_STRUCT.pack(
            MAGIC,
            FORMAT_VERSION,
            _FLAG_KEYFRAME,
            seq,
            NO_BACKUP_SEQ,
            timestamp_ms,
            TOTAL_JOINTS,
            0,
        )

        body = bytearray()
        for q in q_positions:
            body.extend(_QVEC_STRUCT.pack(*q))

        return self._append_checksum(bytes(header) + bytes(body))

    def _build_delta_packet(
        self,
        *,
        seq: int,
        timestamp_ms: int,
        current_entries: Sequence[DeltaEntry],
        backup_seq: int,
        backup_entries: Sequence[DeltaEntry],
    ) -> bytes:
        if backup_seq == NO_BACKUP_SEQ:
            backup_entries = []

        header = _HEADER_STRUCT.pack(
            MAGIC,
            FORMAT_VERSION,
            0,
            seq,
            backup_seq,
            timestamp_ms,
            len(current_entries),
            len(backup_entries),
        )

        body = bytearray()
        for entry in current_entries:
            body.extend(_ENTRY_STRUCT.pack(*entry))
        for entry in backup_entries:
            body.extend(_ENTRY_STRUCT.pack(*entry))

        return self._append_checksum(bytes(header) + bytes(body))

    @staticmethod
    def _append_checksum(payload: bytes) -> bytes:
        checksum = zlib.crc32(payload) & 0xFFFFFFFF
        return payload + _CHECKSUM_STRUCT.pack(checksum)
