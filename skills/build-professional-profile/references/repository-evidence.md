# Repository evidence

Use repository inspection to support capability claims without overstating authorship, production impact, or business outcomes.

## Scope and inventory

For each explicitly authorized repository or root:

1. record its path or canonical URL, repository name, visibility if known, and inspection date;
2. distinguish repositories, nested repositories, generated copies, forks, vendored code, examples, empty projects, and deployment-only directories;
3. record the remote and current branch when locally available;
4. inventory before choosing which repositories deserve deep review;
5. give every reviewed, partial, inventoried, or excluded item a stable ledger ID.

For a large repository root, prioritize sources relevant to the stated objective, then state the selection method and what remains only inventoried. Never imply exhaustive review.

## Contribution boundary

Inspect available authorship evidence such as commit history, contributor summaries, file history, and explicit project documentation. Match identities conservatively. In collaborative or forked repositories:

- separate the subject's attributable contribution from upstream or colleague work;
- avoid assigning entire-system ownership from a minority of commits;
- exclude repositories with no interpretable subject contribution from capability claims;
- describe derivative origins and substantial inherited scaffolds;
- treat local uncommitted work as evidence only when ownership is clear from the task context.

Authorship counts are supporting context, not a proxy for quality or impact.

## Inspect meaningful surfaces

Choose representative evidence across the surfaces that matter to the claim:

- product and architecture documentation;
- manifests, language and framework boundaries;
- central domain or application code;
- tests, proof, evaluation, and quality controls;
- migrations, persistence, authorization, integrations, and background work;
- infrastructure, CI/CD, observability, recovery, and operations;
- commit history showing recency and sustained contribution.

Do not expose secrets or reproduce proprietary implementation details beyond what is needed for a private capability dossier.

## `REPOSITORY_EVIDENCE.md` structure

Include:

- authorized scope and explicit exclusions;
- method and limitations;
- a summary table of repositories, contribution evidence, demonstrated capabilities, and confidence;
- short evidence notes for each reviewed repository;
- cross-repository patterns that require more than one repository to support;
- claims the repositories cannot establish;
- unresolved attribution or production-status questions.

Use restrained language:

- `demonstrates` for directly observed attributable behavior;
- `supports` for a claim with multiple consistent signals;
- `suggests` for a reasonable but incomplete inference;
- `does not establish` for commercial use, production scale, team ownership, or results that code alone cannot prove.

Feed only supported conclusions into `PROFILE.md` and `CAREER_HATS.md`.
