"""Runnable example helpers for contact, stream, and websocket demos."""

from __future__ import annotations

import asyncio
from pathlib import Path
from time import perf_counter_ns
from typing import Any

from .codec import EncoderState, XRCodec
from .constants import FPS
from .contactpose_adapter import (
    ContactPoseSequenceMeta,
    annotation_candidates_from_zip,
    build_zpe_frames_from_annotation,
    download_contactpose_sample_zip,
    read_annotation_from_zip,
)
from .metrics import percentile
from .pipeline import evaluate_gate_b
from .synthetic import generate_sequence

try:
    import websockets
except ImportError:  # pragma: no cover - exercised through runtime error path
    websockets = None


DEFAULT_CONTACTPOSE_SAMPLE = Path("proofs/artifacts/datasets/contactpose/contactpose_sample.zip")


def ensure_contactpose_sample(sample_zip: Path) -> Path:
    if sample_zip.exists():
        return sample_zip
    sample_zip.parent.mkdir(parents=True, exist_ok=True)
    return download_contactpose_sample_zip(sample_zip)


def contactpose_roundtrip_summary(
    sample_zip: Path,
    *,
    archive_member: str | None = None,
    max_frames: int = 90,
) -> dict[str, Any]:
    resolved_sample = sample_zip.resolve()
    candidates = annotation_candidates_from_zip(
        resolved_sample,
        min_frames=max(max_frames, 45),
        require_both_hands=True,
    )
    if not candidates:
        raise RuntimeError(f"no qualifying ContactPose sequences found in {resolved_sample}")

    selected = _select_contactpose_candidate(candidates, archive_member=archive_member)
    annotation = read_annotation_from_zip(resolved_sample, selected.archive_member)
    frames = build_zpe_frames_from_annotation(annotation, max_frames=max_frames)
    gate_b = evaluate_gate_b(frames, _build_codec())

    return {
        "dataset": "ContactPose",
        "sample_zip": str(resolved_sample),
        "archive_member": selected.archive_member,
        "object_name": selected.object_name,
        "frames_used": len(frames),
        "source_frame_count": selected.frame_count,
        "compression_ratio_vs_raw": gate_b.compression_metrics["compression_ratio_vs_raw"],
        "encoded_bytes_total": gate_b.compression_metrics["encoded_bytes_total"],
        "modern_comparator_ratio_vs_zpe": gate_b.compression_metrics["modern_comparator"]["ratio_vs_zpe"],
        "mpjpe_mm": gate_b.fidelity_metrics["mpjpe_mm"],
        "combined_avg_ms": gate_b.latency_metrics["combined_avg_ms"],
        "combined_p95_ms": gate_b.latency_metrics["combined_p95_ms"],
        "quality_pass": gate_b.fidelity_metrics["pass"],
        "latency_pass": gate_b.latency_metrics["pass"],
    }


def streaming_latency_summary(
    *,
    num_frames: int = 900,
    seed: int = 1901,
    gesture: str = "mixed",
) -> dict[str, Any]:
    frames = generate_sequence(num_frames=num_frames, seed=seed, gesture=gesture)
    gate_b = evaluate_gate_b(frames, _build_codec())
    encoded_stats = gate_b.compression_metrics["encoded_stats"]

    return {
        "dataset": "synthetic_openxr_like",
        "fps": FPS,
        "gesture": gesture,
        "frames": len(frames),
        "seconds_of_motion": len(frames) / FPS,
        "compression_ratio_vs_raw": gate_b.compression_metrics["compression_ratio_vs_raw"],
        "latency_ms": dict(gate_b.latency_metrics),
        "packet_bytes": dict(encoded_stats),
        "meets_realtime_budget": bool(gate_b.latency_metrics["pass"]),
    }


def run_websocket_stream_summary(
    *,
    num_frames: int = 180,
    seed: int = 1901,
    gesture: str = "mixed",
) -> dict[str, Any]:
    return asyncio.run(
        websocket_stream_summary(
            num_frames=num_frames,
            seed=seed,
            gesture=gesture,
        )
    )


async def websocket_stream_summary(
    *,
    num_frames: int = 180,
    seed: int = 1901,
    gesture: str = "mixed",
) -> dict[str, Any]:
    if websockets is None:
        raise RuntimeError("websockets is not installed; use ./code[dev] or ./code[test].")

    frames = generate_sequence(num_frames=num_frames, seed=seed, gesture=gesture)
    codec = _build_codec()
    state = EncoderState()
    packets = [codec.encode_frame(frame, state) for frame in frames]
    server_stats = {"messages": 0, "bytes": 0}

    async def handler(websocket: Any) -> None:
        async for message in websocket:
            if not isinstance(message, (bytes, bytearray, memoryview)):
                raise TypeError("websocket demo expects binary packets")
            server_stats["messages"] += 1
            server_stats["bytes"] += len(message)
            await websocket.send(str(server_stats["messages"]))

    async with websockets.serve(handler, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        rtt_ms: list[float] = []
        async with websockets.connect(f"ws://127.0.0.1:{port}") as websocket:
            for packet in packets:
                start_ns = perf_counter_ns()
                await websocket.send(packet)
                await websocket.recv()
                rtt_ms.append((perf_counter_ns() - start_ns) / 1_000_000.0)

    return {
        "dataset": "synthetic_openxr_like",
        "transport": "websocket_loopback",
        "fps": FPS,
        "gesture": gesture,
        "frames_sent": len(packets),
        "packets_received": server_stats["messages"],
        "bytes_sent": server_stats["bytes"],
        "rtt_ms": {
            "count": len(rtt_ms),
            "avg": (sum(rtt_ms) / len(rtt_ms)) if rtt_ms else 0.0,
            "p95": percentile(rtt_ms, 95),
        },
    }


def _build_codec() -> XRCodec:
    return XRCodec(keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0)


def _select_contactpose_candidate(
    candidates: list[ContactPoseSequenceMeta],
    *,
    archive_member: str | None,
) -> ContactPoseSequenceMeta:
    if archive_member is not None:
        for candidate in candidates:
            if candidate.archive_member == archive_member:
                return candidate
        raise ValueError(f"archive member not found in sample: {archive_member}")

    ranked = sorted(
        candidates,
        key=lambda candidate: (-candidate.frame_count, candidate.object_name, candidate.archive_member),
    )
    return ranked[0]
