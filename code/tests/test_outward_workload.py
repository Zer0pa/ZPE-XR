import zipfile

from zpe_xr.contactpose_adapter import ContactPoseSequenceMeta
from zpe_xr.outward_workload import (
    CONTACTPOSE_SAMPLE_FILENAME,
    build_outward_acceptance,
    ensure_contactpose_sample,
    select_best_contactpose_candidate,
)


def test_select_best_contactpose_candidate_prefers_longer_sequence() -> None:
    shorter = ContactPoseSequenceMeta(
        archive_member="a/annotations.json",
        frame_count=45,
        valid_hands=(0, 1),
        object_name="cup",
    )
    longer = ContactPoseSequenceMeta(
        archive_member="b/annotations.json",
        frame_count=90,
        valid_hands=(0, 1),
        object_name="bottle",
    )
    assert select_best_contactpose_candidate([shorter, longer]) == longer


def test_build_outward_acceptance_uses_sovereign_checks() -> None:
    acceptance = build_outward_acceptance(
        compression_metrics={
            "compression_ratio_vs_raw": 12.0,
            "modern_comparator": {"ratio_vs_zpe": 0.8},
        },
        fidelity_metrics={"pass": True},
        latency_metrics={"pass": True},
        packet_loss_metrics={"pass": True},
    )
    assert acceptance["sovereign_pass"] is True
    assert acceptance["secondary_checks"]["modern_comparator_beaten"] is False
    assert acceptance["verdict"] == "PASS"


def test_build_outward_acceptance_fails_when_quality_floor_breaks() -> None:
    acceptance = build_outward_acceptance(
        compression_metrics={
            "compression_ratio_vs_raw": 12.0,
            "modern_comparator": {"ratio_vs_zpe": 1.5},
        },
        fidelity_metrics={"pass": False},
        latency_metrics={"pass": True},
        packet_loss_metrics={"pass": True},
    )
    assert acceptance["sovereign_pass"] is False
    assert acceptance["verdict"] == "FAIL"


def test_ensure_contactpose_sample_reuses_existing_archive(tmp_path) -> None:
    search_root = tmp_path / "artifacts"
    existing = search_root / "historical" / "downloads" / CONTACTPOSE_SAMPLE_FILENAME
    existing.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(existing, "w") as archive:
        archive.writestr("placeholder.txt", "ok")

    destination = tmp_path / "fresh" / "downloads" / CONTACTPOSE_SAMPLE_FILENAME
    reused = ensure_contactpose_sample(destination)

    assert reused == existing.resolve()
    assert not destination.exists()


def test_ensure_contactpose_sample_honors_explicit_search_root(tmp_path) -> None:
    search_root = tmp_path / "shared"
    existing = search_root / "archive" / CONTACTPOSE_SAMPLE_FILENAME
    existing.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(existing, "w") as archive:
        archive.writestr("placeholder.txt", "ok")

    destination = tmp_path / "fresh" / "downloads" / CONTACTPOSE_SAMPLE_FILENAME
    reused = ensure_contactpose_sample(destination, search_root=search_root)

    assert reused == existing.resolve()
    assert not destination.exists()
