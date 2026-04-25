"""Local VectorHand-compatible proxy codec for same-machine benchmarking."""

from __future__ import annotations

from dataclasses import dataclass
import math
import struct
from typing import Sequence

from .constants import HANDS, JOINTS_PER_HAND, TOTAL_JOINTS
from .models import Frame, Quat, Vec3

ULTRALEAP_VECTORHAND_NUM_BYTES = 86
ULTRALEAP_VECTORHAND_NUM_JOINT_POSITIONS = 25
ULTRALEAP_VECTORHAND_MOVEMENT_RANGE_METERS = 0.3
ULTRALEAP_PALM_POSITION_SCALE = 4096.0
ULTRALEAP_TWEAK_WRIST_POSITION: Vec3 = (0.0, -0.015, -0.065)

_HAND_ROTATIONS: tuple[Quat, ...] = ((0.0, 0.0, 0.0, 1.0),) * JOINTS_PER_HAND
_HALF_RANGE = ULTRALEAP_VECTORHAND_MOVEMENT_RANGE_METERS / 2.0
_MAX_QUAT_COMPONENT = 1.0 / math.sqrt(2.0)
_QUAT_SCALE = (1 << 10) - 1
_UINT32_STRUCT = struct.Struct("<I")
_INT16_STRUCT = struct.Struct("<h")

_THUMB_START = 2
_INDEX_START = 6
_MIDDLE_START = 11
_RING_START = 16
_LITTLE_START = 21


@dataclass(frozen=True)
class VectorHandData:
    is_left: bool
    palm_position: Vec3
    palm_rotation: Quat
    joint_positions: tuple[Vec3, ...]


def encode_frame(frame: Frame) -> bytes:
    if len(frame.positions) != TOTAL_JOINTS:
        raise ValueError(f"expected {TOTAL_JOINTS} positions, got {len(frame.positions)}")

    payload = bytearray(HANDS * ULTRALEAP_VECTORHAND_NUM_BYTES)
    offset = 0
    for hand_index in range(HANDS):
        start = hand_index * JOINTS_PER_HAND
        hand_positions = frame.positions[start : start + JOINTS_PER_HAND]
        hand = vectorhand_from_zpe_hand(hand_positions, is_left=hand_index == 0)
        offset = _fill_hand_bytes(payload, offset, hand)
    return bytes(payload)


def decode_frame(payload: bytes, *, seq: int, timestamp_ms: int) -> Frame:
    expected_bytes = HANDS * ULTRALEAP_VECTORHAND_NUM_BYTES
    if len(payload) != expected_bytes:
        raise ValueError(f"expected {expected_bytes} bytes, got {len(payload)}")

    offset = 0
    positions: list[Vec3] = []
    rotations: list[Quat] = []
    for _ in range(HANDS):
        hand, offset = _read_hand_bytes(payload, offset)
        hand_positions = zpe_hand_from_vectorhand(hand)
        positions.extend(hand_positions)
        rotations.extend(_HAND_ROTATIONS)

    return Frame(
        seq=seq,
        timestamp_ms=timestamp_ms,
        positions=tuple(positions),
        rotations=tuple(rotations),
    )


def vectorhand_from_zpe_hand(hand_positions: Sequence[Vec3], *, is_left: bool) -> VectorHandData:
    if len(hand_positions) != JOINTS_PER_HAND:
        raise ValueError(f"expected {JOINTS_PER_HAND} joints per hand, got {len(hand_positions)}")

    palm_position = _to_vec3(hand_positions[1])
    palm_rotation = estimate_palm_rotation(hand_positions, is_left=is_left)
    inverse_rotation = _quat_conjugate(palm_rotation)
    world_joints = (
        _estimate_thumb_base(hand_positions),
        *_slice_finger(hand_positions, _THUMB_START, 4),
        *_slice_finger(hand_positions, _INDEX_START, 5),
        *_slice_finger(hand_positions, _MIDDLE_START, 5),
        *_slice_finger(hand_positions, _RING_START, 5),
        *_slice_finger(hand_positions, _LITTLE_START, 5),
    )
    local_joints = tuple(
        _quat_rotate(inverse_rotation, _sub(joint, palm_position))
        for joint in world_joints
    )
    return VectorHandData(
        is_left=is_left,
        palm_position=palm_position,
        palm_rotation=palm_rotation,
        joint_positions=local_joints,
    )


