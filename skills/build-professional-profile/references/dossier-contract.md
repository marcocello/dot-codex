# Dossier contract

Use this contract to keep the output useful across applications, opportunity evaluation, interviews, biographies, and future updates. Adapt headings to the evidence; do not generate empty ceremonial sections.

## `PROFILE.md` — required

The canonical career and capability record. Include:

- an `as of` date and a one-sentence identity;
- a professional thesis explaining the strongest recurring pattern;
- current professional picture;
- a reverse-chronological career timeline with supported role dates and scope;
- education or credentials when relevant;
- a high-confidence achievement bank;
- a capability map that distinguishes depth, recency, and evidence strength;
- domain exposure and an evidence-grounded operating style;
- source conflicts and positioning risks;
- missing facts or questions that could materially improve the dossier.

Keep facts reusable rather than tailoring the master profile to one vacancy. Avoid personality claims inferred from a single artifact.

## `CAREER_HATS.md` — conditional

Create when the subject has several credible positionings or wants role tailoring. Use as many distinct hats as the evidence supports, normally three to ten; do not pad to ten.

Start with a comparison table covering positioning, plausible titles, strongest fit, and main risk. For each hat include:

- the concise positioning and problems this person can credibly own;
- suitable titles or engagement types;
- strongest supporting evidence and source IDs;
- likely hiring objections, gaps, or framing cautions;
- when to lead with or avoid this positioning.

Hats must be materially different buyer-facing stories, not synonyms for the same role. A recent hands-on builder identity and a historical executive or research identity may coexist, but each must show its evidence and recency.

## `REPOSITORY_EVIDENCE.md` — conditional

Create only when repositories are authorized and actually inspected. Follow [repository-evidence.md](repository-evidence.md).

## `SOURCES.csv` — required

Maintain one machine-readable source ledger with these columns:

```csv
source_id,category,source_type,location,scope,review_status,authority,source_date_or_observed,notes
```

Use stable IDs. Appropriate `review_status` values include `reviewed`, `partially reviewed`, `inventoried`, `registered`, `unavailable`, and `excluded`. Appropriate authority descriptions include `current first-party`, `self-reported`, `repository evidence`, `external corroboration`, `archival`, and `not evidence`.

The count is descriptive, never a target. A source may be inventoried without supporting any claim. Explain exclusions precisely enough that a future maintainer will not accidentally reuse them.

## `README.md` — required for a reusable dossier

Explain:

- the dossier's purpose and privacy posture;
- the recommended read order and what each present artifact does;
- evidence categories and citation conventions;
- the explicitly authorized source scope;
- how to use the dossier without blending every positioning into one story;
- how and when to refresh it;
- the last synthesis date.

Do not list optional artifacts that were not created as though they exist.

## Cross-artifact consistency

- `PROFILE.md` owns canonical facts and conflicts.
- `CAREER_HATS.md` selects and frames those facts; it must not invent new achievements.
- `REPOSITORY_EVIDENCE.md` owns code-derived observations and limitations.
- `JOB_SEARCH_CRITERIA.md` owns preferences and filters, not capability claims.
- `SOURCES.csv` owns provenance and review status.
- `README.md` owns usage and maintenance guidance.

When refreshing, update all affected consumers of a changed canonical fact, but preserve unrelated user-authored content and stable source IDs.
