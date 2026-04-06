#!/usr/bin/env python3
"""Export comparator triage for Phase 09.1."""

from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import activate_source_root

ROOT = activate_source_root(__file__)

from zpe_xr.comparator_triage import build_comparator_triage_report
from zpe_xr.io_utils import write_json


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    output = args.output.resolve()
    write_json(output, build_comparator_triage_report())
    print(f"Exported comparator triage to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
