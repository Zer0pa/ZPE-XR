from __future__ import annotations

import numpy as np

import zpe_xr
from zpe_xr.synthetic import generate_sequence


def test_public_api_roundtrip_uses_rust_backend() -> None:
    frames = generate_sequence(num_frames=12, seed=1901, gesture="mixed")
    positions = np.asarray([frame.positions for frame in frames], dtype=np.float32)

    payload = zpe_xr.encode(positions, frame_rate=90)
    decoded = zpe_xr.decode(payload)
    label, confidence = zpe_xr.gesture_match(payload, ["wave", "grip", "pinch", "point"])
    info = zpe_xr.codec_info()

    assert decoded.shape == positions.shape
    assert info["backend"] == "rust"
    assert info["version"] == "0.3.1"
    assert info["comet_evidence"]
    assert label in {"wave", "grip", "pinch", "point"}
    assert 0.0 <= confidence <= 1.0
