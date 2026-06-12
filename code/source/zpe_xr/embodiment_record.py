"""Fail-closed validation for ZPE-XR capture and EmbodimentRecord manifests."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
import re
from typing import Any

from .constants import HANDS, JOINTS_PER_HAND, TOTAL_JOINTS

REAL_HEADSET_CAPTURE_SCHEMA = "zpe-xr-real-headset-capture-1"
EMBODIMENT_RECORD_SCHEMA = "zpe-xr-embodiment-record-1"

CAPTURE_EVIDENCE_CLASSES = (
    "synthetic_openxr_fixture",
    "green_movement_prior",
    "headset_proxy_permissive",
    "headset_proxy_restricted",
    "native_device_capture",
)

NATIVE_CAPTURE_STATUSES = (
    "not_applicable",
    "pending",
    "pilot_not_sovereign",
    "native_verified",
)

REQUIRED_MOTION_SEGMENTS = frozenset(
    {
        "static_hold",
        "slow_manipulation",
        "active_reaching",
        "fast_translation",
        "pointing",
        "grasp_release",
        "occlusion_jitter",
        "hand_controller_transition_or_tracking_loss",
    }
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class EmbodimentRecordValidationError(ValueError):
    """Raised when a capture manifest or EmbodimentRecord fails validation."""


def validate_real_headset_capture_manifest(payload: Mapping[str, Any]) -> None:
    """Validate the capture manifest embedded in an EmbodimentRecord."""

    capture = _require_mapping(payload, "capture")
    _require_const(capture, "schema", REAL_HEADSET_CAPTURE_SCHEMA, "capture.schema")
    _require_string(capture, "capture_id", "capture.capture_id")

    evidence_class = _require_string(capture, "evidence_class", "capture.evidence_class")
    native_status = _require_string(capture, "native_capture_status", "capture.native_capture_status")
    _validate_evidence_status(evidence_class, native_status, "capture")

    _validate_source(capture)
    _validate_device_runtime(capture)
    _validate_joint_layout(capture)
    _validate_timebase(capture)
    _validate_coordinate_frames(capture)
    _validate_motion_protocol(capture)
    _validate_validity_flags(capture)


def validate_embodiment_record(payload: Mapping[str, Any]) -> None:
    """Validate an EmbodimentRecord without pulling in a JSON Schema dependency."""

    record = _require_mapping(payload, "record")
    _require_const(record, "schema", EMBODIMENT_RECORD_SCHEMA, "schema")
    _require_string(record, "record_id", "record_id")
    _require_string(record, "created_at_utc", "created_at_utc")

    validate_real_headset_capture_manifest(_require_mapping_field(record, "capture", "capture"))
    _validate_source_license(record)
    _validate_calibration_policy(record)
    _validate_frames(record)
    _validate_packet_stream(record)
    _validate_provenance(record)
    _validate_decoder(record)
    _validate_replay(record)
    _validate_privacy(record)


def is_native_capture_verified(payload: Mapping[str, Any]) -> bool:
    """Return true only when the record explicitly carries native verified capture."""

    record = _require_mapping(payload, "record")
    capture = _require_mapping_field(record, "capture", "capture")
    return (
        capture.get("evidence_class") == "native_device_capture"
        and capture.get("native_capture_status") == "native_verified"
    )


def _validate_evidence_status(evidence_class: str, native_status: str, path: str) -> None:
    if evidence_class not in CAPTURE_EVIDENCE_CLASSES:
        _fail(f"{path}.evidence_class", f"unsupported evidence class {evidence_class!r}")
    if native_status not in NATIVE_CAPTURE_STATUSES:
        _fail(f"{path}.native_capture_status", f"unsupported native capture status {native_status!r}")
    if native_status == "native_verified" and evidence_class != "native_device_capture":
        _fail(
            f"{path}.native_capture_status",
            "only native_device_capture records can be native_verified",
        )
    if evidence_class == "native_device_capture" and native_status == "not_applicable":
        _fail(
            f"{path}.native_capture_status",
            "native_device_capture records must be pending, pilot_not_sovereign, or native_verified",
        )


def _validate_source(capture: Mapping[str, Any]) -> None:
    source = _require_mapping_field(capture, "source", "capture.source")
    _require_string(source, "name", "capture.source.name")
    _require_string(source, "capture_mode", "capture.source.capture_mode")


def _validate_device_runtime(capture: Mapping[str, Any]) -> None:
    runtime = _require_mapping_field(capture, "device_runtime", "capture.device_runtime")
    for key in ("device_class", "provider", "runtime", "api"):
        _require_string(runtime, key, f"capture.device_runtime.{key}")


def _validate_joint_layout(capture: Mapping[str, Any]) -> None:
    layout = _require_mapping_field(capture, "joint_layout", "capture.joint_layout")
    _require_const(layout, "standard", "openxr_ext_hand_tracking", "capture.joint_layout.standard")
    _require_const(layout, "joints_per_hand", JOINTS_PER_HAND, "capture.joint_layout.joints_per_hand")
    _require_const(layout, "total_joints", TOTAL_JOINTS, "capture.joint_layout.total_joints")

    hands = _require_sequence(layout, "hands", "capture.joint_layout.hands")
    if tuple(hands) != ("left", "right"):
        _fail("capture.joint_layout.hands", "must be ['left', 'right']")


def _validate_timebase(capture: Mapping[str, Any]) -> None:
    timebase = _require_mapping_field(capture, "timebase", "capture.timebase")
    sample_rate = _require_number(timebase, "sample_rate_hz", "capture.timebase.sample_rate_hz")
    if sample_rate <= 0:
        _fail("capture.timebase.sample_rate_hz", "must be > 0")

    timestamp_unit = _require_string(timebase, "source_timestamp_unit", "capture.timebase.source_timestamp_unit")
    if timestamp_unit not in {"ns", "us", "ms"}:
        _fail("capture.timebase.source_timestamp_unit", "must be one of ns, us, ms")

    frame_index_base = _require_integer(timebase, "frame_index_base", "capture.timebase.frame_index_base")
    if frame_index_base < 0:
        _fail("capture.timebase.frame_index_base", "must be >= 0")


def _validate_coordinate_frames(capture: Mapping[str, Any]) -> None:
    frames = _require_mapping_field(capture, "coordinate_frames", "capture.coordinate_frames")
    for key in ("source_frame", "storage_frame", "units", "handedness"):
        _require_string(frames, key, f"capture.coordinate_frames.{key}")
    if frames["units"] != "meters":
        _fail("capture.coordinate_frames.units", "must be meters")
    if frames["handedness"] not in {"left", "right"}:
        _fail("capture.coordinate_frames.handedness", "must be left or right")


def _validate_motion_protocol(capture: Mapping[str, Any]) -> None:
    protocol = _require_mapping_field(capture, "motion_protocol", "capture.motion_protocol")
    segments = _require_sequence(protocol, "segments", "capture.motion_protocol.segments")
    segment_ids = set()
    for index, segment_obj in enumerate(segments):
        segment = _require_mapping(segment_obj, f"capture.motion_protocol.segments[{index}]")
        segment_id = _require_string(segment, "id", f"capture.motion_protocol.segments[{index}].id")
        duration = _require_number(segment, "duration_s", f"capture.motion_protocol.segments[{index}].duration_s")
        if duration <= 0:
            _fail(f"capture.motion_protocol.segments[{index}].duration_s", "must be > 0")
        segment_ids.add(segment_id)

    missing = REQUIRED_MOTION_SEGMENTS - segment_ids
    if missing:
        _fail("capture.motion_protocol.segments", f"missing required segments: {sorted(missing)}")


def _validate_validity_flags(capture: Mapping[str, Any]) -> None:
    flags = _require_sequence(capture, "validity_flags", "capture.validity_flags")
    required = {"position_valid", "orientation_valid", "tracked"}
    if not required.issubset(set(flags)):
        _fail("capture.validity_flags", f"must include {sorted(required)}")


def _validate_source_license(record: Mapping[str, Any]) -> None:
    license_info = _require_mapping_field(record, "source_license", "source_license")
    _require_string(license_info, "name", "source_license.name")
    commercial_use = _require_string(license_info, "commercial_use", "source_license.commercial_use")
    if commercial_use not in {"allowed", "restricted", "not_applicable", "unknown"}:
        _fail("source_license.commercial_use", "unsupported commercial use value")


def _validate_calibration_policy(record: Mapping[str, Any]) -> None:
    policy = _require_mapping_field(record, "calibration_prior_policy", "calibration_prior_policy")
    for key in ("population_prior", "session_delta", "residual_stream"):
        _require_string(policy, key, f"calibration_prior_policy.{key}")


def _validate_frames(record: Mapping[str, Any]) -> None:
    frames = _require_sequence(record, "frames", "frames")
    if not frames:
        _fail("frames", "must contain at least one frame")

    for index, frame_obj in enumerate(frames):
        frame = _require_mapping(frame_obj, f"frames[{index}]")
        frame_index = _require_integer(frame, "frame_index", f"frames[{index}].frame_index")
        timestamp = _require_integer(frame, "source_timestamp_ns", f"frames[{index}].source_timestamp_ns")
        if frame_index < 0 or timestamp < 0:
            _fail(f"frames[{index}]", "frame_index and source_timestamp_ns must be nonnegative")
        _validate_frame_hands(frame, index)


def _validate_frame_hands(frame: Mapping[str, Any], frame_index: int) -> None:
    hands = _require_sequence(frame, "hands", f"frames[{frame_index}].hands")
    if len(hands) != HANDS:
        _fail(f"frames[{frame_index}].hands", f"must contain {HANDS} hands")

    seen = set()
    for hand_index, hand_obj in enumerate(hands):
        path = f"frames[{frame_index}].hands[{hand_index}]"
        hand = _require_mapping(hand_obj, path)
        handedness = _require_string(hand, "handedness", f"{path}.handedness")
        joint_count = _require_integer(hand, "joint_count", f"{path}.joint_count")
        _require_mapping_field(hand, "joint_validity_summary", f"{path}.joint_validity_summary")
        if handedness not in {"left", "right"}:
            _fail(f"{path}.handedness", "must be left or right")
        if joint_count != JOINTS_PER_HAND:
            _fail(f"{path}.joint_count", f"must be {JOINTS_PER_HAND}")
        seen.add(handedness)

    if seen != {"left", "right"}:
        _fail(f"frames[{frame_index}].hands", "must contain one left and one right hand")


def _validate_packet_stream(record: Mapping[str, Any]) -> None:
    stream = _require_mapping_field(record, "packet_stream", "packet_stream")
    _require_string(stream, "encoding", "packet_stream.encoding")
    packet_count = _require_integer(stream, "packet_count", "packet_stream.packet_count")
    if packet_count < 1:
        _fail("packet_stream.packet_count", "must be >= 1")
    _require_sha256(stream, "packet_sha256", "packet_stream.packet_sha256")
    _require_const(stream, "transport_checksum_kind", "crc32", "packet_stream.transport_checksum_kind")
    checksums = _require_sequence(stream, "transport_checksums", "packet_stream.transport_checksums")
    if not checksums:
        _fail("packet_stream.transport_checksums", "must not be empty")


def _validate_provenance(record: Mapping[str, Any]) -> None:
    provenance = _require_mapping_field(record, "provenance", "provenance")
    record_alg = _require_string(provenance, "record_digest_alg", "provenance.record_digest_alg").lower()
    chain_alg = _require_string(provenance, "packet_hash_chain_alg", "provenance.packet_hash_chain_alg").lower()

    if record_alg == "crc32" or chain_alg == "crc32":
        _fail("provenance", "CRC32 transport checksums cannot satisfy cryptographic record provenance")
    if record_alg != "sha256":
        _fail("provenance.record_digest_alg", "must be sha256")
    if chain_alg != "sha256":
        _fail("provenance.packet_hash_chain_alg", "must be sha256")

    _require_sha256(provenance, "record_digest_sha256", "provenance.record_digest_sha256")
    chain = _require_sequence(provenance, "packet_hash_chain", "provenance.packet_hash_chain")
    if not chain:
        _fail("provenance.packet_hash_chain", "must not be empty")
    for index, digest in enumerate(chain):
        _validate_sha256_value(digest, f"provenance.packet_hash_chain[{index}]")


def _validate_decoder(record: Mapping[str, Any]) -> None:
    decoder = _require_mapping_field(record, "decoder", "decoder")
    for key in ("name", "version", "kernel"):
        _require_string(decoder, key, f"decoder.{key}")


def _validate_replay(record: Mapping[str, Any]) -> None:
    replay = _require_mapping_field(record, "replay", "replay")
    required = _require_bool(replay, "byte_identical_replay_required", "replay.byte_identical_replay_required")
    if not required:
        _fail("replay.byte_identical_replay_required", "must be true for Phase 3 records")
    _require_const(replay, "replay_digest_alg", "sha256", "replay.replay_digest_alg")
    _require_sha256(replay, "replay_digest_sha256", "replay.replay_digest_sha256")
    _require_string(replay, "renderer", "replay.renderer")


def _validate_privacy(record: Mapping[str, Any]) -> None:
    privacy = _require_mapping_field(record, "privacy", "privacy")
    fields = _require_sequence(privacy, "biometric_fields", "privacy.biometric_fields")
    if not fields:
        _fail("privacy.biometric_fields", "must name biometric-like fields")
    for key in (
        "calibration_window_retention",
        "session_delta_retention",
        "deletion_policy",
        "external_sharing",
    ):
        _require_string(privacy, key, f"privacy.{key}")


def _require_mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(path, "must be an object")
    return value


def _require_mapping_field(mapping: Mapping[str, Any], key: str, path: str) -> Mapping[str, Any]:
    return _require_mapping(_require_value(mapping, key, path), path)


def _require_value(mapping: Mapping[str, Any], key: str, path: str) -> Any:
    if key not in mapping:
        _fail(path, "is required")
    return mapping[key]


def _require_const(mapping: Mapping[str, Any], key: str, expected: Any, path: str) -> None:
    actual = _require_value(mapping, key, path)
    if actual != expected:
        _fail(path, f"must be {expected!r}")


def _require_string(mapping: Mapping[str, Any], key: str, path: str) -> str:
    value = _require_value(mapping, key, path)
    if not isinstance(value, str) or not value:
        _fail(path, "must be a non-empty string")
    return value


def _require_integer(mapping: Mapping[str, Any], key: str, path: str) -> int:
    value = _require_value(mapping, key, path)
    if isinstance(value, bool) or not isinstance(value, int):
        _fail(path, "must be an integer")
    return value


def _require_number(mapping: Mapping[str, Any], key: str, path: str) -> float:
    value = _require_value(mapping, key, path)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        _fail(path, "must be a finite number")
    return float(value)


def _require_bool(mapping: Mapping[str, Any], key: str, path: str) -> bool:
    value = _require_value(mapping, key, path)
    if not isinstance(value, bool):
        _fail(path, "must be a boolean")
    return value


def _require_sequence(mapping: Mapping[str, Any], key: str, path: str) -> Sequence[Any]:
    value = _require_value(mapping, key, path)
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        _fail(path, "must be an array")
    return value


def _require_sha256(mapping: Mapping[str, Any], key: str, path: str) -> str:
    digest = _require_string(mapping, key, path)
    _validate_sha256_value(digest, path)
    return digest


def _validate_sha256_value(value: Any, path: str) -> None:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        _fail(path, "must be a lowercase SHA-256 hex digest")


def _fail(path: str, message: str) -> None:
    raise EmbodimentRecordValidationError(f"{path}: {message}")
