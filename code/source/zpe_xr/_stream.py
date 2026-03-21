"""Shared byte-stream container used by the top-level package API."""

from __future__ import annotations

import struct
from typing import Sequence


STREAM_MAGIC = b"ZXRS"
STREAM_VERSION = 1
_HEADER = struct.Struct("<4sBI")
_PACKET_LEN = struct.Struct("<I")


def pack_packets(packets: Sequence[bytes]) -> bytes:
    payload = bytearray()
    payload.extend(_HEADER.pack(STREAM_MAGIC, STREAM_VERSION, len(packets)))
    for packet in packets:
        payload.extend(_PACKET_LEN.pack(len(packet)))
        payload.extend(packet)
    return bytes(payload)


def unpack_packets(data: bytes) -> list[bytes]:
    if len(data) < _HEADER.size:
        raise ValueError("stream too short")

    magic, version, count = _HEADER.unpack_from(data, 0)
    if magic != STREAM_MAGIC:
        raise ValueError("bad stream magic")
    if version != STREAM_VERSION:
        raise ValueError(f"unsupported stream version: {version}")

    cursor = _HEADER.size
    packets: list[bytes] = []
    for _ in range(count):
        if cursor + _PACKET_LEN.size > len(data):
            raise ValueError("truncated stream packet header")
        (packet_len,) = _PACKET_LEN.unpack_from(data, cursor)
        cursor += _PACKET_LEN.size
        end = cursor + packet_len
        if end > len(data):
            raise ValueError("truncated stream packet body")
        packets.append(bytes(data[cursor:end]))
        cursor = end

    if cursor != len(data):
        raise ValueError("stream contains trailing bytes")
    return packets
