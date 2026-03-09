# RunPod Execution Plan

This plan activates only when `runpod_readiness_manifest.json.required` is `true`.

1. Provision GPU node (>=24GB VRAM, >=32GB RAM, >=250GB storage).
2. Sync lane folder and `.env` (tokenized access only, no hardcoded secrets).
3. Install pinned deps from `runpod_requirements_lock.txt`.
4. Execute exact command chain:
   - `set -a; source .env; set +a`
   - `PYTHONHASHSEED=0 python3 scripts/run_gate_m1.py`
   - `PYTHONHASHSEED=0 python3 scripts/run_gate_m3.py`
   - `PYTHONHASHSEED=0 python3 scripts/run_appendix_e.py`
5. Validate outputs against `runpod_expected_artifacts.json` and update claim adjudication.
