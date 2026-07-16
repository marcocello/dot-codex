# Finding Schema

Use one evidence record per candidate during analysis. Keep rejected candidates compact unless their rejection prevents a likely false positive.

## Evidence record

- `Pattern`: concise normalized name.
- `Status`: Confirmed, Suspected, or Rejected.
- `Scope`: exact files, components, paths, or runtime boundary.
- `Observed evidence`: repository facts with focused locations or command evidence.
- `Violated invariant`: the rule the system needs but does not preserve.
- `Failure mode`: concrete behavior, delivery, reliability, security, performance, or maintenance consequence.
- `Counter-evidence checked`: strongest fact that could invalidate the candidate and the result of that check.
- `Confidence`: High, Medium, or Low with one-line justification.
- `Remediation direction`: smallest change that restores the invariant; do not prescribe an implementation unsupported by context.
- `Validation`: focused test, trace, benchmark, gate, scenario, or operational observation needed to prove the remediation.
- `Sources`: optional upstream catalog or rule links that materially support the classification.

## Severity

- `P0`: active catastrophic impact or an immediate safety/security boundary failure.
- `P1`: likely serious production, data, security, or delivery failure.
- `P2`: material recurring fragility, scaling limit, or maintenance cost.
- `P3`: bounded weakness with low immediate impact.

Do not raise severity because a pattern has a famous name. Base severity on repository-specific impact and likelihood.

## Output contract

Return sections in this order:

1. `Findings`
2. `Suspected Candidates`
3. `Rejected Candidates`
4. `Remediation Sequence`
5. `Validation Strategy`
6. `Scope Gaps`

For `Findings`, order by severity and then confidence. Include the pattern name, scope, evidence, violated invariant, failure mode, counter-evidence check, minimal remediation, validation, and confidence.

Omit empty `Suspected Candidates` and `Rejected Candidates` sections. Keep `Scope Gaps` explicit when runtime evidence, architecture intent, or relevant paths were unavailable.
