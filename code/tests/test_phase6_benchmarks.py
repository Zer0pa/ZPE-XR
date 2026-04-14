from __future__ import annotations

from pathlib import Path

from zpe_xr.constants import RAW_BYTES_PER_FRAME, TOTAL_JOINTS
from zpe_xr.external_benchmarks import photon_fusion_measurement
from zpe_xr.phase6_benchmarks import (
    benchmark_environment,
    build_transport_only_row,
    measure_modern_proxy_row,
    measure_raw_proxy_row,
)
from zpe_xr.synthetic import generate_sequence

# Raw proxy row serializes positions (3) + rotations (4) = 7 floats per joint.
# RAW_BYTES_PER_FRAME covers positions only (codec baseline).
RAW_PROXY_BYTES_PER_FRAME = TOTAL_JOINTS * 7 * 4  # 1456


def test_transport_only_row_leaves_latency_and_fidelity_null() -> None:
    row = build_transport_only_row(
        photon_fusion_measurement(),
        evidence_class="doc_derived_transport_only",
        num_frames=12,
    )

    assert row["evidence_class"] == "doc_derived_transport_only"
    assert row["latency"] is None
    assert row["fidelity"] is None
    assert row["transport"]["bytes_per_frame"] == 38.0


def test_raw_proxy_row_matches_frozen_raw_bytes() -> None:
    frames = generate_sequence(num_frames=8, seed=1901, gesture="mixed")
    row = measure_raw_proxy_row(frames=frames, iterations=2)

    assert row["evidence_class"] == "proxy_measured_local"
    assert row["transport"]["bytes_per_frame"] == RAW_PROXY_BYTES_PER_FRAME
    assert row["fidelity"]["mpjpe_mm"] == 0.0


def test_modern_proxy_row_is_locally_measured_proxy() -> None:
    frames = generate_sequence(num_frames=8, seed=2207, gesture="mixed")
    row = measure_modern_proxy_row(frames=frames, iterations=2)

    assert row["evidence_class"] == "proxy_measured_local"
    assert row["transport"]["bytes_per_frame"] > 0.0
    assert row["latency"]["combined_avg_ms_per_frame"] > 0.0


def test_benchmark_environment_flags_missing_root_modules_for_stage_code_root() -> None:
    stage_code_root = Path(__file__).resolve().parents[1]
    environment = benchmark_environment(stage_code_root)

    assert environment["staged_package_backend"] in {"python", "rust"}
    assert environment["root_execution_surface"]["status"] in {"runnable", "incomplete"}
