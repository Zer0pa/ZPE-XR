<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>

<table align="center" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td width="33%"><a href="README.md"><img src=".github/assets/readme/nav/what-this-is.svg" alt="Front Door" width="100%"></a></td>
    <td width="33%"><a href="SECURITY.md"><img src=".github/assets/readme/nav/go-next.svg" alt="Security" width="100%"></a></td>
    <td width="33%"><a href="GOVERNANCE.md"><img src=".github/assets/readme/nav/runtime-proof.svg" alt="Governance" width="100%"></a></td>
  </tr>
</table>

# Contributing

This repository is evidence-first. A contribution that narrows uncertainty is useful; a contribution that inflates a claim without proof is not.

<p>
  <img src=".github/assets/readme/section-bars/evidence-discipline-as-community-norm.svg" alt="GROUND RULES" width="100%">
</p>

## Ground Rules

- keep scope tight
- do not rewrite historical failures into passes
- do not add claim language unless you also add the proof path
- do not commit secrets, local credentials, or machine-specific paths

<p>
  <img src=".github/assets/readme/section-bars/environment-setup.svg" alt="SETUP" width="100%">
</p>

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install "./code[dev]"
python ./executable/verify.py
```

If you touch runtime behavior or proof-generation scripts, also run:

```bash
python -m pytest ./code/tests -q
```

<p>
  <img src=".github/assets/readme/section-bars/pr-process.svg" alt="PULL REQUEST BAR" width="100%">
</p>

## Pull Request Bar

- state the exact problem
- list the files changed
- name any claim or proof surface affected
- include the smallest command set that reproduces your result
- leave contradictory evidence in place and explain it

`LICENSE` is the legal source of truth for contribution terms.

<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>
