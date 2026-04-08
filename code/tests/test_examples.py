from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import zipfile


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run_example(name: str, *args: str) -> dict[str, object]:
    script = _repo_root() / "examples" / name
    result = subprocess.run(
        [sys.executable, str(script), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def _write_contactpose_fixture(path: Path) -> Path:
    annotation = {
        "object": "wine_glass",
        "hands": [
            {"valid": True, "moving": False, "joints": [[0.0, 0.0, 0.0] for _ in range(21)]},
            {"valid": True, "moving": False, "joints": [[1.0, 1.0, 1.0] for _ in range(21)]},
        ],
        "frames": [{"hTo": [{}, {}]} for _ in range(50)],
    }

    object_zip_bytes = BytesIO()
    with zipfile.ZipFile(object_zip_bytes, "w") as object_zip:
        object_zip.writestr("wine_glass/annotations.json", json.dumps(annotation))

    grasps_zip_bytes = BytesIO()
    with zipfile.ZipFile(grasps_zip_bytes, "w") as grasps_zip:
        grasps_zip.writestr("grasps/full28_use/wine_glass.zip", object_zip_bytes.getvalue())

    with zipfile.ZipFile(path, "w") as outer:
        outer.writestr("ContactPose sample data/grasps.zip", grasps_zip_bytes.getvalue())

    return path


def test_contactpose_roundtrip_example_runs_from_fixture(tmp_path: Path) -> None:
    sample_zip = _write_contactpose_fixture(tmp_path / "contactpose_sample.zip")
    summary = _run_example(
        "contactpose_roundtrip.py",
        "--sample-zip",
        str(sample_zip),
        "--max-frames",
        "45",
    )

    assert summary["dataset"] == "ContactPose"
    assert summary["object_name"] == "wine_glass"
    assert summary["frames_used"] == 45
    assert summary["latency_pass"] is True
    assert summary["quality_pass"] is True


def test_streaming_demo_example_runs() -> None:
    summary = _run_example("streaming_demo.py", "--frames", "180")

    assert summary["dataset"] == "synthetic_openxr_like"
    assert summary["frames"] == 180
    assert summary["fps"] == 90
    assert summary["meets_realtime_budget"] is True


def test_websocket_bridge_example_runs() -> None:
    summary = _run_example("websocket_bridge.py", "--frames", "24")

    assert summary["transport"] == "websocket_loopback"
    assert summary["frames_sent"] == 24
    assert summary["packets_received"] == 24
    assert summary["rtt_ms"]["count"] == 24
