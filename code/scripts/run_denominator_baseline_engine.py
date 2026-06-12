#!/usr/bin/env python3
"""Run the Phase 4 denominator-clean benchmark engine."""

from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import activate_source_root

ROOT = activate_source_root(__file__)

from zpe_xr.denominator_baseline import (  # noqa: E402
    build_denominator_report,
    render_denominator_report_markdown,
    validate_denominator_report,
)
from zpe_xr.io_utils import write_json  # noqa: E402


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "proofs" / "artifacts" / "phase4_denominator_baseline",
        help="Directory for denominator_clean_benchmark.json and .md",
    )
    parser.add_argument(
        "--frames-per-segment",
        type=int,
        default=12,
        help="Synthetic frames per required motion segment.",
    )
    parser.add_argument("--seed", type=int, default=4104, help="Deterministic fixture seed.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    report = build_denominator_report(frames_per_segment=args.frames_per_segment, seed=args.seed)
    validate_denominator_report(report)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "denominator_clean_benchmark.json"
    md_path = output_dir / "denominator_clean_benchmark.md"
    write_json(json_path, report)
    md_path.write_text(render_denominator_report_markdown(report), encoding="utf-8")

    print(f"Phase 4 denominator baseline complete: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
