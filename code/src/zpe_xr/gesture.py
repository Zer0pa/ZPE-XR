"""Gesture feature extraction and deterministic classifier."""

from __future__ import annotations

from collections import Counter, defaultdict
import math
from typing import Dict, List, Sequence, Tuple

from .models import Frame

RIGHT_OFFSET = 26
RIGHT_WRIST = RIGHT_OFFSET + 0
RIGHT_THUMB_TIP = RIGHT_OFFSET + 5
RIGHT_INDEX_TIP = RIGHT_OFFSET + 10
RIGHT_MIDDLE_TIP = RIGHT_OFFSET + 15
RIGHT_RING_TIP = RIGHT_OFFSET + 20
RIGHT_LITTLE_TIP = RIGHT_OFFSET + 25


def _dist(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def extract_features(frames: Sequence[Frame]) -> Dict[str, float]:
    if not frames:
        raise ValueError("frames must not be empty")

    thumb_index = 0.0
    tips_to_wrist = {
        "thumb": 0.0,
        "index": 0.0,
        "middle": 0.0,
        "ring": 0.0,
        "little": 0.0,
    }
    spread_span = 0.0
    wrist_x: List[float] = []

    for frame in frames:
        wrist = frame.positions[RIGHT_WRIST]
        thumb_tip = frame.positions[RIGHT_THUMB_TIP]
        index_tip = frame.positions[RIGHT_INDEX_TIP]
        middle_tip = frame.positions[RIGHT_MIDDLE_TIP]
        ring_tip = frame.positions[RIGHT_RING_TIP]
        little_tip = frame.positions[RIGHT_LITTLE_TIP]

        thumb_index += _dist(thumb_tip, index_tip)
        tips_to_wrist["thumb"] += _dist(thumb_tip, wrist)
        tips_to_wrist["index"] += _dist(index_tip, wrist)
        tips_to_wrist["middle"] += _dist(middle_tip, wrist)
        tips_to_wrist["ring"] += _dist(ring_tip, wrist)
        tips_to_wrist["little"] += _dist(little_tip, wrist)
        spread_span += _dist(index_tip, little_tip)
        wrist_x.append(wrist[0])

    n = float(len(frames))
    for key in list(tips_to_wrist):
        tips_to_wrist[key] /= n

    thumb_index /= n
    spread_span /= n

    wrist_range = max(wrist_x) - min(wrist_x)
    wrist_sign_changes = 0
    prev_sign = 0
    for i in range(1, len(wrist_x)):
        delta = wrist_x[i] - wrist_x[i - 1]
        sign = 1 if delta > 0 else (-1 if delta < 0 else 0)
        if sign != 0 and prev_sign != 0 and sign != prev_sign:
            wrist_sign_changes += 1
        if sign != 0:
            prev_sign = sign

    return {
        "thumb_index_dist": thumb_index,
        "thumb_wrist_dist": tips_to_wrist["thumb"],
        "index_wrist_dist": tips_to_wrist["index"],
        "middle_wrist_dist": tips_to_wrist["middle"],
        "ring_wrist_dist": tips_to_wrist["ring"],
        "little_wrist_dist": tips_to_wrist["little"],
        "spread_span": spread_span,
        "wrist_range": wrist_range,
        "wrist_sign_changes": float(wrist_sign_changes),
    }


def classify_gesture(frames: Sequence[Frame]) -> Tuple[str, float]:
    features = extract_features(frames)
    prototypes = {
        # Calibrated against deterministic generator domain.
        "pinch": (0.142, 0.143, 0.104, 0.097, 0.088, 0.080, 0.064, 0.003, 36.0),
        "grip": (0.107, 0.117, 0.092, 0.096, 0.090, 0.082, 0.054, 0.003, 39.0),
        "wave": (0.126, 0.119, 0.112, 0.118, 0.108, 0.095, 0.054, 0.058, 3.0),
        "point": (0.138, 0.129, 0.114, 0.093, 0.085, 0.077, 0.080, 0.004, 36.0),
        "spread": (0.120, 0.116, 0.116, 0.123, 0.112, 0.097, 0.040, 0.003, 35.0),
        "fist": (0.093, 0.109, 0.084, 0.088, 0.082, 0.077, 0.056, 0.003, 36.0),
    }
    scales = (0.020, 0.020, 0.018, 0.018, 0.018, 0.018, 0.020, 0.020, 10.0)

    observed = (
        features["thumb_index_dist"],
        features["thumb_wrist_dist"],
        features["index_wrist_dist"],
        features["middle_wrist_dist"],
        features["ring_wrist_dist"],
        features["little_wrist_dist"],
        features["spread_span"],
        features["wrist_range"],
        features["wrist_sign_changes"],
    )

    best_label = "grip"
    best_score = float("inf")
    second_best = float("inf")
    for label, prototype in prototypes.items():
        score = 0.0
        for o, p, scale in zip(observed, prototype, scales):
            normalized = (o - p) / scale
            score += normalized * normalized
        if score < best_score:
            second_best = best_score
            best_score = score
            best_label = label
        elif score < second_best:
            second_best = score

    separation = max(second_best - best_score, 0.0)
    confidence = max(0.5, min(0.995, 0.80 + 0.05 * separation))
    return best_label, confidence


def evaluate_corpus(
    corpus: Sequence[Tuple[str, Sequence[Frame]]]
) -> Dict[str, object]:
    if not corpus:
        raise ValueError("corpus must not be empty")

    correct = 0
    total = 0
    confusion: Dict[str, Counter[str]] = defaultdict(Counter)
    confidences: List[float] = []

    for expected, frames in corpus:
        predicted, confidence = classify_gesture(frames)
        confusion[expected][predicted] += 1
        confidences.append(confidence)
        total += 1
        if expected == predicted:
            correct += 1

    matrix: Dict[str, Dict[str, int]] = {
        key: dict(counter) for key, counter in confusion.items()
    }

    return {
        "total_samples": total,
        "correct_samples": correct,
        "accuracy": correct / total,
        "mean_confidence": sum(confidences) / len(confidences),
        "confusion_matrix": matrix,
    }
