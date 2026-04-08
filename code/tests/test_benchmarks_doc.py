from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_benchmarks_doc_keeps_current_gate_and_headers() -> None:
    benchmarks = (_repo_root() / "BENCHMARKS.md").read_text(encoding="utf-8")

    assert "| dataset | metric | value |" in benchmarks
    assert "| dataset | joints | frames | ratio | MPJPE (mm) | combined latency (ms) | source |" in benchmarks
    assert "| dataset | status | evidence |" in benchmarks
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


def test_benchmarks_doc_tracks_phase3_interhand_and_access_receipt() -> None:
    root = _repo_root()
    benchmarks = (root / "BENCHMARKS.md").read_text(encoding="utf-8")
    interhand_report = (
        root
        / "proofs/artifacts/2026-04-08_zpe_xr_phase3_interhand_realdata/phase3_interhand_benchmark.md"
    ).read_text(encoding="utf-8")
    access_receipt = (
        root
        / "proofs/artifacts/2026-04-08_zpe_xr_phase3_dataset_access/dataset_access_status.md"
    ).read_text(encoding="utf-8")

    for value in ("4.244x", "0.620", "0.091"):
        assert value in benchmarks
        assert value in interhand_report

    assert "ContactPose full corpus expansion | blocked" in benchmarks
    assert "GRAB benchmark lane | blocked" in benchmarks
    assert "InterHand2.6M bilateral benchmark | complete" in benchmarks
    assert "Status: `blocked`" in access_receipt
    assert "Status: `complete`" in access_receipt
