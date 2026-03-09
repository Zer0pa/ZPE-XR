from __future__ import annotations

import unittest

from zpe_xr.codec import XRCodec
from zpe_xr.metrics import mpjpe_mm, pose_error_percent
from zpe_xr.network import (
    decode_with_realtime_recovery,
    encode_sequence,
    simulate_realtime_packet_map,
)
from zpe_xr.synthetic import generate_sequence


class NetworkTests(unittest.TestCase):
    def test_loss_resilience_target_threshold(self) -> None:
        frames = generate_sequence(num_frames=600, seed=3301, gesture="mixed")
        codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)
        packets = encode_sequence(codec, frames)

        packet_map = simulate_realtime_packet_map(
            packets,
            loss_rate=0.10,
            jitter_probability=0.20,
            max_delay_frames=1,
            seed=4409,
        )
        reconstructed, _ = decode_with_realtime_recovery(
            codec, packet_map, total_frames=len(frames)
        )
        ref = [list(frame.positions) for frame in frames]

        err_mm = mpjpe_mm(ref, reconstructed)
        self.assertLess(pose_error_percent(err_mm, reference_span_mm=120.0), 5.0)
