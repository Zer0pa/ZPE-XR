"""Package metadata and frozen evidence constants for the public API."""

VERSION = "0.3.0"
KERNEL = "python-fallback-or-rust-pyo3"
ENCODING_BASIS = "int16-quant-int8-delta-crc32"
PRIMITIVE_COUNT = 0  # no directional primitives — codec uses int16 quantization + int8 delta compression
COMPRESSION_RATIO_CLAIM = "~24x vs position-only baseline on ContactPose (real data)"
PHASE4_COLD_START_COMET_KEY = None
PHASE5_MULTI_SEQUENCE_COMET_KEY = "0e957cb027364d36880f6962fd70b78f"
