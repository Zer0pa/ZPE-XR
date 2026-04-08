#!/usr/bin/env python3
"""Exercise a local websocket headset-to-server packet path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "code" / "source"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from zpe_xr.example_support import run_websocket_stream_summary  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=180)
    parser.add_argument("--seed", type=int, default=1901)
    parser.add_argument("--gesture", type=str, default="mixed")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_websocket_stream_summary(
        num_frames=args.frames,
        seed=args.seed,
        gesture=args.gesture,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
