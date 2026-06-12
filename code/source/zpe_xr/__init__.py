"""zpe_xr wave-1 deterministic codec and evaluation harness."""

from .metadata import VERSION as __version__

from .constants import (
    FPS,
    HANDS,
    JOINTS_PER_HAND,
    RAW_BYTES_PER_FRAME,
    TOTAL_JOINTS,
)
from .codec import DecoderState, EncoderState, XRCodec
from .embodiment_record import (
    CAPTURE_EVIDENCE_CLASSES,
    EMBODIMENT_RECORD_SCHEMA,
    REAL_HEADSET_CAPTURE_SCHEMA,
    EmbodimentRecordValidationError,
    is_native_capture_verified,
    validate_embodiment_record,
    validate_real_headset_capture_manifest,
)
from .headset_surrogate import (
    build_headset_surrogate_manifest,
    classify_surrogate_dataset,
    headset_surrogate_specs,
)
from .api import codec_info, decode, encode, gesture_match
from .models import Frame, FrameSequence

__all__ = [
    "CAPTURE_EVIDENCE_CLASSES",
    "DecoderState",
    "EMBODIMENT_RECORD_SCHEMA",
    "EncoderState",
    "EmbodimentRecordValidationError",
    "FPS",
    "Frame",
    "FrameSequence",
    "HANDS",
    "JOINTS_PER_HAND",
    "REAL_HEADSET_CAPTURE_SCHEMA",
    "RAW_BYTES_PER_FRAME",
    "TOTAL_JOINTS",
    "XRCodec",
    "build_headset_surrogate_manifest",
    "classify_surrogate_dataset",
    "codec_info",
    "decode",
    "encode",
    "gesture_match",
    "headset_surrogate_specs",
    "is_native_capture_verified",
    "validate_embodiment_record",
    "validate_real_headset_capture_manifest",
    "__version__",
]
