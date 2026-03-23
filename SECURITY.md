<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-XR Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/scope.svg" alt="SCOPE" width="100%">
</p>

This document covers vulnerability reporting for the ZPE-XR package, build surface, and proof artifacts in this repository.

What counts as a security issue here:

- secrets, tokens, or credentials committed to the repo
- dependency or supply-chain vulnerabilities that affect the shipped package or workflows
- arbitrary-code-execution, privilege-escalation, or unsafe parser behavior in the XR package surface

What does not count as a security issue here:

- failed comparator rows or negative benchmark results
- release-readiness disagreements without a security impact
- claim-boundary disputes that belong in `proofs/FINAL_STATUS.md` or `PUBLIC_AUDIT_LIMITS.md`

<p>
  <img src=".github/assets/readme/section-bars/reporting-a-vulnerability.svg" alt="REPORTING A VULNERABILITY" width="100%">
</p>

Do not open a public issue for a security vulnerability.

Report privately to:

- `architects@zer0pa.ai`

Include:

- the affected component or file
- reproduction steps or a proof of concept
- impact and severity assessment
- any remediation guidance you already have

<p>
  <img src=".github/assets/readme/section-bars/response-commitment.svg" alt="RESPONSE COMMITMENT" width="100%">
</p>

| Stage | Target timeframe |
|---|---|
| Acknowledgement | Within 48 hours |
| Initial assessment | Within 7 days |
| Remediation or mitigation plan | Within 30 days for confirmed issues |
| Public disclosure | Coordinated with reporter |

<p>
  <img src=".github/assets/readme/section-bars/secret-scan.svg" alt="SECRET SCAN" width="100%">
</p>

There is no separately promoted XR secret-scan report in this staged repo. If you identify a leaked secret or credential, report it through the private channel above and treat it as a priority incident.

<p>
  <img src=".github/assets/readme/section-bars/supported-versions.svg" alt="SUPPORTED VERSIONS" width="100%">
</p>

| Version | Supported |
|---|---|
| `0.3.0` | Current staged package snapshot |
| Earlier internal snapshots | Not supported |

<p>
  <img src=".github/assets/readme/section-bars/out-of-scope.svg" alt="OUT OF SCOPE" width="100%">
</p>

- `LICENSE` interpretation is a legal-routing question, not a security policy override.
- External engine/runtime partner surfaces remain outside this repo until they are actually imported here.
- Negative benchmark outcomes remain engineering truth, not security incidents.
