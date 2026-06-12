from __future__ import annotations

from zpe_xr.headset_surrogate import (
    build_headset_surrogate_manifest,
    classify_surrogate_dataset,
    headset_surrogate_specs,
)


def test_surrogate_catalog_preserves_evidence_ladder() -> None:
    specs = {spec.dataset_id: spec for spec in headset_surrogate_specs()}

    assert specs["synthetic_openxr_fixture"].evidence_class == "synthetic_openxr_fixture"
    assert specs["kine_adl_be_uji"].evidence_class == "green_movement_prior"
    assert specs["holoassist"].evidence_class == "headset_proxy_permissive"
    assert specs["hot3d"].evidence_class == "headset_proxy_restricted"
    assert specs["egodex"].forbidden_use.startswith("Commercial authority")


def test_surrogate_manifest_keeps_native_capture_pending() -> None:
    manifest = build_headset_surrogate_manifest()

    assert manifest["native_capture_status"] == "pending"
    assert "native_device_capture" in manifest["evidence_classes"]
    assert "non-sovereign" in manifest["native_capture_gate"]


def test_classify_surrogate_dataset_returns_official_url_anchor() -> None:
    spec = classify_surrogate_dataset("holoassist")

    assert spec.official_url == "https://holoassist.github.io/"
    assert spec.evidence_class == "headset_proxy_permissive"
