from __future__ import annotations

import unittest

from zpe_xr.codec import EncoderState, XRCodec
from zpe_xr.metrics import packet_hash_digest
from zpe_xr.synthetic import generate_sequence


class DeterminismTests(unittest.TestCase):
    def test_packet_hash_determinism(self) -> None:
        frames = generate_sequence(num_frames=500, seed=1103, gesture="mixed")
        codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)

        first_state = EncoderState()
        second_state = EncoderState()

        first = [codec.encode_frame(frame, first_state) for frame in frames]
        second = [codec.encode_frame(frame, second_state) for frame in frames]

        self.assertEqual(packet_hash_digest(first), packet_hash_digest(second))
