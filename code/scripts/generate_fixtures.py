#!/usr/bin/env python3
"""Generate deterministic fixture manifests used by Gate B-D runs."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_xr.io_utils import write_json
from zpe_xr.synthetic import CANONICAL_GESTURES, generate_gesture_corpus, generate_sequence


def _digest_positions(frames) -> str:
    h = sha256()
    for frame in frames:
        for x, y, z in frame.positions:
            h.update(f"{x:.6f}|{y:.6f}|{z:.6f}".encode("utf-8"))
    return h.hexdigest()


def main() -> int:
    fixtures_dir = ROOT / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    benchmark_frames = generate_sequence(num_frames=1800, seed=1103, gesture="mixed")
    gesture_corpus = generate_gesture_corpus(
        samples_per_gesture=40,
        frames_per_sample=60,
        seed=2207,
    )

    benchmark_config = {
        "benchmark_sequence": {
            "seed": 1103,
            "num_frames": 1800,
            "gesture": "mixed",
            "digest": _digest_positions(benchmark_frames),
        },
        "gesture_corpus": {
            "seed": 2207,
            "samples_per_gesture": 40,
            "frames_per_sample": 60,
            "labels": list(CANONICAL_GESTURES),
            "num_samples": len(gesture_corpus),
            "first_sample_digest": _digest_positions(gesture_corpus[0][1]),
        },
        "determinism_seeds": [1103, 2207, 3301, 4409, 5501],
    }

    write_json(fixtures_dir / "benchmark_config.json", benchmark_config)
    print("Generated fixtures/benchmark_config.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
