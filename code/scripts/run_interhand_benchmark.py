#!/usr/bin/env python3
"""Run the Phase 3 InterHand2.6M benchmark on local annotation files."""

from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import activate_source_root

ROOT = activate_source_root(__file__)

from zpe_xr.interhand_benchmark import benchmark_interhand_paths, render_interhand_benchmark_markdown
from zpe_xr.io_utils import write_json
from zpe_xr.runtime_paths import resolve_artifact_dir


def parse_args() -> argparse.Namespace:
    repo_root = ROOT.parent
    default_dataset_root = repo_root / "datasets" / "interhand30fps"
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, default=default_dataset_root / "train_joint_3d.json")
    parser.add_argument("--val", type=Path, default=default_dataset_root / "val_joint_3d.json")
    parser.add_argument("--test", type=Path, default=default_dataset_root / "test_joint_3d.json")
    parser.add_argument("--artifact-dir", type=Path, default=None)
    parser.add_argument("--min-frames", type=int, default=90)
    parser.add_argument("--max-sequences", type=int, default=3)
    parser.add_argument("--max-frames-per-sequence", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    artifact_dir = args.artifact_dir or resolve_artifact_dir(ROOT)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    report = benchmark_interhand_paths(
        {
            "train": args.train,
            "val": args.val,
            "test": args.test,
        },
        min_frames=args.min_frames,
        max_sequences=args.max_sequences,
        max_frames_per_sequence=args.max_frames_per_sequence,
    )

    write_json(artifact_dir / "phase3_interhand_benchmark.json", report)
    (artifact_dir / "phase3_interhand_benchmark.md").write_text(
        render_interhand_benchmark_markdown(report),
        encoding="utf-8",
    )
    print(f"Phase 3 InterHand benchmark complete. sequences={report['aggregate']['sequence_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
