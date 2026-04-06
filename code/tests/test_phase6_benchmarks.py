from __future__ import annotations

from pathlib import Path

from zpe_xr.constants import RAW_BYTES_PER_FRAME
from zpe_xr.external_benchmarks import photon_fusion_measurement
import zpe_xr.phase6_benchmarks as phase6_benchmarks
from zpe_xr.phase6_benchmarks import (
    _REQUIRED_ROOT_MODULES,
    _transport_metrics,
    attempt_contactpose_report,
    benchmark_report,
    benchmark_environment,
    build_transport_only_row,
    measure_modern_proxy_row,
    measure_raw_proxy_row,
)
from zpe_xr.synthetic import generate_sequence


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
    assert row["transport"]["bytes_per_frame"] == RAW_BYTES_PER_FRAME
    assert row["fidelity"]["mpjpe_mm"] == 0.0


def test_transport_metrics_handles_zero_bytes_total() -> None:
    metrics = _transport_metrics(bytes_total=0, num_frames=10)

    assert metrics["compression_ratio_vs_raw"] == 0.0
    assert metrics["kb_per_s_single_remote"] == 0.0
    assert metrics["kb_per_s_modeled_4_player_session"] == 0.0


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


def test_benchmark_report_skips_contactpose_when_disabled() -> None:
    stage_code_root = Path(__file__).resolve().parents[1]
    report = benchmark_report(
        stage_code_root=stage_code_root,
        num_frames=8,
        gesture="mixed",
        seed=31415,
        iterations=1,
        attempt_contactpose=False,
    )

    assert report["contactpose_attempt"]["status"] == "skipped"
    assert len(report["rows"]) == 6
    assert any(row["comparator_id"] == "zpe_xr_current_mac" for row in report["rows"])
    assert report["conclusions"]


def test_benchmark_report_handles_zero_frames_and_iterations() -> None:
    stage_code_root = Path(__file__).resolve().parents[1]
    report = benchmark_report(
        stage_code_root=stage_code_root,
        num_frames=0,
        gesture="mixed",
        seed=42,
        iterations=0,
        attempt_contactpose=False,
    )

    zpe_row = report["rows"][0]
    assert zpe_row["transport"]["bytes_per_frame"] == 0.0
    assert zpe_row["latency"]["combined_avg_ms_per_frame"] == 0.0
    assert report["contactpose_attempt"]["status"] == "skipped"


def test_attempt_contactpose_report_blocked_on_error(monkeypatch, tmp_path: Path) -> None:
    def _raise_in_contactpose(*args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        raise RuntimeError("synthetic ContactPose failure")

    monkeypatch.setattr(phase6_benchmarks, "ensure_contactpose_sample", _raise_in_contactpose)

    report = attempt_contactpose_report(tmp_path / "code")

    assert report["status"] == "blocked"
    assert report["error_type"] == "RuntimeError"
    assert "synthetic ContactPose failure" in report["reason"]


def test_benchmark_environment_incomplete_when_root_missing_required_modules(tmp_path: Path) -> None:
    environment = benchmark_environment(tmp_path)

    root_surface = environment["root_execution_surface"]
    assert root_surface["status"] == "incomplete"
    assert set(root_surface["missing_modules"]) == set(_REQUIRED_ROOT_MODULES)


def test_benchmark_environment_runnable_when_all_required_root_modules_present(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "zpe_xr"
    src_root.mkdir(parents=True, exist_ok=True)
    for module_name in _REQUIRED_ROOT_MODULES:
        (src_root / module_name).write_text("# test module\n", encoding="utf-8")

    environment = benchmark_environment(tmp_path)

    root_surface = environment["root_execution_surface"]
    assert root_surface["status"] == "runnable"
    assert root_surface["missing_modules"] == []
