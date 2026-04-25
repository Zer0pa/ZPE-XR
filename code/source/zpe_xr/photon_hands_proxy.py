"""Local Photon-style hand articulation proxy for same-machine benchmarking."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

from .constants import HANDS, JOINTS_PER_HAND, TOTAL_JOINTS
from .models import Frame, Quat, Vec3

PHOTON_COMPRESSED_BYTES_PER_HAND = 19
PHOTON_THUMB_SWEEP_RANGE_RAD = 1.3
PHOTON_SPREAD_RANGE_RAD = 0.6
PHOTON_CURL_RANGE_RAD = 1.45

_IDENTITY_ROTATIONS: tuple[Quat, ...] = ((0.0, 0.0, 0.0, 1.0),) * JOINTS_PER_HAND
_DEFAULT_WRIST_OFFSET: Vec3 = (0.0, -0.019, 0.0)


@dataclass(frozen=True)
class FingerSpec:
    name: str
    start: int
    count: int
    includes_spread: bool


@dataclass(frozen=True)
class FingerCalibration:
    spec: FingerSpec
    base_offset: Vec3
    segment_lengths: tuple[float, ...]
    curl_sign: float
    thumb_x_sign: float


@dataclass(frozen=True)
class HandCalibration:
    is_left: bool
    wrist_offset: Vec3
    fingers: tuple[FingerCalibration, ...]


@dataclass(frozen=True)
class SequenceCalibration:
    hands: tuple[HandCalibration, HandCalibration]


@dataclass(frozen=True)
class RootPose:
    palm_position: Vec3
    rotation: Quat


_FINGERS: tuple[FingerSpec, ...] = (
    FingerSpec(name="thumb", start=2, count=4, includes_spread=True),
    FingerSpec(name="index", start=6, count=5, includes_spread=True),
    FingerSpec(name="middle", start=11, count=5, includes_spread=False),
    FingerSpec(name="ring", start=16, count=5, includes_spread=True),
    FingerSpec(name="little", start=21, count=5, includes_spread=True),
)


def calibrate_sequence(frames: Sequence[Frame]) -> SequenceCalibration:
    if not frames:
        raise ValueError("at least one frame is required for Photon proxy calibration")

    first = frames[0]
    left_positions = first.positions[:JOINTS_PER_HAND]
    right_positions = first.positions[JOINTS_PER_HAND:]
    return SequenceCalibration(
        hands=(
            _calibrate_hand(left_positions, is_left=True),
            _calibrate_hand(right_positions, is_left=False),
        )
    )


def encode_frame(frame: Frame, calibration: SequenceCalibration) -> bytes:
    if len(frame.positions) != TOTAL_JOINTS:
        raise ValueError(f"expected {TOTAL_JOINTS} positions, got {len(frame.positions)}")

    payload = bytearray(HANDS * PHOTON_COMPRESSED_BYTES_PER_HAND)
    offset = 0
    for hand_index in range(HANDS):
        start = hand_index * JOINTS_PER_HAND
        offset = _fill_hand_payload(
            payload,
            offset,
            hand_positions=frame.positions[start : start + JOINTS_PER_HAND],
            calibration=calibration.hands[hand_index],
        )
    return bytes(payload)


def decode_frame(
    payload: bytes,
    *,
    calibration: SequenceCalibration,
    root_frame: Frame,
    seq: int,
    timestamp_ms: int,
) -> Frame:
    expected = HANDS * PHOTON_COMPRESSED_BYTES_PER_HAND
    if len(payload) != expected:
        raise ValueError(f"expected {expected} bytes, got {len(payload)}")

    positions: list[Vec3] = []
    offset = 0
    for hand_index in range(HANDS):
        start = hand_index * JOINTS_PER_HAND
        root_pose = estimate_root_pose(
            root_frame.positions[start : start + JOINTS_PER_HAND],
            is_left=calibration.hands[hand_index].is_left,
        )
        hand_positions, offset = _decode_hand_payload(
            payload,
            offset,
            calibration=calibration.hands[hand_index],
            root_pose=root_pose,
        )
        positions.extend(hand_positions)

    return Frame(
        seq=seq,
        timestamp_ms=timestamp_ms,
        positions=tuple(positions),
        rotations=_IDENTITY_ROTATIONS * HANDS,
    )


def estimate_root_pose(hand_positions: Sequence[Vec3], *, is_left: bool) -> RootPose:
    palm = _to_vec3(hand_positions[1])
    wrist = _to_vec3(hand_positions[0])
    index_base = _to_vec3(hand_positions[6])
    little_base = _to_vec3(hand_positions[21])
    middle_base = _to_vec3(hand_positions[11])

    across = _normalize(_sub(index_base, little_base))
    if _is_zero(across):
        across = (-1.0, 0.0, 0.0) if is_left else (1.0, 0.0, 0.0)

    forward_seed = _normalize(_sub(middle_base, palm))
    if _is_zero(forward_seed):
        forward_seed = _normalize(_sub(palm, wrist))
    if _is_zero(forward_seed):
        forward_seed = (0.0, 1.0, 0.0)

    normal = _normalize(_cross(across, forward_seed))
    if _is_zero(normal):
        normal = (0.0, 0.0, 1.0)

    forward = _normalize(_cross(normal, across))
    if _is_zero(forward):
        forward = (0.0, 1.0, 0.0)

    if _dot(forward, forward_seed) < 0.0:
        forward = _mul(forward, -1.0)
        normal = _mul(normal, -1.0)

    rotation = _quat_from_basis(across, forward, normal)
    return RootPose(palm_position=palm, rotation=rotation)


def localize_hand_positions(hand_positions: Sequence[Vec3], root_pose: RootPose) -> tuple[Vec3, ...]:
    inverse = _quat_conjugate(root_pose.rotation)
    return tuple(
        _quat_rotate(inverse, _sub(_to_vec3(position), root_pose.palm_position))
        for position in hand_positions
    )


def _calibrate_hand(hand_positions: Sequence[Vec3], *, is_left: bool) -> HandCalibration:
    root_pose = estimate_root_pose(hand_positions, is_left=is_left)
    local_positions = localize_hand_positions(hand_positions, root_pose)

    finger_calibrations: list[FingerCalibration] = []
    for spec in _FINGERS:
        points = local_positions[spec.start : spec.start + spec.count]
        segment_vectors = [_sub(points[index + 1], points[index]) for index in range(len(points) - 1)]
        segment_lengths = tuple(max(_length(vector), 1e-6) for vector in segment_vectors)
        z_components = [vector[2] for vector in segment_vectors if abs(vector[2]) > 1e-6]
        x_components = [vector[0] for vector in segment_vectors if abs(vector[0]) > 1e-6]
        curl_sign = 1.0 if sum(z_components) >= 0.0 else -1.0
        thumb_x_sign = 1.0 if sum(x_components) >= 0.0 else -1.0
        finger_calibrations.append(
            FingerCalibration(
                spec=spec,
                base_offset=points[0],
                segment_lengths=segment_lengths,
                curl_sign=curl_sign,
                thumb_x_sign=thumb_x_sign,
            )
        )

    wrist_offset = local_positions[0] if not _is_zero(local_positions[0]) else _DEFAULT_WRIST_OFFSET
    return HandCalibration(
        is_left=is_left,
        wrist_offset=wrist_offset,
        fingers=tuple(finger_calibrations),
    )


def _fill_hand_payload(
    payload: bytearray,
    offset: int,
    *,
    hand_positions: Sequence[Vec3],
    calibration: HandCalibration,
) -> int:
    root_pose = estimate_root_pose(hand_positions, is_left=calibration.is_left)
    local_positions = localize_hand_positions(hand_positions, root_pose)

    for finger in calibration.fingers:
        points = local_positions[finger.spec.start : finger.spec.start + finger.spec.count]
        directions = _segment_directions(points)
        if finger.spec.name == "thumb":
            sweep = _estimate_thumb_sweep(directions[0], thumb_x_sign=finger.thumb_x_sign)
            payload[offset] = _quantize_byte(sweep, low=-PHOTON_THUMB_SWEEP_RANGE_RAD, high=PHOTON_THUMB_SWEEP_RANGE_RAD)
            offset += 1
            for direction in directions:
                curl = _estimate_thumb_curl(direction, thumb_x_sign=finger.thumb_x_sign)
                payload[offset] = _quantize_byte(curl, low=0.0, high=PHOTON_CURL_RANGE_RAD)
                offset += 1
            continue

        if finger.spec.includes_spread:
            spread = _estimate_spread(directions[0])
            payload[offset] = _quantize_byte(spread, low=-PHOTON_SPREAD_RANGE_RAD, high=PHOTON_SPREAD_RANGE_RAD)
            offset += 1
        payload[offset] = _quantize_byte(_estimate_curl(directions[0]), low=0.0, high=PHOTON_CURL_RANGE_RAD)
        offset += 1
        payload[offset] = _quantize_byte(_estimate_curl(directions[1]), low=0.0, high=PHOTON_CURL_RANGE_RAD)
        offset += 1
        distal_curl = _mean((_estimate_curl(direction) for direction in directions[2:]), fallback=0.0)
        payload[offset] = _quantize_byte(distal_curl, low=0.0, high=PHOTON_CURL_RANGE_RAD)
        offset += 1

    return offset


def _decode_hand_payload(
    payload: bytes,
    offset: int,
    *,
    calibration: HandCalibration,
    root_pose: RootPose,
) -> tuple[tuple[Vec3, ...], int]:
    local_positions: list[Vec3] = [calibration.wrist_offset, (0.0, 0.0, 0.0)]

    for finger in calibration.fingers:
        if finger.spec.name == "thumb":
            sweep = _dequantize_byte(
                payload[offset],
                low=-PHOTON_THUMB_SWEEP_RANGE_RAD,
                high=PHOTON_THUMB_SWEEP_RANGE_RAD,
            )
            offset += 1
            curls = [
                _dequantize_byte(payload[offset + index], low=0.0, high=PHOTON_CURL_RANGE_RAD)
                for index in range(3)
            ]
            offset += 3
            local_positions.extend(_decode_thumb_points(finger, sweep=sweep, curls=curls))
            continue

        spread = 0.0
        if finger.spec.includes_spread:
            spread = _dequantize_byte(
                payload[offset],
                low=-PHOTON_SPREAD_RANGE_RAD,
                high=PHOTON_SPREAD_RANGE_RAD,
            )
            offset += 1
        curls = [
            _dequantize_byte(payload[offset + index], low=0.0, high=PHOTON_CURL_RANGE_RAD)
            for index in range(3)
        ]
        offset += 3
        local_positions.extend(_decode_finger_points(finger, spread=spread, curls=curls))

    if len(local_positions) != JOINTS_PER_HAND:
        raise AssertionError(f"unexpected local hand size {len(local_positions)}")

    world_positions = tuple(
        _add(root_pose.palm_position, _quat_rotate(root_pose.rotation, position))
        for position in local_positions
    )
    return world_positions, offset


def _decode_thumb_points(
    finger: FingerCalibration,
    *,
    sweep: float,
    curls: Sequence[float],
) -> tuple[Vec3, ...]:
    points = [finger.base_offset]
    sweep_factors = (1.0, 0.82, 0.64)
    for index, segment_length in enumerate(finger.segment_lengths):
        sweep_value = sweep * sweep_factors[min(index, len(sweep_factors) - 1)]
        curl_value = curls[min(index, len(curls) - 1)]
        direction = _normalize(
            (
                finger.thumb_x_sign * math.cos(sweep_value) * math.cos(curl_value),
                math.sin(sweep_value) * math.cos(curl_value),
                finger.curl_sign * math.sin(curl_value),
            )
        )
        points.append(_add(points[-1], _mul(direction, segment_length)))
    return tuple(points)


def _decode_finger_points(
    finger: FingerCalibration,
    *,
    spread: float,
    curls: Sequence[float],
) -> tuple[Vec3, ...]:
    points = [finger.base_offset]
    spread_factors = (1.0, 0.75, 0.55, 0.35)
    curl_sequence = (
        curls[0],
        curls[1],
        curls[2],
        min(PHOTON_CURL_RANGE_RAD, curls[2] + 0.12),
    )
    for index, segment_length in enumerate(finger.segment_lengths):
        spread_value = spread * spread_factors[min(index, len(spread_factors) - 1)]
        curl_value = curl_sequence[min(index, len(curl_sequence) - 1)]
        direction = _normalize(
            (
                math.sin(spread_value) * math.cos(curl_value),
                math.cos(spread_value) * math.cos(curl_value),
                finger.curl_sign * math.sin(curl_value),
            )
        )
        points.append(_add(points[-1], _mul(direction, segment_length)))
    return tuple(points)


def _segment_directions(points: Sequence[Vec3]) -> tuple[Vec3, ...]:
    return tuple(
        _normalize(_sub(points[index + 1], points[index]))
        for index in range(len(points) - 1)
    )


def _estimate_spread(direction: Vec3) -> float:
    return _clamp(math.atan2(direction[0], max(direction[1], 1e-6)), -PHOTON_SPREAD_RANGE_RAD, PHOTON_SPREAD_RANGE_RAD)


def _estimate_curl(direction: Vec3) -> float:
    return _clamp(math.atan2(abs(direction[2]), max(direction[1], 1e-6)), 0.0, PHOTON_CURL_RANGE_RAD)


def _estimate_thumb_sweep(direction: Vec3, *, thumb_x_sign: float) -> float:
    return _clamp(
        math.atan2(direction[1], max(abs(direction[0]), 1e-6)) * thumb_x_sign,
        -PHOTON_THUMB_SWEEP_RANGE_RAD,
        PHOTON_THUMB_SWEEP_RANGE_RAD,
    )


def _estimate_thumb_curl(direction: Vec3, *, thumb_x_sign: float) -> float:
    aligned_x = direction[0] * thumb_x_sign
    return _clamp(math.atan2(abs(direction[2]), max(aligned_x, 1e-6)), 0.0, PHOTON_CURL_RANGE_RAD)


def _quantize_byte(value: float, *, low: float, high: float) -> int:
    if high <= low:
        raise ValueError("invalid quantization range")
    clamped = _clamp(value, low, high)
    normalized = (clamped - low) / (high - low)
    return int(round(normalized * 255.0))


def _dequantize_byte(value: int, *, low: float, high: float) -> float:
    return low + (float(value) / 255.0) * (high - low)


def _mean(values: Sequence[float] | tuple[float, ...] | list[float] | object, *, fallback: float) -> float:
    values = list(values)
    if not values:
        return fallback
    return float(sum(values) / len(values))


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _quat_from_basis(x_axis: Vec3, y_axis: Vec3, z_axis: Vec3) -> Quat:
    m00, m01, m02 = x_axis[0], y_axis[0], z_axis[0]
    m10, m11, m12 = x_axis[1], y_axis[1], z_axis[1]
    m20, m21, m22 = x_axis[2], y_axis[2], z_axis[2]
    trace = m00 + m11 + m22
    if trace > 0.0:
        scale = math.sqrt(trace + 1.0) * 2.0
        w = 0.25 * scale
        x = (m21 - m12) / scale
        y = (m02 - m20) / scale
        z = (m10 - m01) / scale
        return _quat_normalize((x, y, z, w))
    if m00 > m11 and m00 > m22:
        scale = math.sqrt(1.0 + m00 - m11 - m22) * 2.0
        x = 0.25 * scale
        y = (m01 + m10) / scale
        z = (m02 + m20) / scale
        w = (m21 - m12) / scale
        return _quat_normalize((x, y, z, w))
    if m11 > m22:
        scale = math.sqrt(1.0 + m11 - m00 - m22) * 2.0
        x = (m01 + m10) / scale
        y = 0.25 * scale
        z = (m12 + m21) / scale
        w = (m02 - m20) / scale
        return _quat_normalize((x, y, z, w))
    scale = math.sqrt(1.0 + m22 - m00 - m11) * 2.0
    x = (m02 + m20) / scale
    y = (m12 + m21) / scale
    z = 0.25 * scale
    w = (m10 - m01) / scale
    return _quat_normalize((x, y, z, w))


def _quat_rotate(quaternion: Quat, vector: Vec3) -> Vec3:
    x, y, z, w = quaternion
    vx, vy, vz = vector
    tx = 2.0 * (y * vz - z * vy)
    ty = 2.0 * (z * vx - x * vz)
    tz = 2.0 * (x * vy - y * vx)
    return (
        vx + w * tx + (y * tz - z * ty),
        vy + w * ty + (z * tx - x * tz),
        vz + w * tz + (x * ty - y * tx),
    )


def _quat_conjugate(quaternion: Quat) -> Quat:
    x, y, z, w = quaternion
    return (-x, -y, -z, w)


def _quat_normalize(quaternion: Quat) -> Quat:
    length = math.sqrt(sum(component * component for component in quaternion))
    if length == 0.0:
        return (0.0, 0.0, 0.0, 1.0)
    return tuple(component / length for component in quaternion)  # type: ignore[return-value]


def _to_vec3(vector: Sequence[float]) -> Vec3:
    return (float(vector[0]), float(vector[1]), float(vector[2]))


def _add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _mul(vector: Vec3, scalar: float) -> Vec3:
    return (vector[0] * scalar, vector[1] * scalar, vector[2] * scalar)


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _length(vector: Vec3) -> float:
    return math.sqrt(_dot(vector, vector))


def _normalize(vector: Vec3) -> Vec3:
    length = _length(vector)
    if length == 0.0:
        return (0.0, 0.0, 0.0)
    return (vector[0] / length, vector[1] / length, vector[2] / length)


def _is_zero(vector: Vec3) -> bool:
    return abs(vector[0]) < 1e-9 and abs(vector[1]) < 1e-9 and abs(vector[2]) < 1e-9
