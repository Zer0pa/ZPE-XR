import importlib
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import zpe_xr.runtime_paths as runtime_paths
from zpe_xr.runtime_paths import artifact_ref, canonical_root, is_staged_code_root


def test_root_runtime_paths() -> None:
    root = Path("/tmp/zpe-root")
    assert canonical_root(root) == root
    assert is_staged_code_root(root) is False
    assert artifact_ref(root, "file.json").startswith("artifacts/")


def test_staged_runtime_paths() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "ZPE-XR" / "code"
        proofs = root.parent / "proofs"
        proofs.mkdir(parents=True, exist_ok=True)
        assert canonical_root(root) == Path(tmpdir)
        assert is_staged_code_root(root) is True
        assert artifact_ref(root, "file.json").startswith("proofs/artifacts/")


def test_artifact_run_id_prefers_env_override() -> None:
    original = os.environ.get("ZPE_XR_ARTIFACT_RUN_ID")
    try:
        os.environ["ZPE_XR_ARTIFACT_RUN_ID"] = "phase4-test-run"
        importlib.reload(runtime_paths)
        assert runtime_paths.artifact_run_id() == "phase4-test-run"
    finally:
        if original is None:
            os.environ.pop("ZPE_XR_ARTIFACT_RUN_ID", None)
        else:
            os.environ["ZPE_XR_ARTIFACT_RUN_ID"] = original
        importlib.reload(runtime_paths)


def test_artifact_run_id_generates_live_id_when_env_missing() -> None:
    original = os.environ.get("ZPE_XR_ARTIFACT_RUN_ID")
    try:
        os.environ.pop("ZPE_XR_ARTIFACT_RUN_ID", None)
        importlib.reload(runtime_paths)
        run_id = runtime_paths.artifact_run_id()
        assert run_id != "2026-02-20_zpe_xr_wave1"
        assert "_zpe_xr_live_" in run_id
        assert runtime_paths.artifact_run_id() == run_id
    finally:
        if original is None:
            os.environ.pop("ZPE_XR_ARTIFACT_RUN_ID", None)
        else:
            os.environ["ZPE_XR_ARTIFACT_RUN_ID"] = original
        importlib.reload(runtime_paths)
