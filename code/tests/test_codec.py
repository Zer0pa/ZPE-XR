from __future__ import annotations

import unittest

from zpe_xr.codec import PacketDecodeError, XRCodec
from zpe_xr.metrics import mpjpe_mm
from zpe_xr.network import decode_sequence, encode_sequence
from zpe_xr.synthetic import generate_sequence


class CodecTests(unittest.TestCase):
    def test_roundtrip_fidelity_threshold(self) -> None:
        frames = generate_sequence(num_frames=300, seed=1103, gesture="mixed")
        codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)
        packets = encode_sequence(codec, frames)
        decoded = decode_sequence(codec, packets)
        ref = [list(frame.positions) for frame in frames]
        self.assertLessEqual(mpjpe_mm(ref, decoded), 2.0)

    def test_parser_rejects_bad_checksum(self) -> None:
        frames = generate_sequence(num_frames=10, seed=2207, gesture="mixed")
        codec = XRCodec()
        packet = encode_sequence(codec, frames)[3]
        bad = bytearray(packet)
        bad[-1] ^= 0xFF

        with self.assertRaises(PacketDecodeError):
            codec.parse_packet(bytes(bad))
