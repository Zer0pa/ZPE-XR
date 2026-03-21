"""Helpers for bounded ContactPose ingestion in Phase 2."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from io import BytesIO
import json
from pathlib import Path
import tempfile
from typing import Any, Iterable, List, Sequence, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import zipfile

from .constants import FPS
from .models import Frame, Quat, Vec3


CONTACTPOSE_SAMPLE_FILE_ID = "1paUAxXgHp6wDFBFw9MI1mxGElEl2KPew"
CONTACTPOSE_SAMPLE_PAGE = (
    "https://drive.google.com/uc?export=download&id=" + CONTACTPOSE_SAMPLE_FILE_ID
)
IDENTITY_QUATERNION: Quat = (0.0, 0.0, 0.0, 1.0)
_NESTED_MEMBER_SEPARATOR = "::"


@dataclass(frozen=True)
class ContactPoseSequenceMeta:
    archive_member: str
    frame_count: int
    valid_hands: Tuple[int, ...]
    object_name: str


def contactpose_21_to_zpe_xr_26(hand_joints: Sequence[Sequence[float]]) -> Tuple[Vec3, ...]:
    if len(hand_joints) != 21:
        raise ValueError(f"expected 21 joints, got {len(hand_joints)}")

    joints = [tuple(float(value) for value in joint[:3]) for joint in hand_joints]
    wrist = joints[0]
    palm_sources = [wrist, joints[1], joints[5], joints[9], joints[13], joints[17]]
    palm = _mean_vec3(palm_sources)

    converted: List[Vec3] = [wrist, palm]
    converted.extend(joints[1:5])

    for start in (5, 9, 13, 17):
        finger = joints[start : start + 4]
        metacarpal = _midpoint(palm, finger[0])
        converted.append(metacarpal)
        converted.extend(finger)

    if len(converted) != 26:
        raise AssertionError(f"unexpected converted joint count: {len(converted)}")

    return tuple(converted)


def annotation_candidates_from_zip(
    zip_path: Path,
    *,
    min_frames: int = 45,
    require_both_hands: bool = True,
) -> List[ContactPoseSequenceMeta]:
    candidates: List[ContactPoseSequenceMeta] = []

    with zipfile.ZipFile(zip_path) as archive:
        candidates.extend(
            _annotation_candidates_from_members(
                archive,
                min_frames=min_frames,
                require_both_hands=require_both_hands,
            )
        )
        if candidates:
            return candidates

        grasps_member = _find_grasps_bundle_member(archive)
        if grasps_member is None:
            return candidates

        with _open_nested_zip_from_archive(archive, grasps_member) as grasps_archive:
            for member in grasps_archive.namelist():
                if not _is_grasp_zip_member(member):
                    continue
                with _open_nested_zip_from_archive(grasps_archive, member) as grasp_archive:
                    for nested_candidate in _annotation_candidates_from_members(
                        grasp_archive,
                        min_frames=min_frames,
                        require_both_hands=require_both_hands,
                    ):
                        candidates.append(
                            ContactPoseSequenceMeta(
                                archive_member=_join_nested_member(
                                    grasps_member,
                                    member,
                                    nested_candidate.archive_member,
                                ),
                                frame_count=nested_candidate.frame_count,
                                valid_hands=nested_candidate.valid_hands,
                                object_name=nested_candidate.object_name,
                            )
                        )

    return candidates


def build_zpe_frames_from_annotation(
    annotation: dict[str, Any],
    *,
    max_frames: int = 90,
) -> Tuple[Frame, ...]:
    frames = annotation.get("frames", [])
    hands = annotation.get("hands", [])
    if len(hands) < 2:
        raise ValueError("annotation does not contain two hand slots")

    valid_hands = [idx for idx, hand in enumerate(hands) if hand.get("valid")]
    if len(valid_hands) < 2:
        raise ValueError("annotation does not contain two valid hands")

    canonical_hands: List[List[Vec3]] = []
    for hand_idx, hand in enumerate(hands[:2]):
        if not hand.get("valid"):
            raise ValueError("annotation lost a required hand")
        canonical_hands.append(
            [tuple(float(value) for value in joint[:3]) for joint in hand["joints"]]
        )

    converted_frames: List[Frame] = []
    for seq, frame in enumerate(frames[:max_frames]):
        positions: List[Vec3] = []
        for hand_idx in range(2):
            transformed = _contactpose_object_space_joints(
                canonical_hands[hand_idx],
                hands[hand_idx],
                frame,
                hand_idx,
            )
            positions.extend(contactpose_21_to_zpe_xr_26(transformed))

        rotations = tuple(IDENTITY_QUATERNION for _ in range(len(positions)))
        converted_frames.append(
            Frame(
                seq=seq,
                timestamp_ms=int(round((1000.0 / FPS) * seq)),
                positions=tuple(positions),
                rotations=rotations,
            )
        )

    return tuple(converted_frames)


def download_contactpose_sample_zip(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(CONTACTPOSE_SAMPLE_PAGE, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="ignore")

    action = _extract_form_action(html)
    if action is None:
        raise RuntimeError("ContactPose Google Drive confirm form not found")

    params = _extract_hidden_inputs(html)
    params.setdefault("id", CONTACTPOSE_SAMPLE_FILE_ID)
    params.setdefault("export", "download")
    params.setdefault("confirm", "t")

    download_url = f"{action}?{urlencode(params)}"
    req = Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=60) as response, destination.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    return destination


def read_annotation_from_zip(zip_path: Path, member: str) -> dict[str, Any]:
    with zipfile.ZipFile(zip_path) as archive:
        nested_members = member.split(_NESTED_MEMBER_SEPARATOR)
        if len(nested_members) == 1:
            with archive.open(member) as handle:
                return json.load(handle)
        if len(nested_members) != 3:
            raise ValueError(f"unsupported ContactPose archive member reference: {member}")

        grasps_member, grasp_member, annotation_member = nested_members
        with _open_nested_zip_from_archive(archive, grasps_member) as grasps_archive:
            with _open_nested_zip_from_archive(grasps_archive, grasp_member) as grasp_archive:
                with grasp_archive.open(annotation_member) as handle:
                    return json.load(handle)


def _annotation_candidates_from_members(
    archive: zipfile.ZipFile,
    *,
    min_frames: int,
    require_both_hands: bool,
) -> List[ContactPoseSequenceMeta]:
    candidates: List[ContactPoseSequenceMeta] = []
    for member in archive.namelist():
        if not _is_annotation_member(member):
            continue
        with archive.open(member) as handle:
            annotation = json.load(handle)
        candidate = _candidate_from_annotation(
            annotation,
            member=member,
            min_frames=min_frames,
            require_both_hands=require_both_hands,
        )
        if candidate is not None:
            candidates.append(candidate)
    return candidates


def _candidate_from_annotation(
    annotation: dict[str, Any],
    *,
    member: str,
    min_frames: int,
    require_both_hands: bool,
) -> ContactPoseSequenceMeta | None:
    valid_hands = tuple(
        idx
        for idx, hand in enumerate(annotation.get("hands", []))
        if hand.get("valid")
    )
    frame_count = len(annotation.get("frames", []))
    if frame_count < min_frames:
        return None
    if require_both_hands and len(valid_hands) < 2:
        return None

    object_name = Path(member).parts[-2] if len(Path(member).parts) >= 2 else "unknown"
    return ContactPoseSequenceMeta(
        archive_member=member,
        frame_count=frame_count,
        valid_hands=valid_hands,
        object_name=object_name,
    )


def _is_annotation_member(member: str) -> bool:
    return member.endswith("annotations.json") and not _is_metadata_member(member)


def _find_grasps_bundle_member(archive: zipfile.ZipFile) -> str | None:
    for member in archive.namelist():
        if member.endswith("grasps.zip") and not _is_metadata_member(member):
            return member
    return None


def _is_grasp_zip_member(member: str) -> bool:
    return member.endswith(".zip") and not _is_metadata_member(member)


def _is_metadata_member(member: str) -> bool:
    name = Path(member).name
    return member.startswith("__MACOSX/") or name == ".DS_Store" or name.startswith("._")


def _join_nested_member(*parts: str) -> str:
    return _NESTED_MEMBER_SEPARATOR.join(parts)


@contextmanager
def _open_nested_zip_from_archive(archive: zipfile.ZipFile, member: str):
    if not member.endswith(".zip"):
        raise ValueError(f"expected zip member, got {member}")

    if member.endswith("grasps.zip"):
        with tempfile.TemporaryDirectory() as temp_dir:
            extracted = Path(archive.extract(member, path=temp_dir))
            with zipfile.ZipFile(extracted) as nested_archive:
                yield nested_archive
        return

    with zipfile.ZipFile(BytesIO(archive.read(member))) as nested_archive:
        yield nested_archive


def _contactpose_object_space_joints(
    hand_joints: Sequence[Vec3],
    hand_meta: dict[str, Any],
    frame: dict[str, Any],
    hand_idx: int,
) -> List[Vec3]:
    if not hand_meta.get("moving"):
        return [tuple(joint) for joint in hand_joints]

    transforms = frame.get("hTo", [])
    if hand_idx >= len(transforms):
        return [tuple(joint) for joint in hand_joints]

    o_th = _invert_pose_matrix(_pose_matrix(transforms[hand_idx]))
    return _transform_points(o_th, hand_joints)


def _extract_form_action(html: str) -> str | None:
    marker = 'form id="download-form" action="'
    start = html.find(marker)
    if start == -1:
        return None
    start += len(marker)
    end = html.find('"', start)
    if end == -1:
        return None
    return html[start:end]


def _extract_hidden_inputs(html: str) -> dict[str, str]:
    inputs: dict[str, str] = {}
    marker = '<input type="hidden" name="'
    cursor = 0
    while True:
        start = html.find(marker, cursor)
        if start == -1:
            break
        start += len(marker)
        name_end = html.find('"', start)
        value_marker = '" value="'
        value_start = html.find(value_marker, name_end)
        if name_end == -1 or value_start == -1:
            break
        value_start += len(value_marker)
        value_end = html.find('"', value_start)
        if value_end == -1:
            break
        inputs[html[start:name_end]] = html[value_start:value_end]
        cursor = value_end + 1
    return inputs


def _mean_vec3(points: Iterable[Vec3]) -> Vec3:
    pts = list(points)
    if not pts:
        return (0.0, 0.0, 0.0)
    return tuple(sum(point[idx] for point in pts) / len(pts) for idx in range(3))


def _midpoint(a: Vec3, b: Vec3) -> Vec3:
    return tuple((a[idx] + b[idx]) / 2.0 for idx in range(3))


def _pose_matrix(pose: dict[str, Any]) -> list[list[float]]:
    q = [float(value) for value in pose["rotation"]]
    x, y, z = [float(value) for value in pose["translation"]]
    w, qx, qy, qz = q

    xx = qx * qx
    yy = qy * qy
    zz = qz * qz
    xy = qx * qy
    xz = qx * qz
    yz = qy * qz
    wx = w * qx
    wy = w * qy
    wz = w * qz

    return [
        [1.0 - 2.0 * (yy + zz), 2.0 * (xy - wz), 2.0 * (xz + wy), x],
        [2.0 * (xy + wz), 1.0 - 2.0 * (xx + zz), 2.0 * (yz - wx), y],
        [2.0 * (xz - wy), 2.0 * (yz + wx), 1.0 - 2.0 * (xx + yy), z],
        [0.0, 0.0, 0.0, 1.0],
    ]


def _invert_pose_matrix(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    rotation = [[matrix[row][col] for col in range(3)] for row in range(3)]
    translation = [matrix[row][3] for row in range(3)]
    rotation_t = [[rotation[col][row] for col in range(3)] for row in range(3)]
    inverted_translation = [
        -sum(rotation_t[row][col] * translation[col] for col in range(3))
        for row in range(3)
    ]
    return [
        [rotation_t[0][0], rotation_t[0][1], rotation_t[0][2], inverted_translation[0]],
        [rotation_t[1][0], rotation_t[1][1], rotation_t[1][2], inverted_translation[1]],
        [rotation_t[2][0], rotation_t[2][1], rotation_t[2][2], inverted_translation[2]],
        [0.0, 0.0, 0.0, 1.0],
    ]


def _transform_points(matrix: Sequence[Sequence[float]], points: Sequence[Vec3]) -> List[Vec3]:
    transformed: List[Vec3] = []
    for point in points:
        px, py, pz = point
        transformed.append(
            (
                matrix[0][0] * px + matrix[0][1] * py + matrix[0][2] * pz + matrix[0][3],
                matrix[1][0] * px + matrix[1][1] * py + matrix[1][2] * pz + matrix[1][3],
                matrix[2][0] * px + matrix[2][1] * py + matrix[2][2] * pz + matrix[2][3],
            )
        )
    return transformed
