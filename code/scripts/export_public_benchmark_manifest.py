#!/usr/bin/env python3
"""Export scaffold-only public benchmark dataset artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import activate_source_root

ROOT = activate_source_root(__file__)

from zpe_xr.io_utils import write_json
from zpe_xr.public_benchmark_catalog import build_dataset_status, build_public_benchmark_manifest, public_hand_dataset_specs


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT.parent / "proofs" / "artifacts" / "public_hand_benchmarks",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    write_json(output_dir / "public_hand_benchmark_manifest.json", build_public_benchmark_manifest())
    for spec in public_hand_dataset_specs():
        write_json(output_dir / f"{spec.dataset_id}_status.json", build_dataset_status(spec))

    print(f"Exported public benchmark scaffold to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
