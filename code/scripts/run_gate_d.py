#!/usr/bin/env python3
"""Gate D: malformed/adversarial campaigns and deterministic replay checks."""

from __future__ import annotations

import copy
from dataclasses import replace
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_xr.codec import EncoderState, PacketDecodeError, XRCodec
from zpe_xr.gesture import evaluate_corpus
from zpe_xr.io_utils import write_json
from zpe_xr.metrics import packet_hash_digest
from zpe_xr.network import encode_sequence
from zpe_xr.pipeline import evaluate_bandwidth, evaluate_packet_loss_resilience
from zpe_xr.synthetic import CANONICAL_GESTURES, generate_gesture_corpus, generate_sequence

ARTIFACT_DIR = ROOT.parent / "proofs" / "artifacts" / "2026-02-20_zpe_xr_wave1"


def _build_malformed_packets(valid_packet: bytes) -> list[bytes]:
    malformed = []
    malformed.append(b"")
    malformed.append(valid_packet[:5])
    malformed.append(b"BAD" + valid_packet[3:])

    # Invalid checksum.
    if len(valid_packet) > 6:
        bad_checksum = bytearray(valid_packet)
        bad_checksum[-1] ^= 0xFF
        malformed.append(bytes(bad_checksum))

    # Body length mismatch by tampering header count bytes.
    if len(valid_packet) >= 15:
        tampered = bytearray(valid_packet)
        tampered[13] = 120  # current_count
        tampered[14] = 120  # backup_count
        malformed.append(bytes(tampered))

    # Truncated payload.
    malformed.append(valid_packet[:-3])
    return malformed


def _run_malformed_campaign(codec: XRCodec) -> dict:
    frames = generate_sequence(num_frames=120, seed=3301, gesture="mixed")
    packets = encode_sequence(codec, frames)
    valid_packet = packets[20]

    malformed_packets = _build_malformed_packets(valid_packet)

    handled = 0
    uncaught = 0
    signatures: list[str] = []

    for packet in malformed_packets:
        try:
            codec.parse_packet(packet)
            signatures.append("unexpected-accept")
        except PacketDecodeError as exc:
            handled += 1
            signatures.append(str(exc))
        except Exception as exc:  # noqa: BLE001
            uncaught += 1
            signatures.append(f"UNCAUGHT:{type(exc).__name__}:{exc}")

    return {
        "campaign": "DT-XR-1",
        "malformed_inputs": len(malformed_packets),
        "handled_failures": handled,
        "uncaught_crashes": uncaught,
        "pass": uncaught == 0,
        "failure_signatures": signatures,
    }


def _run_adversarial_gesture_campaign() -> dict:
    base_corpus = generate_gesture_corpus(
        samples_per_gesture=20,
        frames_per_sample=50,
        seed=4409,
    )

    adversarial_corpus = []
    for expected, frames in base_corpus:
        mutated = []
        for frame in frames:
            positions = []
            for idx, (x, y, z) in enumerate(frame.positions):
                # Apply deterministic confuser perturbation concentrated near fingertips.
                if idx in (31, 36, 41, 46, 51):
                    x += 0.0015
                    z -= 0.0012
                positions.append((x, y, z))
            mutated.append(replace(frame, positions=tuple(positions)))
        adversarial_corpus.append((expected, tuple(mutated)))

    result = evaluate_corpus(adversarial_corpus)
    return {
        "campaign": "DT-XR-3",
        "total_samples": result["total_samples"],
        "accuracy": result["accuracy"],
        "pass_threshold_accuracy": 0.90,
        "pass": result["accuracy"] >= 0.90,
        "confusion_matrix": result["confusion_matrix"],
    }


def _run_determinism_campaign(codec: XRCodec) -> dict:
    seeds = [1103, 2207, 3301, 4409, 5501]
    runs = []
    consistent = 0

    for seed in seeds:
        frames = generate_sequence(num_frames=700, seed=seed, gesture="mixed")

        first_state = EncoderState()
        second_state = EncoderState()
        first_packets = [codec.encode_frame(frame, first_state) for frame in frames]
        second_packets = [codec.encode_frame(frame, second_state) for frame in frames]

        first_hash = packet_hash_digest(first_packets)
        second_hash = packet_hash_digest(second_packets)
        match = first_hash == second_hash
        if match:
            consistent += 1

        runs.append(
            {
                "seed": seed,
                "packet_count": len(first_packets),
                "first_hash": first_hash,
                "second_hash": second_hash,
                "hash_match": match,
            }
        )

    return {
        "campaign": "DT-XR-4",
        "required_consistent_runs": 5,
        "consistent_runs": consistent,
        "pass": consistent == 5,
        "runs": runs,
    }


def _run_loss_jitter_falsification(codec: XRCodec) -> dict:
    frames = generate_sequence(num_frames=1500, seed=5501, gesture="mixed")
    packets = encode_sequence(codec, frames)

    target = evaluate_packet_loss_resilience(
        frames=frames,
        packets=packets,
        codec=codec,
        loss_rate=0.10,
        jitter_probability=0.20,
        max_delay_frames=1,
        seed=1103,
    )
    stress = evaluate_packet_loss_resilience(
        frames=frames,
        packets=packets,
        codec=codec,
        loss_rate=0.30,
        jitter_probability=0.30,
        max_delay_frames=2,
        seed=2207,
    )

    return {
        "campaign": "DT-XR-2",
        "target_case": target,
        "stress_case": stress,
        "pass": bool(target["pass"]),
    }


def _run_bandwidth_stress(codec: XRCodec) -> dict:
    frames = generate_sequence(num_frames=1800, seed=3301, gesture="mixed")
    packets = encode_sequence(codec, frames)

    four_player = evaluate_bandwidth(packets=packets, remote_players=3)
    eight_player = evaluate_bandwidth(packets=packets, remote_players=7)

    return {
        "campaign": "DT-XR-5",
        "four_player": four_player,
        "eight_player": eight_player,
        "pass": bool(four_player["pass"]),
    }


def _render_falsification_markdown(results: list[dict]) -> str:
    lines = ["# Falsification Results (Gate D)", ""]
    for result in results:
        lines.append(f"## {result['campaign']}")
        lines.append(f"- Pass: `{result.get('pass')}`")
        for key, value in result.items():
            if key in {"campaign", "pass"}:
                continue
            lines.append(f"- {key}: `{value}`")
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    codec = XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)

    dt1 = _run_malformed_campaign(codec)
    dt2 = _run_loss_jitter_falsification(codec)
    dt3 = _run_adversarial_gesture_campaign()
    dt4 = _run_determinism_campaign(codec)
    dt5 = _run_bandwidth_stress(codec)

    all_results = [dt1, dt2, dt3, dt4, dt5]

    write_json(ARTIFACT_DIR / "determinism_replay_results.json", dt4)
    (ARTIFACT_DIR / "falsification_results.md").write_text(
        _render_falsification_markdown(all_results),
        encoding="utf-8",
    )

    uncaught_crash_rate = 0.0 if dt1["malformed_inputs"] == 0 else dt1["uncaught_crashes"] / dt1["malformed_inputs"]
    overall_pass = bool(
        dt1["pass"]
        and dt2["pass"]
        and dt3["pass"]
        and dt4["pass"]
        and dt5["pass"]
        and uncaught_crash_rate == 0.0
    )

    write_json(
        ARTIFACT_DIR / "gate_d_summary.json",
        {
            "campaigns": all_results,
            "uncaught_crash_rate": uncaught_crash_rate,
            "overall_pass": overall_pass,
        },
    )

    print(f"Gate D complete. PASS={overall_pass}")
    return 0 if overall_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
