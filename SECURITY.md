# Security Policy

## Supported Scope

This policy covers the `zpe-xr` Python package, the `code/rust/` codec crate,
repo verification surfaces under `executable/`, proof artifacts, and
security-sensitive repo assets such as workflows and release metadata.

What counts as a security issue here:

- arbitrary code execution, privilege escalation, or data exfiltration through package or native-code paths
- secrets or tokens committed to the repo
- vulnerable CI/workflow behavior
- supply-chain issues in declared dependencies or published artifacts

What does not count as a security issue here:

- benchmark losses
- codec-quality regressions
- documentation disputes about technical claims

## Reporting

Do not open a public issue for a security vulnerability.

Report privately through:

- GitHub Private Vulnerability Reporting
- `architects@zer0pa.ai`

Include:

- affected component
- reproduction steps or proof of concept
- severity and impact
- suggested remediation if you have one

## Response Targets

| Stage | Target timeframe |
|---|---|
| Acknowledgement | within 5 business days |
| Initial triage | within 10 business days |
| Remediation or mitigation plan | post-triage, based on confirmed severity |

We follow coordinated disclosure and will not take legal action against
good-faith security research that follows this policy.