def zpe_hand_from_vectorhand(hand: VectorHandData) -> tuple[Vec3, ...]:
    if len(hand.joint_positions) != ULTRALEAP_VECTORHAND_NUM_JOINT_POSITIONS:
        raise ValueError(
            f"expected {ULTRALEAP_VECTORHAND_NUM_JOINT_POSITIONS} VectorHand joints, got {len(hand.joint_positions)}"
        )

    world_joints = tuple(
        _add(hand.palm_position, _quat_rotate(hand.palm_rotation, joint))
        for joint in hand.joint_positions
    )
    wrist = _add(
        hand.palm_position,
        _quat_rotate(hand.palm_rotation, ULTRALEAP_TWEAK_WRIST_POSITION),
    )
    return (
        wrist,
        hand.palm_position,
        *world_joints[1:5],
        *world_joints[5:10],
        *world_joints[10:15],
        *world_joints[15:20],
        *world_joints[20:25],
    )


def estimate_palm_rotation(hand_positions: Sequence[Vec3], *, is_left: bool) -> Quat:
    palm = _to_vec3(hand_positions[1])
    index_base = _to_vec3(hand_positions[_INDEX_START])
    little_base = _to_vec3(hand_positions[_LITTLE_START])
    middle_base = _to_vec3(hand_positions[_MIDDLE_START])
    wrist = _to_vec3(hand_positions[0])

    across = _normalize(_sub(index_base, little_base))
    forward_seed = _normalize(_sub(middle_base, palm))
    if _is_zero(forward_seed):
        forward_seed = _normalize(_sub(palm, wrist))
    normal = _normalize(_cross(across, forward_seed))
    if _is_zero(normal):
        fallback = (-1.0, 0.0, 0.0) if is_left else (1.0, 0.0, 0.0)
        across = fallback
        normal = (0.0, 1.0, 0.0)
    forward = _normalize(_cross(normal, across))
    if _dot(forward, forward_seed) < 0.0:
        forward = _mul(forward, -1.0)
        normal = _mul(normal, -1.0)
    return _quat_from_basis(across, normal, forward)


def compress_quaternion_to_uint32(quaternion: Quat) -> int:
    components = list(_quat_normalize(quaternion))
    largest_index = max(range(4), key=lambda index: abs(components[index]))
    if components[largest_index] < 0.0:
        components = [-value for value in components]

    packed = largest_index & 0x3
    shift = 2
    for index, component in enumerate(components):
        if index == largest_index:
            continue
        normalized = (component + _MAX_QUAT_COMPONENT) / (2.0 * _MAX_QUAT_COMPONENT)
        quantized = int(round(normalized * _QUAT_SCALE))
        quantized = max(0, min(_QUAT_SCALE, quantized))
        packed |= quantized << shift
        shift += 10
    return packed


def decompress_quaternion_from_uint32(packed: int) -> Quat:
    largest_index = packed & 0x3
    shift = 2
    partials: list[float] = []
    for _ in range(3):
        quantized = (packed >> shift) & _QUAT_SCALE
        partial = (quantized / _QUAT_SCALE) * (2.0 * _MAX_QUAT_COMPONENT) - _MAX_QUAT_COMPONENT
        partials.append(partial)
        shift += 10

    components = [0.0, 0.0, 0.0, 0.0]
    partial_index = 0
    squared_sum = 0.0
    for index in range(4):
        if index == largest_index:
            continue
        value = partials[partial_index]
        partial_index += 1
        components[index] = value
        squared_sum += value * value

    components[largest_index] = math.sqrt(max(0.0, 1.0 - squared_sum))
    return _quat_normalize(tuple(components))  # type: ignore[return-value]


