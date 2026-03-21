"""Minimal Comet ML integration for live execution logging."""

from __future__ import annotations

from datetime import datetime, UTC
import json
import os
from pathlib import Path
import subprocess
from typing import Any, Dict, Iterable, Mapping, Sequence

try:
    from comet_ml import Experiment
except ImportError:  # pragma: no cover - optional dependency
    Experiment = None


DEFAULT_COMET_PROJECT = "zpe-xr"
DEFAULT_COMET_WORKSPACE = "zer0pa"


def comet_available() -> bool:
    return Experiment is not None and bool(os.getenv("COMET_API_KEY"))


def create_experiment(
    *,
    name: str,
    tags: Sequence[str] | None = None,
    parameters: Mapping[str, Any] | None = None,
) -> Any | None:
    if not comet_available():
        return None

    experiment = Experiment(
        api_key=os.getenv("COMET_API_KEY"),
        project_name=os.getenv("COMET_PROJECT_NAME", DEFAULT_COMET_PROJECT),
        workspace=os.getenv("COMET_WORKSPACE", DEFAULT_COMET_WORKSPACE),
        log_code=False,
        log_graph=False,
        auto_param_logging=False,
        auto_metric_logging=False,
        parse_args=False,
        auto_output_logging=None,
        log_env_details=False,
        log_git_metadata=False,
        log_git_patch=False,
        log_env_gpu=False,
        log_env_host=False,
        log_env_cpu=False,
        log_env_network=False,
        log_env_disk=False,
        auto_log_co2=False,
        display_summary_level=0,
    )
    experiment.set_name(name)
    for tag in tags or []:
        experiment.add_tag(tag)
    if parameters:
        experiment.log_parameters(dict(parameters))
    return experiment


def git_head(cwd: Path) -> str | None:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(cwd), text=True, stderr=subprocess.DEVNULL)
            .strip()
            or None
        )
    except Exception:  # noqa: BLE001
        return None


def log_mapping(experiment: Any | None, prefix: str, payload: Mapping[str, Any]) -> None:
    if experiment is None:
        return

    metrics = _numeric_leaf_mapping(payload, prefix)
    others = _string_leaf_mapping(payload, prefix)

    if metrics:
        experiment.log_metrics(metrics)
    if others:
        experiment.log_others(others)


def log_asset_if_exists(experiment: Any | None, path: Path) -> None:
    if experiment is None or not path.exists():
        return
    experiment.log_asset(str(path))


def append_run_manifest(manifest_path: Path, entry: Mapping[str, Any]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {
            "workspace": os.getenv("COMET_WORKSPACE", DEFAULT_COMET_WORKSPACE),
            "project": os.getenv("COMET_PROJECT_NAME", DEFAULT_COMET_PROJECT),
            "runs": [],
        }
    manifest["runs"].append(dict(entry))
    manifest["updated_at_utc"] = datetime.now(UTC).isoformat()
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def experiment_key(experiment: Any | None) -> str | None:
    if experiment is None:
        return None
    try:
        key = experiment.get_key()
    except Exception:  # noqa: BLE001
        return None
    return key or None


def _numeric_leaf_mapping(payload: Mapping[str, Any], prefix: str) -> Dict[str, float]:
    metrics: Dict[str, float] = {}
    for key, value in _flatten_items(payload, prefix):
        if isinstance(value, bool):
            metrics[key] = 1.0 if value else 0.0
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            metrics[key] = float(value)
    return metrics


def _string_leaf_mapping(payload: Mapping[str, Any], prefix: str) -> Dict[str, Any]:
    others: Dict[str, Any] = {}
    for key, value in _flatten_items(payload, prefix):
        if isinstance(value, (dict, list, tuple)):
            continue
        if isinstance(value, (int, float, bool)) or value is None:
            continue
        others[key] = value
    return others


def _flatten_items(payload: Any, prefix: str) -> Iterable[tuple[str, Any]]:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            yield from _flatten_items(value, next_prefix)
        return
    if isinstance(payload, list):
        for idx, value in enumerate(payload):
            next_prefix = f"{prefix}[{idx}]"
            yield from _flatten_items(value, next_prefix)
        return
    yield prefix, payload
