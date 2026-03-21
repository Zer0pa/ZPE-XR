from __future__ import annotations

from pathlib import Path


def test_src_tree_is_shim_only() -> None:
    src_dir = Path(__file__).resolve().parents[1] / "src" / "zpe_xr"
    py_files = sorted(path.name for path in src_dir.glob("*.py"))
    assert py_files == ["__init__.py"]


def test_canonical_source_root_exists() -> None:
    source_init = Path(__file__).resolve().parents[1] / "source" / "zpe_xr" / "__init__.py"
    assert source_init.exists()
