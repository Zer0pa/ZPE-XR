from zpe_xr.external_benchmarks import photon_fusion_measurement
from zpe_xr.phase8_photon_benchmarks import measure_photon_row
from zpe_xr.photon_hands_proxy import (
    PHOTON_COMPRESSED_BYTES_PER_HAND,
    calibrate_sequence,
    decode_frame,
    encode_frame,
)
from zpe_xr.synthetic import generate_sequence


def test_encode_frame_uses_fixed_photon_width() -> None:
    frames = generate_sequence(num_frames=1, seed=7, gesture="pinch")
    calibration = calibrate_sequence(frames)
    payload = encode_frame(frames[0], calibration)
    assert len(payload) == PHOTON_COMPRESSED_BYTES_PER_HAND * 2


def test_decode_frame_restores_root_topology_shape() -> None:
    frames = generate_sequence(num_frames=2, seed=9, gesture="wave")
    calibration = calibrate_sequence(frames)
    payload = encode_frame(frames[1], calibration)
    decoded = decode_frame(
        payload,
        calibration=calibration,
        root_frame=frames[1],
        seq=frames[1].seq,
        timestamp_ms=frames[1].timestamp_ms,
    )
    assert len(decoded.positions) == len(frames[1].positions)
    assert len(decoded.rotations) == len(frames[1].rotations)


def test_photon_row_reports_official_bytes_and_bounded_error() -> None:
    frames = generate_sequence(num_frames=30, seed=11, gesture="mixed")
    row = measure_photon_row(frames, calibration=calibrate_sequence(frames))
    assert row["transport"]["bytes_per_frame"] == photon_fusion_measurement().bytes_per_frame
    assert row["transport"]["bytes_per_frame"] == 38.0
    assert row["fidelity"]["mpjpe_mm"] < 25.0