def float_to_byte(value: float, *, movement_range: float = ULTRALEAP_VECTORHAND_MOVEMENT_RANGE_METERS) -> int:
    clamped = max(-movement_range / 2.0, min(movement_range / 2.0, value))
    normalized = (clamped + movement_range / 2.0) / movement_range
    return int(math.floor(normalized * 255.0))


def byte_to_float(value: int, *, movement_range: float = ULTRALEAP_VECTORHAND_MOVEMENT_RANGE_METERS) -> float:
    return (float(value) / 255.0) * movement_range - (movement_range / 2.0)


def _fill_hand_bytes(buffer: bytearray, offset: int, hand: VectorHandData) -> int:
    if len(hand.joint_positions) != ULTRALEAP_VECTORHAND_NUM_JOINT_POSITIONS:
        raise ValueError(
            f"expected {ULTRALEAP_VECTORHAND_NUM_JOINT_POSITIONS} local joints, got {len(hand.joint_positions)}"
        )

    buffer[offset] = 0x00 if hand.is_left else 0x01
    offset += 1

    for component in hand.palm_position:
        _INT16_STRUCT.pack_into(buffer, offset, int(round(component * ULTRALEAP_PALM_POSITION_SCALE)))
        offset += _INT16_STRUCT.size

    _UINT32_STRUCT.pack_into(buffer, offset, compress_quaternion_to_uint32(hand.palm_rotation))
    offset += _UINT32_STRUCT.size

    for joint in hand.joint_positions:
        for component in joint:
            buffer[offset] = float_to_byte(component)
            offset += 1
    return offset


def _read_hand_bytes(payload: bytes, offset: int) -> tuple[VectorHandData, int]:
    if len(payload) - offset < ULTRALEAP_VECTORHAND_NUM_BYTES:
        raise ValueError("not enough bytes to read VectorHand payload")

    is_left = payload[offset] == 0x00
    offset += 1

    palm_position: list[float] = []
    for _ in range(3):
        palm_position.append(_INT16_STRUCT.unpack_from(payload, offset)[0] / ULTRALEAP_PALM_POSITION_SCALE)
        offset += _INT16_STRUCT.size

    palm_rotation = decompress_quaternion_from_uint32(_UINT32_STRUCT.unpack_from(payload, offset)[0])
    offset += _UINT32_STRUCT.size

    joint_positions: list[Vec3] = []
    for _ in range(ULTRALEAP_VECTORHAND_NUM_JOINT_POSITIONS):
        joint_positions.append(
            (
                byte_to_float(payload[offset]),
                byte_to_float(payload[offset + 1]),
                byte_to_float(payload[offset + 2]),
            )
        )
        offset += 3

    return (
        VectorHandData(
            is_left=is_left,
            palm_position=tuple(palm_position),  # type: ignore[arg-type]
            palm_rotation=palm_rotation,
            joint_positions=tuple(joint_positions),
        ),
        offset,
    )


def _estimate_thumb_base(hand_positions: Sequence[Vec3]) -> Vec3:
    wrist = _to_vec3(hand_positions[0])
    thumb_root = _to_vec3(hand_positions[_THUMB_START])
    return _mul(_add(wrist, thumb_root), 0.5)


def _slice_finger(hand_positions: Sequence[Vec3], start: int, count: int) -> tuple[Vec3, ...]:
    return tuple(_to_vec3(hand_positions[index]) for index in range(start, start + count))


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


def _normalize(vector: Vec3) -> Vec3:
    length = math.sqrt(_dot(vector, vector))
    if length == 0.0:
        return (0.0, 0.0, 0.0)
    return (vector[0] / length, vector[1] / length, vector[2] / length)


def _is_zero(vector: Vec3) -> bool:
    return abs(vector[0]) < 1e-9 and abs(vector[1]) < 1e-9 and abs(vector[2]) < 1e-9
