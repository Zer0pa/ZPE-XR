from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT / "source", ROOT / "src"):
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
