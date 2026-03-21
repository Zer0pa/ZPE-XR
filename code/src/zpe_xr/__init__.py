"""Compatibility shim for legacy repo-local imports.

The canonical Python runtime now lives under ``code/source/zpe_xr``.
This shim exists only so older repo-local script paths that still insert
``code/src`` keep resolving to the canonical package instead of drifting.
"""

from __future__ import annotations

from pathlib import Path

_SOURCE_PACKAGE = Path(__file__).resolve().parents[2] / "source" / "zpe_xr"
_SOURCE_INIT = _SOURCE_PACKAGE / "__init__.py"

if not _SOURCE_INIT.exists():
    raise ImportError(f"canonical source package missing: {_SOURCE_INIT}")

__path__ = [str(_SOURCE_PACKAGE)]
__file__ = str(_SOURCE_INIT)
exec(compile(_SOURCE_INIT.read_text(encoding="utf-8"), str(_SOURCE_INIT), "exec"), globals(), globals())
