from __future__ import annotations

import os
from pathlib import Path
import subprocess
import venv


def test_clean_install_from_source_checkout(tmp_path: Path) -> None:
    code_dir = Path(__file__).resolve().parents[1]
    venv_dir = tmp_path / "clean-install"
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(venv_dir)

    python_bin = venv_dir / "bin" / "python"
    if not python_bin.exists():
        python_bin = venv_dir / "Scripts" / "python.exe"

    env = os.environ.copy()
    env["PATH"] = f"{python_bin.parent}:{env.get('PATH', '')}"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    env.pop("PYTHONPATH", None)

    subprocess.run(
        [str(python_bin), "-m", "pip", "install", str(code_dir)],
        check=True,
        cwd=code_dir,
        env=env,
        capture_output=True,
        text=True,
    )

    smoke = subprocess.run(
        [
            str(python_bin),
            "-c",
            (
                "import numpy as np; import zpe_xr; "
                "joints = np.zeros((2, zpe_xr.TOTAL_JOINTS, 3), dtype=np.float32); "
                "payload = zpe_xr.encode(joints, frame_rate=90); "
                "decoded = zpe_xr.decode(payload); "
                "print(decoded.shape)"
            ),
        ],
        check=True,
        cwd=code_dir,
        env=env,
        capture_output=True,
        text=True,
    )

    assert smoke.stdout.strip() == "(2, 52, 3)"
