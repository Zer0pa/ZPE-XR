from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from zpe_xr.interhand_benchmark import benchmark_interhand_paths


def _benchmark_fixture(tmp_path: Path) -> Path:
    full_valid = [[1.0] for _ in range(42)]
    world = [[float(idx), float(idx + 10), float(idx + 20)] for idx in range(42)]
    annotations = {
        "0": {
            str(100 + idx): {
                "world_coord": world,
                "joint_valid": full_valid,
                "hand_type": "interacting",
                "seq": "fixture",
            }
            for idx in range(4)
        }
    }
    path = tmp_path / "fixture_joint_3d.json"
    path.write_text(json.dumps(annotations), encoding="utf-8")
    return path


def test_benchmark_interhand_paths_returns_aggregate_report(tmp_path: Path) -> None:
    fixture_path = _benchmark_fixture(tmp_path)
    report = benchmark_interhand_paths(
        {"test": fixture_path},
        min_frames=2,
        max_sequences=1,
    )

    assert report["dataset"] == "InterHand2.6M"
    assert report["aggregate"]["sequence_count"] == 1
    assert report["aggregate"]["frame_count_total"] == 4
    assert report["sequence_results"][0]["split"] == "test"


def test_interhand_benchmark_script_writes_artifacts(tmp_path: Path) -> None:
    fixture_path = _benchmark_fixture(tmp_path)
    repo_root = Path(__file__).resolve().parents[2]
    artifact_dir = tmp_path / "artifacts"
    script = repo_root / "code" / "scripts" / "run_interhand_benchmark.py"

    subprocess.run(
        [
            sys.executable,
            str(script),
            "--test",
            str(fixture_path),
            "--artifact-dir",
            str(artifact_dir),
            "--min-frames",
            "2",
            "--max-sequences",
            "1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads((artifact_dir / "phase3_interhand_benchmark.json").read_text(encoding="utf-8"))
    assert payload["aggregate"]["sequence_count"] == 1
    assert (artifact_dir / "phase3_interhand_benchmark.md").exists()
