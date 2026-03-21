"""Data models used across generation, codec, and evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

Vec3 = Tuple[float, float, float]
Quat = Tuple[float, float, float, float]


@dataclass(frozen=True)
class Frame:
    seq: int
    timestamp_ms: int
    positions: Tuple[Vec3, ...]
    rotations: Tuple[Quat, ...]


FrameSequence = Tuple[Frame, ...]
