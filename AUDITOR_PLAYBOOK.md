# Auditor Playbook

This is the shortest honest audit path for the current private staging repo.

It verifies that the staged repo is coherent. It does not establish public
release readiness.

## Shortest Staged Audit Path

1. Clone or use the staged repo.
2. Create an environment and install the package:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e "./code[dev]"
```

3. Run the repo-local sanity probe:

```bash
python ./executable/verify.py
```

4. Optional test replay:

```bash
python -m pytest ./code/tests -q
```

## What To Inspect

- `proofs/FINAL_STATUS.md`
- `proofs/RELEASE_READINESS_REPORT.md`
- `proofs/artifacts/2026-02-20_zpe_xr_wave1/claim_final_status.json`
- `PUBLIC_AUDIT_LIMITS.md`

## Expected Current Reading

- package imports cleanly from `code/src`
- historical Wave-1 artifact bundle is present
- repo docs explicitly limit M1 and Appendix-E overreach
- `XR-C007` remains `PAUSED_EXTERNAL` for runtime closure
