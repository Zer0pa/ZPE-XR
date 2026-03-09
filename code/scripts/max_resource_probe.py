#!/usr/bin/env python3
"""Utilities for Appendix D/E resource probing and evidence capture."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC
import json
from pathlib import Path
import shlex
import subprocess
from typing import Any, Dict, List, Optional


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class CommandResult:
    command: str
    cwd: str
    returncode: int
    stdout: str
    stderr: str
    started_at_utc: str
    ended_at_utc: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "cwd": self.cwd,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "started_at_utc": self.started_at_utc,
            "ended_at_utc": self.ended_at_utc,
        }


def run_cmd(command: str, *, cwd: Path, timeout_s: int = 240) -> CommandResult:
    started = utc_now_iso()
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        shell=True,
        text=True,
        capture_output=True,
        timeout=timeout_s,
    )
    ended = utc_now_iso()
    return CommandResult(
        command=command,
        cwd=str(cwd),
        returncode=proc.returncode,
        stdout=proc.stdout[-20000:],
        stderr=proc.stderr[-20000:],
        started_at_utc=started,
        ended_at_utc=ended,
    )


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_log(path: Path, header: str, result: CommandResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {header}\n")
        handle.write(f"- command: `{result.command}`\n")
        handle.write(f"- returncode: `{result.returncode}`\n")
        if result.stdout.strip():
            handle.write("- stdout:\n")
            handle.write("```\n")
            handle.write(result.stdout.strip()[:4000])
            handle.write("\n```\n")
        if result.stderr.strip():
            handle.write("- stderr:\n")
            handle.write("```\n")
            handle.write(result.stderr.strip()[:4000])
            handle.write("\n```\n")


def classify_impracticality(*, reason: str) -> Optional[str]:
    text = reason.lower()
    if "license" in text or "terms" in text or "commercial" in text:
        return "IMP-LICENSE"
    if "timed out" in text or "compute" in text or "gpu" in text:
        return "IMP-COMPUTE"
    if "space" in text or "storage" in text or "disk" in text:
        return "IMP-STORAGE"
    if "not found" in text or "access" in text or "403" in text or "404" in text or "auth" in text:
        return "IMP-ACCESS"
    if "no public code" in text or "no code" in text:
        return "IMP-NOCODE"
    return None
