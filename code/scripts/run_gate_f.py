#!/usr/bin/env python3
"""Gate F: commercialization and final closure adjudication for open XR claims."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_xr.io_utils import utc_now_iso, write_json

ARTIFACT_DIR = ROOT.parent / "proofs" / "artifacts" / "2026-02-20_zpe_xr_wave1"


def _load_json(name: str, *, required: bool = True) -> Any:
    path = ARTIFACT_DIR / name
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Missing prerequisite artifact: {path}")
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _claim_pass_from_artifact(data: Dict[str, Any]) -> bool:
    return bool(data.get("pass"))


def _base_claim_statuses() -> Dict[str, str]:
    compression = _load_json("xr_compression_benchmark.json")
    fidelity = _load_json("xr_fidelity_eval.json")
    latency = _load_json("xr_latency_benchmark.json")
    packet_loss = _load_json("xr_packet_loss_resilience.json")
    gesture = _load_json("xr_gesture_eval.json")
    bandwidth = _load_json("xr_bandwidth_eval.json")
    unity = _load_json("xr_unity_roundtrip.json")

    return {
        "XR-C001": "PASS" if _claim_pass_from_artifact(compression) else "FAIL",
        "XR-C002": "PASS" if _claim_pass_from_artifact(fidelity) else "FAIL",
        "XR-C003": "PASS" if _claim_pass_from_artifact(latency) else "FAIL",
        "XR-C004": "PASS" if _claim_pass_from_artifact(packet_loss) else "FAIL",
        "XR-C005": "PASS" if _claim_pass_from_artifact(gesture) else "FAIL",
        "XR-C006": "PASS" if _claim_pass_from_artifact(bandwidth) else "FAIL",
        "XR-C007": "PASS" if _claim_pass_from_artifact(unity) else "FAIL",
    }


def _ensure_impracticality_records(
    impracticality: List[Dict[str, Any]],
    pass_conditions: Dict[str, bool],
) -> List[Dict[str, Any]]:
    updated: List[Dict[str, Any]] = []
    by_resource: Dict[str, Dict[str, Any]] = {}

    for item in impracticality:
        if not isinstance(item, dict):
            continue
        resource = str(item.get("resource", ""))
        impacts = item.get("claim_impact", {})
        impacts_dict = impacts if isinstance(impacts, dict) else {}

        if resource in {"Unity runtime (Meta XR path)", "Meta XR SDK package endpoint", "MANO licensed retarget assets"}:
            impacts_dict["XR-C007"] = "PAUSED_EXTERNAL"
            if resource == "MANO licensed retarget assets":
                impacts_dict.setdefault("XR-C002", "UNCHANGED")

        row = dict(item)
        row["claim_impact"] = impacts_dict
        updated.append(row)
        if resource:
            by_resource[resource] = row

    if not pass_conditions.get("unity_cli_available", True) and "Unity runtime (Meta XR path)" not in by_resource:
        updated.append(
            {
                "resource": "Unity runtime (Meta XR path)",
                "code": "IMP-ACCESS",
                "command_evidence": "proofs/artifacts/2026-02-20_zpe_xr_wave1/resource_attempts_raw.log",
                "error_signature": "UNITY_RUNTIME_OR_DEVICE_UNAVAILABLE",
                "fallback": "Retain interface-level Unity envelope tests; runtime closure paused until Unity runtime/device access is available.",
                "claim_impact": {"XR-C007": "PAUSED_EXTERNAL"},
            }
        )

    if not pass_conditions.get("meta_sdk_accessible", True) and "Meta XR SDK package endpoint" not in by_resource:
        updated.append(
            {
                "resource": "Meta XR SDK package endpoint",
                "code": "IMP-ACCESS",
                "command_evidence": "proofs/artifacts/2026-02-20_zpe_xr_wave1/resource_attempts_raw.log",
                "error_signature": "META_XR_SDK_ENDPOINT_UNAVAILABLE",
                "fallback": "Retain OpenXR-compatible interface harness while runtime SDK path is blocked.",
                "claim_impact": {"XR-C007": "PAUSED_EXTERNAL"},
            }
        )

    if not pass_conditions.get("mano_license_resolved", True) and "MANO licensed retarget assets" not in by_resource:
        updated.append(
            {
                "resource": "MANO licensed retarget assets",
                "code": "IMP-LICENSE",
                "command_evidence": "proofs/artifacts/2026-02-20_zpe_xr_wave1/resource_attempts_raw.log",
                "error_signature": "MANO_COMMERCIAL_LICENSE_UNRESOLVED",
                "fallback": "Use MANO-free paths for non-retarget claims; keep runtime retarget commercialization paused.",
                "claim_impact": {"XR-C002": "UNCHANGED", "XR-C007": "PAUSED_EXTERNAL"},
            }
        )

    return updated


def _write_license_register(claim_statuses: Dict[str, str], pass_conditions: Dict[str, bool]) -> None:
    lines = [
        "# License Risk Register (XR Max Wave)",
        "",
        "| Resource | License/Gate | Risk | Decision | Claim impact | Evidence |",
        "|---|---|---|---|---|---|",
        "| HOT3D toolkit | CC BY-NC 4.0 (+ MANO constraints) | Commercial publication constraints may apply. | Retained for benchmarking; commercialization risk explicitly tracked. | XR-C001/XR-C002/XR-C005 remain metric-valid with commercialization caveat. | proofs/artifacts/2026-02-20_zpe_xr_wave1/max_resource_lock.json |",
        "| HOI-M3 | Public publication endpoint only | Public executable corpus endpoint not confirmed. | IMP-ACCESS logged; synthetic stress path retained. | No automatic claim downgrade from this resource alone. | proofs/artifacts/2026-02-20_zpe_xr_wave1/impracticality_decisions.json |",
        "| HO-Cap | Public publication endpoint only | Public executable corpus endpoint not confirmed. | IMP-ACCESS logged; runtime-retarget evidence not promoted. | XR-C007 remains runtime-blocked. | proofs/artifacts/2026-02-20_zpe_xr_wave1/impracticality_decisions.json |",
        "| MANO | Registration + non-commercial research terms | Commercial retarget usage unresolved. | IMP-LICENSE logged and tied to runtime commercialization pause. | XR-C007 -> PAUSED_EXTERNAL. | proofs/artifacts/2026-02-20_zpe_xr_wave1/impracticality_decisions.json |",
        f"| Unity runtime/Meta SDK | Runtime dependency gate | Unity CLI available={pass_conditions.get('unity_cli_available', False)}, Meta SDK endpoint available={pass_conditions.get('meta_sdk_accessible', False)}. | Hardware/runtime path paused externally. | XR-C007={claim_statuses['XR-C007']}. | proofs/artifacts/2026-02-20_zpe_xr_wave1/gate_m2_result.json |",
        "",
    ]
    (ARTIFACT_DIR / "license_risk_register_xr.md").write_text("\n".join(lines), encoding="utf-8")


def _update_gap_closure(
    claim_statuses: Dict[str, str],
    fg1_pass: bool,
    fg2_pass: bool,
) -> None:
    closure = _load_json("net_new_gap_closure_matrix.json", required=False)
    if not isinstance(closure, dict):
        closure = {"rows": []}
    rows = closure.get("rows", [])
    if not isinstance(rows, list):
        rows = []

    kept_rows: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("gap_id") in {"F-G1", "F-G2"}:
            continue
        kept_rows.append(row)

    kept_rows.extend(
        [
            {
                "gap_id": "F-G1",
                "gap": "XR-C002/XR-C007 closed or moved to PAUSED_EXTERNAL",
                "severity": "HIGH",
                "status": "CLOSED" if fg1_pass else "OPEN",
                "impracticality_code": "IMP-ACCESS" if claim_statuses.get("XR-C007") == "PAUSED_EXTERNAL" else None,
                "quantified_impact": (
                    f"XR-C002={claim_statuses.get('XR-C002')}, XR-C007={claim_statuses.get('XR-C007')}"
                ),
                "evidence": "proofs/artifacts/2026-02-20_zpe_xr_wave1/gate_f_result.json",
            },
            {
                "gap_id": "F-G2",
                "gap": "License-risk register maps each accepted-with-impact item",
                "severity": "HIGH",
                "status": "CLOSED" if fg2_pass else "OPEN",
                "impracticality_code": "IMP-LICENSE" if claim_statuses.get("XR-C007") == "PAUSED_EXTERNAL" else None,
                "quantified_impact": "All non-PASS commercialization decisions are tied to explicit IMP and evidence rows.",
                "evidence": "proofs/artifacts/2026-02-20_zpe_xr_wave1/license_risk_register_xr.md",
            },
        ]
    )

    high_open = [row for row in kept_rows if row.get("severity") == "HIGH" and row.get("status") == "OPEN"]
    closure["rows"] = kept_rows
    closure["generated_at_utc"] = utc_now_iso()
    closure["high_severity_open_count"] = len(high_open)
    closure["pass"] = len(high_open) == 0
    closure["gate"] = "M4+F"
    write_json(ARTIFACT_DIR / "net_new_gap_closure_matrix.json", closure)


def _gate_f_checks(claim_statuses: Dict[str, str], impracticality: List[Dict[str, Any]]) -> Tuple[bool, bool]:
    closed_statuses = {"PASS", "FAIL", "PAUSED_EXTERNAL"}
    fg1_pass = claim_statuses.get("XR-C002") in closed_statuses and claim_statuses.get("XR-C007") in closed_statuses

    claim_to_imp: Dict[str, List[str]] = {}
    for row in impracticality:
        impacts = row.get("claim_impact", {})
        if not isinstance(impacts, dict):
            continue
        resource = str(row.get("resource", "unknown"))
        for claim, status in impacts.items():
            if status in {"PAUSED_EXTERNAL", "FAIL", "INCONCLUSIVE"}:
                claim_to_imp.setdefault(claim, []).append(resource)

    unresolved = [
        claim
        for claim, status in claim_statuses.items()
        if status in {"PAUSED_EXTERNAL", "FAIL"} and claim not in claim_to_imp
    ]
    fg2_pass = len(unresolved) == 0
    return fg1_pass, fg2_pass


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    gate_m2 = _load_json("gate_m2_result.json")
    pass_conditions = gate_m2.get("pass_conditions", {})
    if not isinstance(pass_conditions, dict):
        pass_conditions = {}

    claim_statuses = _base_claim_statuses()

    # Appendix F commercialization rule: runtime/hardware-gated Unity closure pauses externally.
    runtime_blocked = (not pass_conditions.get("unity_cli_available", False)) or (
        not pass_conditions.get("meta_sdk_accessible", False)
    )
    if runtime_blocked:
        claim_statuses["XR-C007"] = "PAUSED_EXTERNAL"

    impracticality = _load_json("impracticality_decisions.json", required=False)
    if not isinstance(impracticality, list):
        impracticality = []
    impracticality = _ensure_impracticality_records(impracticality, pass_conditions)
    write_json(ARTIFACT_DIR / "impracticality_decisions.json", impracticality)

    fg1_pass, fg2_pass = _gate_f_checks(claim_statuses, impracticality)
    _write_license_register(claim_statuses, pass_conditions)
    _update_gap_closure(claim_statuses, fg1_pass, fg2_pass)

    claim_final = {
        "generated_at_utc": utc_now_iso(),
        "claims": {
            claim_id: {
                "status": status,
                "evidence": [
                    f"proofs/artifacts/2026-02-20_zpe_xr_wave1/{name}"
                    for name in [
                        "xr_compression_benchmark.json",
                        "xr_fidelity_eval.json",
                        "xr_latency_benchmark.json",
                        "xr_packet_loss_resilience.json",
                        "xr_gesture_eval.json",
                        "xr_bandwidth_eval.json",
                        "xr_unity_roundtrip.json",
                        "gate_m2_result.json",
                        "impracticality_decisions.json",
                        "license_risk_register_xr.md",
                    ]
                ],
            }
            for claim_id, status in claim_statuses.items()
        },
    }
    write_json(ARTIFACT_DIR / "claim_final_status.json", claim_final)

    gate_f_result = {
        "gate": "F",
        "generated_at_utc": utc_now_iso(),
        "F-G1_close_XR-C002_XR-C007_or_pause_external": fg1_pass,
        "F-G2_license_risk_register_mapped": fg2_pass,
        "overall_pass": bool(fg1_pass and fg2_pass),
        "claim_statuses": claim_statuses,
        "runtime_blocked": runtime_blocked,
        "evidence": [
            "proofs/artifacts/2026-02-20_zpe_xr_wave1/claim_final_status.json",
            "proofs/artifacts/2026-02-20_zpe_xr_wave1/impracticality_decisions.json",
            "proofs/artifacts/2026-02-20_zpe_xr_wave1/license_risk_register_xr.md",
            "proofs/artifacts/2026-02-20_zpe_xr_wave1/net_new_gap_closure_matrix.json",
        ],
    }
    write_json(ARTIFACT_DIR / "gate_f_result.json", gate_f_result)

    print(f"Gate F complete. PASS={gate_f_result['overall_pass']}")
    return 0 if gate_f_result["overall_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
