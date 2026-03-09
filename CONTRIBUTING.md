# Contributing

This repository is evidence-first. A contribution that narrows uncertainty is
useful; a contribution that inflates a claim without proof is not.

## Ground Rules

- Keep scope tight.
- Do not rewrite historical failures into passes.
- Do not add claim language unless you also add the proof path.
- Do not commit secrets, local credentials, or machine-specific paths.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e "./code[dev]"
python ./executable/verify.py
```

If you touch runtime behavior or proof-generation scripts, also run:

```bash
python -m pytest ./code/tests -q
```

## Pull Request Bar

- state the exact problem
- list the files changed
- name any claim or proof surface affected
- include the smallest command set that reproduces your result
- leave contradictory evidence in place and explain it

`LICENSE` is the legal source of truth for contribution terms.
