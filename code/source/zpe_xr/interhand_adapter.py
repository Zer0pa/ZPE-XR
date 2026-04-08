"""InterHand2.6M adapters for the canonical XR benchmark lane."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .constants import FPS, TOTAL_JOINTS
from .contactpose_adapter import contactpose_21_to_zpe_xr_26
from .models import Frame


INTERHAND_HAND_JOINTS = 21
INTERHAND_TOTAL_JOINTS = 42
_IDENTITY_QUAT = (0.0, 0.0, 0.0, 1.0)
_INTERHAND_TO_OPENPOSE_ORDER = (
    20,
    3,
    2,
    1,
    0,
    7,
    6,
    5,
    4,
    11,
    10,
    9,
    8,
    15,
    14,
    13,
    12,
    19,
    18,
    17,
    16,
)


InterHandAnnotations = dict[str, dict[str, dict[str, Any]]]


@dataclass(frozen=True)
class InterHandSequenceMeta:
    split: str
    capture_id: str
    seq_id: str
    frame_ids: tuple[str, ...]
    frame_count: int


def load_interhand_joint_annotations(path: Path) -> InterHandAnnotations:
    return json.loads(path.read_text(encoding="utf-8"))


def interhand21_to_zpe_xr_26(hand_joints_mm: list[list[float]] | tuple[tuple[float, ...], ...]) -> tuple[tuple[float, float, float], ...]:
    if len(hand_joints_mm) != INTERHAND_HAND_JOINTS:
        raise ValueError(f"expected {INTERHAND_HAND_JOINTS} hand joints, got {len(hand_joints_mm)}")

    openpose_order = []
    for idx in _INTERHAND_TO_OPENPOSE_ORDER:
        x_mm, y_mm, z_mm = hand_joints_mm[idx][:3]
        openpose_order.append((float(x_mm) / 1000.0, float(y_mm) / 1000.0, float(z_mm) / 1000.0))
    return contactpose_21_to_zpe_xr_26(openpose_order)


def collect_interhand_sequences(
    annotations: InterHandAnnotations,
    *,
    split: str,
    min_frames: int = 90,
    require_full_valid: bool = True,
) -> list[InterHandSequenceMeta]:
    grouped: dict[tuple[str, str], list[str]] = {}

    for capture_id, frames in annotations.items():
        for frame_id in sorted(frames, key=int):
            item = frames[frame_id]
            if item.get("hand_type") != "interacting":
                continue
            if require_full_valid and not _frame_has_all_joints(item.get("joint_valid", [])):
                continue

            key = (str(capture_id), str(item["seq"]))
            grouped.setdefault(key, []).append(str(frame_id))

    sequences = [
        InterHandSequenceMeta(
            split=split,
            capture_id=capture_id,
            seq_id=seq_id,
            frame_ids=tuple(frame_ids),
            frame_count=len(frame_ids),
        )
        for (capture_id, seq_id), frame_ids in grouped.items()
        if len(frame_ids) >= min_frames
    ]
    return sorted(
        sequences,
        key=lambda item: (-item.frame_count, item.split, item.capture_id, item.seq_id),
    )


def build_zpe_frames_from_interhand_sequence(
    annotations: InterHandAnnotations,
    sequence: InterHandSequenceMeta,
    *,
    max_frames: int | None = None,
) -> tuple[Frame, ...]:
    capture = annotations[sequence.capture_id]
    selected_frame_ids = sequence.frame_ids[:max_frames] if max_frames is not None else sequence.frame_ids

    frames: list[Frame] = []
    for seq_index, frame_id in enumerate(selected_frame_ids):
        item = capture[frame_id]
        world_coord = item["world_coord"]
        if len(world_coord) != INTERHAND_TOTAL_JOINTS:
            raise ValueError(f"expected {INTERHAND_TOTAL_JOINTS} world joints, got {len(world_coord)}")
        if not _frame_has_all_joints(item.get("joint_valid", [])):
            raise ValueError(f"frame {frame_id} is not fully valid")

        right_hand = interhand21_to_zpe_xr_26(world_coord[:INTERHAND_HAND_JOINTS])
        left_hand = interhand21_to_zpe_xr_26(world_coord[INTERHAND_HAND_JOINTS:])
        positions = tuple(right_hand + left_hand)
        if len(positions) != TOTAL_JOINTS:
            raise AssertionError(f"expected {TOTAL_JOINTS} canonical joints, got {len(positions)}")

        frames.append(
            Frame(
                seq=seq_index,
                timestamp_ms=int(round((1000.0 / FPS) * seq_index)),
                positions=positions,
                rotations=tuple(_IDENTITY_QUAT for _ in range(TOTAL_JOINTS)),
            )
        )

    return tuple(frames)


def _frame_has_all_joints(joint_valid: list[Any]) -> bool:
    if len(joint_valid) != INTERHAND_TOTAL_JOINTS:
        return False
    flattened = [_as_valid_flag(value) for value in joint_valid]
    return all(flattened)


def _as_valid_flag(value: Any) -> int:
    if isinstance(value, list):
        return int(value[0])
    return int(value)
