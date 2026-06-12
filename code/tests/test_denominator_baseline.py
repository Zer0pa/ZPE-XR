from __future__ import annotations

import copy

import pytest

from zpe_xr.denominator_baseline import (
    DEFAULT_FRAMES_PER_SEGMENT,
    REQUIRED_MEASURED_ROW_IDS,
    DenominatorReportValidationError,
    build_denominator_report,
    validate_denominator_report,
)


def _small_report() -> dict[str, object]:
    return build_denominator_report(frames_per_segment=3, seed=1117)


def _row_by_id(segment: dict[str, object], row_id: str) -> dict[str, object]:
    rows = segment["denominator_rows"]
    assert isinstance(rows, list)
    for row in rows:
        assert isinstance(row, dict)
        if row["id"] == row_id:
            return row
    raise AssertionError(f"missing row {row_id}")


def test_denominator_rows_exist_per_segment() -> None:
    report = _small_report()

    validate_denominator_report(report)

    segments = report["segments"]
    assert isinstance(segments, list)
    assert len(segments) == 8
    for segment in segments:
        assert isinstance(segment, dict)
        row_ids = {row["id"] for row in segment["denominator_rows"]}
        assert REQUIRED_MEASURED_ROW_IDS.issubset(row_ids)
        assert "zpe_adaptive_hybrid" in row_ids
        assert _row_by_id(segment, "raw_21xyz")["status"] == "not_applicable"


def test_missing_denominator_fails_closed() -> None:
    report = _small_report()
    bad = copy.deepcopy(report)
    first_segment = bad["segments"][0]
    first_row = first_segment["denominator_rows"][0]
    del first_row["denominator"]

    with pytest.raises(DenominatorReportValidationError, match="denominator"):
        validate_denominator_report(bad)


def test_record_overhead_is_counted_separately() -> None:
    report = _small_report()
    first_segment = report["segments"][0]
    record_row = _row_by_id(first_segment, "zpe_embodiment_record")
    components = record_row["components"]

    assert components["packet_payload_bytes"] > 0
    assert components["packet_stream_container_bytes"] > components["packet_payload_bytes"]
    assert components["record_overhead_bytes"] > components["provenance_overhead_bytes"] > 0
    assert components["record_total_bytes"] == (
        components["packet_stream_container_bytes"] + components["record_overhead_bytes"]
    )


def test_surrogate_evidence_class_cannot_become_native_claim() -> None:
    report = _small_report()
    bad = copy.deepcopy(report)
    bad["native_capture_claim"] = True

    with pytest.raises(DenominatorReportValidationError, match="native_capture"):
        validate_denominator_report(bad)


def test_float16_zlib_baselines_run_on_fixture_data() -> None:
    report = build_denominator_report(frames_per_segment=DEFAULT_FRAMES_PER_SEGMENT, seed=2119)
    first_segment = report["segments"][0]
    xyz = _row_by_id(first_segment, "float16_zlib_xyz")
    xyzquat = _row_by_id(first_segment, "float16_zlib_xyzquat")

    assert xyz["bytes_total"] > 0
    assert xyz["bytes_per_frame"] > 0
    assert xyzquat["bytes_total"] > xyz["bytes_total"]
    assert xyzquat["denominator"]["coordinate_channels"] == "xyzquat"


def test_aggregate_only_report_is_rejected() -> None:
    report = _small_report()
    bad = copy.deepcopy(report)
    bad["segments"] = []
    bad["aggregate_only"] = True

    with pytest.raises(DenominatorReportValidationError, match="aggregate-only"):
        validate_denominator_report(bad)


def test_xyz_vs_xyzquat_ratio_mixing_is_rejected() -> None:
    report = _small_report()
    bad = copy.deepcopy(report)
    first_segment = bad["segments"][0]
    zpe_row = _row_by_id(first_segment, "zpe_packet_stream")
    zpe_row["compression_ratio"] = 2.0
    zpe_row["ratio_denominator_id"] = "raw_26xyzquat"

    with pytest.raises(DenominatorReportValidationError, match="xyz-vs-xyzquat"):
        validate_denominator_report(bad)


def test_adaptive_hybrid_requires_separated_bytes_or_not_available() -> None:
    report = _small_report()
    bad = copy.deepcopy(report)
    first_segment = bad["segments"][0]
    adaptive = _row_by_id(first_segment, "zpe_adaptive_hybrid")
    adaptive["status"] = "measured"
    adaptive["bytes_total"] = 125
    adaptive["bytes_per_frame"] = 41.6666666667
    adaptive["prior_reference_bytes"] = 100
    adaptive["session_delta_bytes"] = None
    adaptive["residual_stream_bytes"] = 25

    with pytest.raises(DenominatorReportValidationError, match="session_delta_bytes"):
        validate_denominator_report(bad)
