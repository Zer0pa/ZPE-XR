#!/usr/bin/env python3
"""Gate A: lock resource provenance and deterministic fixture metadata."""

from __future__ import annotations

from datetime import datetime, UTC
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_xr.io_utils import write_json
from zpe_xr.synthetic import generate_sequence


def _sequence_digest(seed: int, frames: int) -> str:
    seq = generate_sequence(num_frames=frames, seed=seed, gesture="mixed")
    hasher = sha256()
    for frame in seq:
        for x, y, z in frame.positions:
            hasher.update(f"{x:.6f},{y:.6f},{z:.6f}".encode("utf-8"))
    return hasher.hexdigest()


def main() -> int:
    fixtures_dir = ROOT / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    concept_anchor = ROOT.parent / "README.md"

    resource_lock = {
        "lock_generated_at_utc": datetime.now(UTC).isoformat(),
        "lane_root": "code",
        "concept_anchor": {
            "path": "README.md",
            "exists": concept_anchor.exists(),
        },
        "resources": [
            {
                "resource_id": "openxr_sdk",
                "source_reference": "https://github.com/KhronosGroup/OpenXR-SDK",
                "access_mode": "reference-only",
                "local_probe": None,
                "available_locally": False,
                "fallback": "openxr_interface_contract_fixture_v1",
            },
            {
                "resource_id": "meta_xr_sdk",
                "source_reference": "Meta XR SDK v72+ (Unity package)",
                "access_mode": "license-gated external",
                "local_probe": None,
                "available_locally": False,
                "fallback": "unity_envelope_contract_harness_v1",
            },
            {
                "resource_id": "hot3d",
                "source_reference": "https://facebookresearch.github.io/hot3d/",
                "access_mode": "dataset external",
                "local_probe": "code/fixtures/hot3d",
                "available_locally": (ROOT / "fixtures" / "hot3d").exists(),
                "fallback": "synthetic_hot3d_snapshot_v1",
            },
            {
                "resource_id": "xr_interaction_toolkit",
                "source_reference": "Unity package com.unity.xr.interaction.toolkit",
                "access_mode": "external package",
                "local_probe": None,
                "available_locally": False,
                "fallback": "xr_input_contract_fixture_v1",
            },
            {
                "resource_id": "unity_netcode_and_fishnet",
                "source_reference": "Unity Netcode 1.8 + FishNet MIT",
                "access_mode": "external package",
                "local_probe": None,
                "available_locally": False,
                "fallback": "transport_serializer_compat_matrix_v1",
            },
            {
                "resource_id": "mano",
                "source_reference": "https://mano.is.tue.mpg.de",
                "access_mode": "registration/licensed",
                "local_probe": "code/fixtures/mano",
                "available_locally": (ROOT / "fixtures" / "mano").exists(),
                "fallback": "kinematic_hand_shape_proxy_v1",
            },
            {
                "resource_id": "avatarposer",
                "source_reference": "https://arxiv.org/abs/2207.13784",
                "access_mode": "paper reference",
                "local_probe": None,
                "available_locally": False,
                "fallback": "sparse-body-extension_decision_record_v1",
            },
        ],
        "determinism": {
            "pythonhashseed": "0",
            "global_seeds": [1103, 2207, 3301, 4409, 5501],
            "quantization_mm": 1.0,
        },
        "comparators": {
            "incumbent": "raw_openxr_float_stream",
            "modern": "float16_delta_plus_zlib",
        },
    }

    snapshot = {
        "snapshot_id": "synthetic_hot3d_snapshot_v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "generator": "zpe_xr.synthetic.generate_sequence",
        "frame_count": 900,
        "profile": "mixed",
        "seed_hashes": {
            "1103": _sequence_digest(1103, 900),
            "2207": _sequence_digest(2207, 900),
            "3301": _sequence_digest(3301, 900),
        },
        "position_units": "meters",
        "joint_layout": "26 joints/hand x 2 hands",
        "comparability_note": (
            "Synthetic fixture preserves OpenXR-like dimensionality and frame rate but is not "
            "a substitute for HOT3D real capture domain shift."
        ),
    }

    write_json(fixtures_dir / "resource_lock.json", resource_lock)
    write_json(fixtures_dir / "synthetic_hot3d_snapshot_v1.json", snapshot)

    print("Generated fixtures/resource_lock.json and fixtures/synthetic_hot3d_snapshot_v1.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
