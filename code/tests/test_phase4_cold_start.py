from pathlib import Path

from zpe_xr.cold_start_audit import audit_outward_claims


def test_audit_outward_claims_passes_with_required_markers(tmp_path: Path) -> None:
    (tmp_path / "proofs").mkdir(parents=True)
    (tmp_path / "README.md").write_text("Private-stage package candidate\n", encoding="utf-8")
    (tmp_path / "PUBLIC_AUDIT_LIMITS.md").write_text("Audit boundary\n", encoding="utf-8")
    (tmp_path / "proofs" / "FINAL_STATUS.md").write_text(
        "Photon displacement remains open\nXR-C007 is `PAUSED_EXTERNAL`\n",
        encoding="utf-8",
    )
    (tmp_path / "proofs" / "RELEASE_READINESS_REPORT.md").write_text(
        "Modern Comparator Gate: `0/5 FAIL`\n",
        encoding="utf-8",
    )

    result = audit_outward_claims(tmp_path)
    assert result["pass"] is True


def test_audit_outward_claims_flags_forbidden_language(tmp_path: Path) -> None:
    (tmp_path / "proofs").mkdir(parents=True)
    (tmp_path / "README.md").write_text("Ready for public release\n", encoding="utf-8")
    (tmp_path / "PUBLIC_AUDIT_LIMITS.md").write_text("Audit boundary\n", encoding="utf-8")
    (tmp_path / "proofs" / "FINAL_STATUS.md").write_text(
        "Photon is displaced\n",
        encoding="utf-8",
    )
    (tmp_path / "proofs" / "RELEASE_READINESS_REPORT.md").write_text(
        "Modern Comparator Gate: `0/5 FAIL`\n",
        encoding="utf-8",
    )

    result = audit_outward_claims(tmp_path)
    assert result["pass"] is False
    assert result["forbidden_hits"]
