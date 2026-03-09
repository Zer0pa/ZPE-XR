#!/usr/bin/env python3
"""Minimal staged-repo sanity check."""

from __future__ import annotations

import json
from pathlib import Path
import sys


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "code" / "src"))

    import zpe_xr  # noqa: PLC0415

    checks = {
        "repo_root": str(repo_root),
        "package_import": True,
        "package_version": getattr(zpe_xr, "__version__", "unknown"),
        "proof_bundle_present": (repo_root / "proofs" / "artifacts" / "2026-02-20_zpe_xr_wave1").exists(),
        "final_status_present": (repo_root / "proofs" / "FINAL_STATUS.md").exists(),
        "audit_limits_present": (repo_root / "PUBLIC_AUDIT_LIMITS.md").exists(),
    }
    print(json.dumps(checks, indent=2, sort_keys=True))
    return 0 if all(value for key, value in checks.items() if key.endswith("_present") or key == "package_import") else 2


if __name__ == "__main__":
    raise SystemExit(main())
