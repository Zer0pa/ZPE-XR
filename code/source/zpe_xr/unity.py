"""Unity-facing packet envelope simulation for roundtrip validation."""

from __future__ import annotations

import base64
import json
from typing import Dict


class UnityBridge:
    """Represents the C#<->native packet envelope used for roundtrip validation."""

    SCHEMA_VERSION = "zpe-xr-unity-1"

    @classmethod
    def serialize_packet(cls, *, seq: int, timestamp_ms: int, packet: bytes) -> bytes:
        envelope: Dict[str, object] = {
            "schema": cls.SCHEMA_VERSION,
            "seq": seq,
            "timestamp_ms": timestamp_ms,
            "payload_b64": base64.b64encode(packet).decode("ascii"),
        }
        return json.dumps(envelope, separators=(",", ":")).encode("utf-8")

    @classmethod
    def deserialize_packet(cls, envelope_bytes: bytes) -> bytes:
        envelope = json.loads(envelope_bytes.decode("utf-8"))
        if envelope.get("schema") != cls.SCHEMA_VERSION:
            raise ValueError("Unsupported unity envelope schema")
        encoded = envelope.get("payload_b64")
        if not isinstance(encoded, str):
            raise ValueError("Malformed unity envelope payload")
        return base64.b64decode(encoded.encode("ascii"))
