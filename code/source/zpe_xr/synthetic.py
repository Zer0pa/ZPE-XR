"""Deterministic synthetic OpenXR-like hand sequence generation."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Dict, Iterable, List, Sequence, Tuple

from .constants import FPS, JOINTS_PER_HAND
from .models import Frame

CANONICAL_GESTURES = ("pinch", "grip", "wave", "point", "spread", "fist")


@dataclass(frozen=True)
class GestureProfile:
    curls: Dict[str, float]
    spread: float
    thumb_opposition: float
    wrist_wave_amp: float


_IDENTITY_QUAT = (0.0, 0.0, 0.0, 1.0)
_FINGER_ORDER = ("thumb", "index", "middle", "ring", "little")
_FINGER_BASE_X = {
    "thumb": 0.036,
    "index": 0.023,
    "middle": 0.004,
    "ring": -0.015,
    "little": -0.032,
}
_FINGER_BASE_Y = {
    "thumb": 0.008,
    "index": 0.028,
    "middle": 0.031,
    "ring": 0.028,
    "little": 0.023,
}
_FINGER_BASE_Z = {
    "thumb": 0.014,
    "index": 0.034,
    "middle": 0.038,
    "ring": 0.034,
    "little": 0.028,
}
_SEGMENT_LENGTHS = {
    "thumb": (0.022, 0.019, 0.017, 0.015),
    "index": (0.022, 0.019, 0.016, 0.013, 0.010),
    "middle": (0.024, 0.020, 0.017, 0.014, 0.011),
    "ring": (0.022, 0.019, 0.016, 0.013, 0.010),
    "little": (0.019, 0.017, 0.014, 0.011, 0.009),
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _gesture_profile(gesture: str, t: float) -> GestureProfile:
    if gesture == "pinch":
        return GestureProfile(
            curls={"thumb": 0.68, "index": 0.44, "middle": 0.76, "ring": 0.82, "little": 0.84},
            spread=0.08,
            thumb_opposition=0.95,
            wrist_wave_amp=0.002,
        )
    if gesture == "grip":
        return GestureProfile(
            curls={k: 0.78 for k in _FINGER_ORDER},
            spread=0.12,
            thumb_opposition=0.4,
            wrist_wave_amp=0.002,
        )
    if gesture == "wave":
        return GestureProfile(
            curls={"thumb": 0.22, "index": 0.18, "middle": 0.20, "ring": 0.24, "little": 0.28},
            spread=0.25,
            thumb_opposition=0.22,
            wrist_wave_amp=0.034,
        )
    if gesture == "point":
        return GestureProfile(
            curls={"thumb": 0.34, "index": 0.08, "middle": 0.86, "ring": 0.90, "little": 0.90},
            spread=0.20,
            thumb_opposition=0.5,
            wrist_wave_amp=0.002,
        )
    if gesture == "spread":
        return GestureProfile(
            curls={k: 0.05 for k in _FINGER_ORDER},
            spread=1.0,
            thumb_opposition=0.1,
            wrist_wave_amp=0.002,
        )
    if gesture == "fist":
        return GestureProfile(
            curls={k: 0.97 for k in _FINGER_ORDER},
            spread=0.03,
            thumb_opposition=0.35,
            wrist_wave_amp=0.001,
        )

    # Mixed dynamic profile used for benchmark runs.
    return GestureProfile(
        curls={
            "thumb": 0.35 + 0.12 * math.sin(1.2 * t),
            "index": 0.30 + 0.14 * math.sin(0.9 * t + 0.6),
            "middle": 0.34 + 0.13 * math.sin(0.85 * t + 1.1),
            "ring": 0.39 + 0.16 * math.sin(0.75 * t + 1.5),
            "little": 0.43 + 0.15 * math.sin(0.65 * t + 1.9),
        },
        spread=0.30 + 0.20 * math.sin(0.35 * t),
        thumb_opposition=0.25 + 0.15 * math.sin(1.1 * t + 0.3),
        wrist_wave_amp=0.006,
    )


def _build_finger(
    *,
    hand_sign: float,
    finger: str,
    wrist: Tuple[float, float, float],
    curl: float,
    spread: float,
    thumb_opposition: float,
    t: float,
) -> List[Tuple[float, float, float]]:
    base_x = _FINGER_BASE_X[finger] * hand_sign
    base_x += hand_sign * spread * 0.006 * _FINGER_ORDER.index(finger)
    base_y = _FINGER_BASE_Y[finger]
    base_z = _FINGER_BASE_Z[finger]

    x = wrist[0] + base_x
    y = wrist[1] + base_y
    z = wrist[2] + base_z

    points: List[Tuple[float, float, float]] = []
    segment_lengths = _SEGMENT_LENGTHS[finger]

    if finger == "thumb":
        for idx, seg_len in enumerate(segment_lengths):
            # Thumb bends across x-z plane and opposes toward index during pinch.
            theta = _clamp(curl, 0.0, 1.0) * (0.45 + idx * 0.30)
            x += hand_sign * seg_len * math.cos(theta)
            y += seg_len * (0.18 + 0.04 * idx)
            z -= seg_len * math.sin(theta)
            x += hand_sign * thumb_opposition * 0.004 * (idx + 1)
            z -= thumb_opposition * 0.002 * (idx + 1)
            points.append((x, y, z))
        return points

    # Non-thumb fingers bend mostly in y-z with minor x spread dynamics.
    for idx, seg_len in enumerate(segment_lengths):
        theta = _clamp(curl, 0.0, 1.0) * (0.50 + idx * 0.24)
        y += seg_len * math.cos(theta)
        z -= seg_len * math.sin(theta)
        x += hand_sign * spread * 0.0015 * math.sin(t * 0.6 + idx)
        points.append((x, y, z))

    return points


def _build_hand_positions(
    *,
    hand_sign: float,
    t: float,
    profile: GestureProfile,
    rng: random.Random,
) -> List[Tuple[float, float, float]]:
    phase_bias = 0.0 if hand_sign > 0 else 0.7
    wrist = (
        hand_sign * (0.082 + 0.005 * math.sin(0.7 * t + phase_bias)),
        1.245 + 0.004 * math.sin(0.45 * t + phase_bias),
        0.482 + 0.006 * math.cos(0.52 * t + phase_bias),
    )

    wrist = (
        wrist[0] + hand_sign * profile.wrist_wave_amp * math.sin(4.2 * t + phase_bias),
        wrist[1],
        wrist[2],
    )

    palm = (wrist[0], wrist[1] + 0.017, wrist[2] + 0.010)

    joints: List[Tuple[float, float, float]] = [wrist, palm]

    for finger in _FINGER_ORDER:
        finger_points = _build_finger(
            hand_sign=hand_sign,
            finger=finger,
            wrist=wrist,
            curl=profile.curls[finger],
            spread=profile.spread,
            thumb_opposition=profile.thumb_opposition,
            t=t,
        )
        joints.extend(finger_points)

    assert len(joints) == JOINTS_PER_HAND

    # Add deterministic micro-noise to avoid degenerate all-zero deltas.
    noisy: List[Tuple[float, float, float]] = []
    for x, y, z in joints:
        nx = x + rng.uniform(-0.00035, 0.00035)
        ny = y + rng.uniform(-0.00035, 0.00035)
        nz = z + rng.uniform(-0.00035, 0.00035)
        noisy.append((nx, ny, nz))

    return noisy


def generate_sequence(
    *,
    num_frames: int,
    seed: int,
    gesture: str = "mixed",
    phase_shift: float = 0.0,
) -> Tuple[Frame, ...]:
    rng = random.Random(seed)
    frames: List[Frame] = []

    for seq in range(num_frames):
        t = phase_shift + seq / FPS
        profile = _gesture_profile(gesture, t)

        left = _build_hand_positions(
            hand_sign=-1.0,
            t=t,
            profile=profile,
            rng=rng,
        )
        right = _build_hand_positions(
            hand_sign=1.0,
            t=t + 0.21,
            profile=profile,
            rng=rng,
        )

        positions = tuple(left + right)
        rotations = tuple(_IDENTITY_QUAT for _ in range(len(positions)))
        timestamp_ms = int(round((1000.0 / FPS) * seq))

        frames.append(
            Frame(
                seq=seq,
                timestamp_ms=timestamp_ms,
                positions=positions,
                rotations=rotations,
            )
        )

    return tuple(frames)


def generate_gesture_corpus(
    *,
    samples_per_gesture: int,
    frames_per_sample: int,
    seed: int,
) -> List[Tuple[str, Tuple[Frame, ...]]]:
    rng = random.Random(seed)
    corpus: List[Tuple[str, Tuple[Frame, ...]]] = []

    for gesture in CANONICAL_GESTURES:
        for _ in range(samples_per_gesture):
            phase_shift = rng.uniform(0.0, 4.0)
            sample_seed = rng.randint(1, 10_000_000)
            seq = generate_sequence(
                num_frames=frames_per_sample,
                seed=sample_seed,
                gesture=gesture,
                phase_shift=phase_shift,
            )
            corpus.append((gesture, seq))

    return corpus


def flatten_positions(frames: Sequence[Frame]) -> List[Tuple[float, float, float]]:
    flat: List[Tuple[float, float, float]] = []
    for frame in frames:
        flat.extend(frame.positions)
    return flat


def iter_gesture_names() -> Iterable[str]:
    return CANONICAL_GESTURES
