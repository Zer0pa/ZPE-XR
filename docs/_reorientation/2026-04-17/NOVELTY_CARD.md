# ZPE-XR Novelty Card

**Product:** ZPE-XR  
**Domain:** Deterministic transport encoding for two-hand XR joint-position streams.  
**What we sell:** Smaller, replay-safe hand-stream transport with bounded recovery behavior and installable evaluation surfaces.

## Novel contributions

1. **Backup-delta packet envelope for two-hand joint streams** — ZPE-XR uses a packet layout that carries the current delta payload plus the prior primary delta payload, keyed by sequence number, inside a bounded parser with checksum validation. That lets the decoder recover the immediately previous frame when the prior packet is missing instead of relying only on concealment. Code: `code/source/zpe_xr/codec.py:24-27`, `code/source/zpe_xr/codec.py:82-127`, `code/source/zpe_xr/codec.py:129-192`. Nearest prior art: generic delta-compressed state replication and keyframe/delta video or game transport. What is genuinely new here: the specific dual-hand XR packet contract that pairs primary and backup delta entries in one compact transport envelope for this codec.
2. **Deterministic concealment and backup-first recovery logic** — The network path applies explicit backup recovery when the previous packet was missed, then falls back to bounded concealment based on prior decoded states. Code: `code/source/zpe_xr/network.py:73-158`. Nearest prior art: packet-loss concealment and snapshot interpolation in real-time networking. What is genuinely new here: the particular recovery ordering and state handling used for this XR codec's packet semantics and proof harness.
3. **Position-only XR transport surface with install-time Rust/Python parity** — The public API preserves the same transport contract whether the Rust kernel is present or whether the Python fallback is used, and it exposes the codec honestly as a position-only transport rather than a full pose platform. Code: `code/source/zpe_xr/api.py:32-80`, `code/source/zpe_xr/api.py:116-127`, `code/source/zpe_xr/metadata.py:4-8`. Nearest prior art: PyO3-backed Python packages and fallback APIs. What is genuinely new here: the XR-specific transport contract and evidence wiring, not the PyO3 mechanism itself.

## Standard techniques used (explicit, not novel)

- `zlib.crc32` checksum validation
- `struct.Struct` packet packing and parsing
- int16 quantization of positions
- int8 delta entries with keyframe resets on overflow
- Python/Rust packaging through PyO3 and maturin
- gesture classification and packet replay harnessing as ordinary evaluation machinery

## Compass-8 / 8-primitive architecture

NO — ZPE-XR does not use Compass-8 or any directional primitive basis. The repo declares `PRIMITIVE_COUNT = 0` and the encoding basis as `int16-quant-int8-delta-crc32`. Evidence: `code/source/zpe_xr/metadata.py:5-7`.

## Open novelty questions for the license agent

- Should the backup-delta packet contract and the backup-first recovery policy be licensed as one combined novelty item or as separate product contributions?
- Should `gesture_match` remain outside the novelty schedule because it is an evaluation convenience around the transport surface rather than the transport mechanism itself?
