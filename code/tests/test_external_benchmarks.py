import unittest

from zpe_xr.external_benchmarks import (
    PHOTON_FUSION_COMPRESSED_BYTES_PER_HAND,
    PHOTON_FUSION_FULL_QUATERNION_BYTES_PER_HAND,
    ULTRALEAP_VECTORHAND_BYTES_PER_HAND,
    photon_fusion_measurement,
    ultraleap_vectorhand_measurement,
)


class ExternalBenchmarkTests(unittest.TestCase):
    def test_photon_reference_constants(self) -> None:
        self.assertEqual(PHOTON_FUSION_FULL_QUATERNION_BYTES_PER_HAND, 386)
        self.assertEqual(PHOTON_FUSION_COMPRESSED_BYTES_PER_HAND, 19)

    def test_ultraleap_reference_constant(self) -> None:
        self.assertEqual(ULTRALEAP_VECTORHAND_BYTES_PER_HAND, 86)

    def test_measurements_scale_to_two_hands(self) -> None:
        self.assertEqual(photon_fusion_measurement().bytes_per_frame, 38.0)
        self.assertEqual(ultraleap_vectorhand_measurement().bytes_per_frame, 172.0)
