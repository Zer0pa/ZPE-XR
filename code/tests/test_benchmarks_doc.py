from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_benchmarks_doc_keeps_current_gate_and_headers() -> None:
    benchmarks = (_repo_root() / "BENCHMARKS.md").read_text(encoding="utf-8")

    assert "| dataset | metric | value |" in benchmarks
    assert "| dataset | joints | frames | ratio | MPJPE (mm) | combined latency (ms) | source |" in benchmarks
    assert "Modern comparator gate: `0/5`" in benchmarks
    assert "Public release posture: `PRIVATE_ONLY`" in benchmarks


def test_benchmarks_doc_matches_phase5_contactpose_anchor() -> None:
    root = _repo_root()
    benchmarks = (root / "BENCHMARKS.md").read_text(encoding="utf-8")
    phase5 = (
        root
        / "proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.md"
    ).read_text(encoding="utf-8")

    for value in ("56.144x", "0.479", "0.026"):
        assert value in benchmarks
        assert value in phase5
