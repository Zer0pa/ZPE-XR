from __future__ import annotations

from importlib.util import find_spec

if find_spec("zpe_xr") is None:
    raise RuntimeError(
        "zpe_xr must be installed into the active interpreter before running tests. "
        "Use `python -m pip install \"./code[dev]\"` or `maturin develop --release`."
    )
