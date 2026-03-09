"""zpe_xr wave-1 deterministic codec and evaluation harness."""

__version__ = "0.0.0"

from .constants import (
    FPS,
    HANDS,
    JOINTS_PER_HAND,
    RAW_BYTES_PER_FRAME,
    TOTAL_JOINTS,
)
from .codec import DecoderState, EncoderState, XRCodec
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
    "__version__",
]
