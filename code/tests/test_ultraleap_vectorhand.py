from zpe_xr.constants import RAW_BYTES_PER_FRAME
from zpe_xr.external_benchmarks import ultraleap_vectorhand_measurement
from zpe_xr.phase7_ultraleap_benchmarks import measure_ultraleap_row
from zpe_xr.synthetic import generate_sequence
from zpe_xr.ultraleap_vectorhand import (
    ULTRALEAP_VECTORHAND_NUM_BYTES,
    byte_to_float,
    decode_frame,
    encode_frame,
    float_to_byte,
)


def test_float_byte_roundtrip_stays_within_expected_bucket() -> None:
    quantized = float_to_byte(0.03125)
    restored = byte_to_float(quantized)
    assert abs(restored - 0.03125) <= 0.002


def test_encode_frame_uses_fixed_vectorhand_width() -> None:
    frame = generate_sequence(num_frames=1, seed=7, gesture="pinch")[0]
    payload = encode_frame(frame)
    assert len(payload) == ULTRALEAP_VECTORHAND_NUM_BYTES * 2


def test_decode_frame_restores_root_topology_shape() -> None:
    frame = generate_sequence(num_frames=1, seed=9, gesture="wave")[0]
    payload = encode_frame(frame)
    decoded = decode_frame(payload, seq=frame.seq, timestamp_ms=frame.timestamp_ms)
    assert len(decoded.positions) == len(frame.positions)
    assert len(decoded.rotations) == len(frame.rotations)


def test_ultraleap_row_reports_official_bytes_and_bounded_error() -> None:
    frames = generate_sequence(num_frames=30, seed=11, gesture="mixed")
    row = measure_ultraleap_row(frames, measurement=ultraleap_vectorhand_measurement())
    assert row["transport"]["bytes_per_frame"] == 172.0
    assert row["transport"]["compression_ratio_vs_raw"] == RAW_BYTES_PER_FRAME / 172.0
    assert row["fidelity"]["mpjpe_mm"] < 5.0
