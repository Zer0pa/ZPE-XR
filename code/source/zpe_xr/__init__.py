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
from .api import codec_info, decode, encode, gesture_match
from .models import Frame, FrameSequence

__all__ = [
    "DecoderState",
    "EncoderState",
    "FPS",
    "Frame",
    "FrameSequence",
    "HANDS",
    "JOINTS_PER_HAND",
    "RAW_BYTES_PER_FRAME",
    "TOTAL_JOINTS",
    "XRCodec",
    "codec_info",
    "decode",
    "encode",
    "gesture_match",
    "__version__",
]
