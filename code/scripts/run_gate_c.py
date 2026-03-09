#!/usr/bin/env python3
"""Gate C: network resilience, gesture accuracy, and bandwidth evidence."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_xr.codec import XRCodec
from zpe_xr.gesture import evaluate_corpus
from zpe_xr.io_utils import write_json
from zpe_xr.network import encode_sequence
from zpe_xr.pipeline import evaluate_bandwidth, evaluate_packet_loss_resilience
from zpe_xr.synthetic import generate_gesture_corpus, generate_sequence

ARTIFACT_DIR = ROOT.parent / "proofs" / "artifacts" / "2026-02-20_zpe_xr_wave1"


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    frames = generate_sequence(num_frames=1800, seed=1103, gesture="mixed")
    codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)
    packets = encode_sequence(codec, frames)

    sweep = []
    for loss_rate, jitter_probability, max_delay_frames, seed in [
        (0.05, 0.10, 1, 3301),
        (0.10, 0.20, 1, 4409),
        (0.20, 0.25, 2, 5501),
    ]:
        sweep.append(
            evaluate_packet_loss_resilience(
                frames=frames,
                packets=packets,
                codec=codec,
                loss_rate=loss_rate,
                jitter_probability=jitter_probability,
                max_delay_frames=max_delay_frames,
                seed=seed,
            )
        )

    target_case = next(item for item in sweep if abs(item["loss_rate"] - 0.10) < 1e-9)
    packet_loss_report = {
        "claim_id": "XR-C004",
        "target_case": target_case,
        "sweep": sweep,
        "pass": bool(target_case["pass"]),
    }
    write_json(ARTIFACT_DIR / "xr_packet_loss_resilience.json", packet_loss_report)

    gesture_corpus = generate_gesture_corpus(
        samples_per_gesture=40,
        frames_per_sample=60,
        seed=2207,
    )
    gesture_result = evaluate_corpus(gesture_corpus)
    gesture_report = {
        "claim_id": "XR-C005",
        **gesture_result,
        "pass_threshold_accuracy": 0.95,
        "pass": gesture_result["accuracy"] >= 0.95,
    }
    write_json(ARTIFACT_DIR / "xr_gesture_eval.json", gesture_report)

    bandwidth_report = {
        "claim_id": "XR-C006",
        **evaluate_bandwidth(packets=packets),
    }
    write_json(ARTIFACT_DIR / "xr_bandwidth_eval.json", bandwidth_report)

    all_pass = bool(packet_loss_report["pass"] and gesture_report["pass"] and bandwidth_report["pass"])
    print(f"Gate C complete. PASS={all_pass}")
    return 0 if all_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
