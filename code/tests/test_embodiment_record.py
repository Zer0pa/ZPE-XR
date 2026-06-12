from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from zpe_xr.embodiment_record import (
    CAPTURE_EVIDENCE_CLASSES,
    EmbodimentRecordValidationError,
    is_native_capture_verified,
    validate_embodiment_record,
    validate_real_headset_capture_manifest,
)


def _fixtures_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures"


def _load_fixture(name: str) -> dict[str, object]:
    with (_fixtures_dir() / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_valid_surrogate_embodiment_record_passes_but_is_not_native() -> None:
    payload = _load_fixture("embodiment_record_valid_surrogate_v1.json")

    validate_embodiment_record(payload)

    assert not is_native_capture_verified(payload)
    assert payload["capture"]["evidence_class"] == "synthetic_openxr_fixture"
    assert "native_device_capture" in CAPTURE_EVIDENCE_CLASSES


def test_capture_manifest_requires_openxr_shape_and_motion_protocol() -> None:
    payload = _load_fixture("embodiment_record_valid_surrogate_v1.json")

    validate_real_headset_capture_manifest(payload["capture"])

    segments = {segment["id"] for segment in payload["capture"]["motion_protocol"]["segments"]}
    assert "hand_controller_transition_or_tracking_loss" in segments


def test_crc32_cannot_satisfy_record_provenance() -> None:
    payload = _load_fixture("embodiment_record_invalid_crc_provenance_v1.json")

    with pytest.raises(EmbodimentRecordValidationError, match="CRC32 transport checksums"):
        validate_embodiment_record(payload)


def test_evidence_class_is_required() -> None:
    payload = _load_fixture("embodiment_record_valid_surrogate_v1.json")
    missing = copy.deepcopy(payload)
    del missing["capture"]["evidence_class"]

    with pytest.raises(EmbodimentRecordValidationError, match="capture.evidence_class"):
        validate_embodiment_record(missing)


def test_non_native_record_cannot_claim_native_verified() -> None:
    payload = _load_fixture("embodiment_record_valid_surrogate_v1.json")
    bad = copy.deepcopy(payload)
    bad["capture"]["native_capture_status"] = "native_verified"

    with pytest.raises(EmbodimentRecordValidationError, match="only native_device_capture"):
        validate_embodiment_record(bad)
