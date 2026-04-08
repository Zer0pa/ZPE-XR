#!/usr/bin/env python3
"""Download or reuse a ContactPose sample, then compress and verify it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "code" / "source"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from zpe_xr.example_support import (  # noqa: E402
    DEFAULT_CONTACTPOSE_SAMPLE,
    contactpose_roundtrip_summary,
    ensure_contactpose_sample,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sample-zip",
        type=Path,
        default=ROOT / DEFAULT_CONTACTPOSE_SAMPLE,
        help="Path to a ContactPose sample zip. Downloads the public sample if missing.",
    )
    parser.add_argument("--archive-member", type=str, default=None)
    parser.add_argument("--max-frames", type=int, default=90)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sample_zip = ensure_contactpose_sample(args.sample_zip)
    summary = contactpose_roundtrip_summary(
        sample_zip,
        archive_member=args.archive_member,
        max_frames=args.max_frames,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
