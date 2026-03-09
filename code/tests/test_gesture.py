from __future__ import annotations

import unittest

from zpe_xr.gesture import evaluate_corpus
from zpe_xr.synthetic import generate_gesture_corpus


class GestureTests(unittest.TestCase):
    def test_gesture_accuracy_threshold(self) -> None:
        corpus = generate_gesture_corpus(
            samples_per_gesture=12,
            frames_per_sample=50,
            seed=5501,
        )
        result = evaluate_corpus(corpus)
        self.assertGreaterEqual(result["accuracy"], 0.95)
