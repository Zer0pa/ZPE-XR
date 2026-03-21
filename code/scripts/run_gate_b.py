#!/usr/bin/env python3
"""Gate B: core codec and baseline compression/fidelity/latency evidence."""

from __future__ import annotations

from pathlib import Path
import sys

from _bootstrap import activate_source_root

ROOT = activate_source_root(__file__)

from zpe_xr.codec import XRCodec
from zpe_xr.io_utils import write_json
from zpe_xr.metrics import packet_hash_digest
from zpe_xr.pipeline import evaluate_gate_b
from zpe_xr.runtime_paths import resolve_artifact_dir
from zpe_xr.synthetic import generate_sequence

ARTIFACT_DIR = resolve_artifact_dir(ROOT)


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    frames = generate_sequence(num_frames=1800, seed=1103, gesture="mixed")
    codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)

    result = evaluate_gate_b(frames, codec)

    compression = dict(result.compression_metrics)
    compression["claim_id"] = "XR-C001"
    compression["pass_threshold_ratio"] = 10.0
    compression["pass"] = compression["compression_ratio_vs_raw"] >= 10.0

    fidelity = dict(result.fidelity_metrics)
    fidelity["claim_id"] = "XR-C002"

    latency = dict(result.latency_metrics)
    latency["claim_id"] = "XR-C003"

    write_json(ARTIFACT_DIR / "xr_compression_benchmark.json", compression)
    write_json(ARTIFACT_DIR / "xr_fidelity_eval.json", fidelity)
    write_json(ARTIFACT_DIR / "xr_latency_benchmark.json", latency)

    write_json(
        ARTIFACT_DIR / "gate_b_repro_metadata.json",
        {
            "sequence_seed": 1103,
            "num_frames": 1800,
            "codec": {
                "keyframe_interval": 45,
                "deadband_mm": 1,
                "quant_step_mm": 1.0,
            },
            "packet_digest_sha256": packet_hash_digest(result.packets),
        },
    )

    all_pass = bool(compression["pass"] and fidelity["pass"] and latency["pass"])
    print(f"Gate B complete. PASS={all_pass}")
    return 0 if all_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
