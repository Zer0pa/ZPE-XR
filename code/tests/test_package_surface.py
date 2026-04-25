from pathlib import Path

from zpe_xr.package_surface import (
    build_package_surface,
    build_wedge_claims,
    render_staged_files,
)


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_wedge_claims_keep_photon_open_and_runtime_paused() -> None:
    claims = build_wedge_claims(_root())
    open_ids = {item["id"] for item in claims["open_claims"]}
    assert "photon_displacement" in open_ids
    assert "runtime_closure" in open_ids


def test_package_surface_uses_non_placeholder_version() -> None:
    surface = build_package_surface(
        _root(),
        build_summary={"passed": True, "artifacts": []},
        install_smoke={"passed": True, "version": "0.3.1"},
        test_summary={"passed": True, "summary": "12 passed"},
        stage_verify={"passed": True},
    )
    assert surface["package"]["version"] != "0.0.0"
    assert surface["release_readiness"] == "PUBLISHED_PYPI"


def test_rendered_final_status_uses_fresh_artifact_chain() -> None:
    surface = build_package_surface(
        _root(),
        artifact_prefix="proofs/artifacts",
        build_summary={"passed": True, "artifacts": []},
        install_smoke={"passed": True, "version": "0.3.1"},
        test_summary={"passed": True, "summary": "12 passed"},
        stage_verify={"passed": True},
    )
    claims = build_wedge_claims(_root(), artifact_prefix="proofs/artifacts")
    rendered = render_staged_files(surface, claims)
    assert (
        "proofs/artifacts/2026-03-21_zpe_xr_phase5_multi_sequence_161900Z/phase5_multi_sequence_benchmark.json"
        in rendered["proofs/FINAL_STATUS.md"]
    )
    assert "Photon displacement remains open" in rendered["proofs/FINAL_STATUS.md"]
    assert "`XR-C007` remains `PAUSED_EXTERNAL`" in rendered["proofs/FINAL_STATUS.md"]
