from __future__ import annotations

from zpe_xr.interhand_adapter import (
    InterHandSequenceMeta,
    build_zpe_frames_from_interhand_sequence,
    collect_interhand_sequences,
    interhand21_to_zpe_xr_26,
)


def _interhand_hand(offset: float) -> list[list[float]]:
    hand = []
    for idx in range(21):
        hand.append([offset + idx, offset + idx + 100, offset + idx + 200])
    return hand


def _annotations_fixture() -> dict[str, dict[str, dict[str, object]]]:
    full_valid = [[1.0] for _ in range(42)]
    partial_valid = [[1.0] for _ in range(21)] + [[0.0] for _ in range(21)]
    right = _interhand_hand(0.0)
    left = _interhand_hand(1000.0)
    world = right + left

    return {
        "0": {
            "100": {"world_coord": world, "joint_valid": full_valid, "hand_type": "interacting", "seq": "demo"},
            "101": {"world_coord": world, "joint_valid": full_valid, "hand_type": "interacting", "seq": "demo"},
            "102": {"world_coord": world, "joint_valid": partial_valid, "hand_type": "interacting", "seq": "demo"},
            "103": {"world_coord": world, "joint_valid": full_valid, "hand_type": "right", "seq": "single"},
        }
    }


def test_interhand21_to_zpe_xr_26_reorders_wrist_first() -> None:
    converted = interhand21_to_zpe_xr_26(_interhand_hand(0.0))

    assert len(converted) == 26
    assert converted[0] == (0.02, 0.12, 0.22)


def test_collect_interhand_sequences_filters_to_full_valid_interacting_frames() -> None:
    sequences = collect_interhand_sequences(_annotations_fixture(), split="test", min_frames=2)

    assert len(sequences) == 1
    assert sequences[0].seq_id == "demo"
    assert sequences[0].frame_count == 2


def test_build_zpe_frames_from_interhand_sequence_returns_dual_hand_frames() -> None:
    sequence = InterHandSequenceMeta(
        split="test",
        capture_id="0",
        seq_id="demo",
        frame_ids=("100", "101"),
        frame_count=2,
    )
    frames = build_zpe_frames_from_interhand_sequence(_annotations_fixture(), sequence)

    assert len(frames) == 2
    assert len(frames[0].positions) == 52
    assert frames[1].timestamp_ms > frames[0].timestamp_ms
