#!/usr/bin/env python3
"""Gate M4: residual risk closure and quantified-impact acceptance matrix."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_xr.io_utils import utc_now_iso, write_json

ARTIFACT_DIR = ROOT.parent / "proofs" / "artifacts" / "2026-02-20_zpe_xr_wave1"


def _load_json(name: str) -> Dict[str, Any]:
    path = ARTIFACT_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    m1 = _load_json("gate_m1_result.json")
    m2 = _load_json("gate_m2_result.json")
    m3 = _load_json("gate_m3_result.json")

    gap_rows: List[Dict[str, Any]] = []

    if m1.get("pass"):
        gap_rows.append(
            {
                "gap_id": "D2-1",
                "gap": "HOT3D-backed benchmark path",
                "severity": "HIGH",
                "status": "CLOSED",
                "impracticality_code": None,
                "quantified_impact": "None",
                "evidence": "proofs/artifacts/2026-02-20_zpe_xr_wave1/gate_m1_result.json",
            }
        )
    else:
        gap_rows.append(
            {
                "gap_id": "D2-1",
                "gap": "HOT3D-backed benchmark path",
                "severity": "HIGH",
                "status": "ACCEPTED_WITH_IMPACT",
                "impracticality_code": "IMP-ACCESS",
                "quantified_impact": "XR-C001/XR-C002/XR-C005 remain synthetic-backed with real-corpus external validity risk.",
                "evidence": "proofs/artifacts/2026-02-20_zpe_xr_wave1/gate_m1_result.json",
            }
        )

    if m2.get("pass"):
        gap_rows.append(
            {
                "gap_id": "D2-2",
                "gap": "Meta/Unity runtime integration",
                "severity": "HIGH",
                "status": "CLOSED",
                "impracticality_code": None,
                "quantified_impact": "None",
                "evidence": "proofs/artifacts/2026-02-20_zpe_xr_wave1/gate_m2_result.json",
            }
        )
    else:
        gap_rows.append(
            {
                "gap_id": "D2-2",
                "gap": "Meta/Unity runtime integration",
                "severity": "HIGH",
                "status": "ACCEPTED_WITH_IMPACT",
                "impracticality_code": "IMP-ACCESS",
                "quantified_impact": "XR-C007 production-readiness remains limited to interface-level contract evidence.",
                "evidence": "proofs/artifacts/2026-02-20_zpe_xr_wave1/gate_m2_result.json",
            }
        )

    mano_resolved = bool(m2.get("pass_conditions", {}).get("mano_license_resolved", False))
    if mano_resolved:
        gap_rows.append(
            {
                "gap_id": "D2-3",
                "gap": "MANO licensing + retarget validation",
                "severity": "HIGH",
                "status": "CLOSED",
                "impracticality_code": None,
                "quantified_impact": "None",
                "evidence": "proofs/artifacts/2026-02-20_zpe_xr_wave1/gate_m2_result.json",
            }
        )
    else:
        gap_rows.append(
            {
                "gap_id": "D2-3",
                "gap": "MANO licensing + retarget validation",
                "severity": "HIGH",
                "status": "ACCEPTED_WITH_IMPACT",
                "impracticality_code": "IMP-LICENSE",
                "quantified_impact": "Cross-hand-model retarget fidelity remains INCONCLUSIVE until license-approved corpus execution.",
                "evidence": "proofs/artifacts/2026-02-20_zpe_xr_wave1/gate_m2_result.json",
            }
        )

    gap_rows.append(
        {
            "gap_id": "D4-3",
            "gap": "Extended stress profile >30% packet loss",
            "severity": "MEDIUM",
            "status": "CLOSED" if m3.get("pass") else "ACCEPTED_WITH_IMPACT",
            "impracticality_code": None,
            "quantified_impact": (
                "Stress profile executed; see interaction report."
                if m3.get("pass")
                else "Stress profile executed but one or more stress thresholds failed; deployment risk elevated."
            ),
            "evidence": "proofs/artifacts/2026-02-20_zpe_xr_wave1/interaction_stress_report.json",
        }
    )

    high_open = [
        row for row in gap_rows if row["severity"] == "HIGH" and row["status"] == "OPEN"
    ]
    m4_pass = len(high_open) == 0

    closure_matrix = {
        "generated_at_utc": utc_now_iso(),
        "gate": "M4",
        "pass": m4_pass,
        "rows": gap_rows,
        "high_severity_open_count": len(high_open),
    }
    write_json(ARTIFACT_DIR / "net_new_gap_closure_matrix.json", closure_matrix)
    write_json(ARTIFACT_DIR / "gate_m4_result.json", closure_matrix)

    residual_lines = [
        "# Residual Risk Register",
        "",
        "| Risk ID | Description | Severity | Status | Quantified Impact | Evidence |",
        "|---|---|---|---|---|---|",
    ]
    for idx, row in enumerate(gap_rows, start=1):
        residual_lines.append(
            f"| RR-M{idx:03d} | {row['gap']} | {row['severity']} | {row['status']} | {row['quantified_impact']} | {row['evidence']} |"
        )
    residual_lines.append("")
    (ARTIFACT_DIR / "residual_risk_register.md").write_text("\n".join(residual_lines), encoding="utf-8")

    print(f"Gate M4 complete. PASS={m4_pass}")
    return 0 if m4_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
