---
name: build-professional-profile
description: Build or refresh an evidence-backed professional-profile dossier from any available CVs, repositories, portfolios, career artifacts, and objectives. Use for reusable career context, positioning, job-search criteria, application grounding, or an auditable capability inventory.
---

# Build Professional Profile

Create a private working dossier that separates supported facts, interpretation, conflicts, and unknowns. Accept any subset of the following; none is mandatory except enough context to identify the subject:

- CVs, bios, LinkedIn exports or links, portfolios, publications, patents, talks, testimonials, and prior applications;
- local repository paths or repository URLs;
- product, architecture, research, leadership, or delivery artifacts;
- an existing profile dossier to refresh;
- the person's objective, desired roles or engagements, constraints, and preferences.

A path, URL, or file explicitly supplied for this task authorizes read-only inspection of that item. Do not expand into sibling folders, private accounts, or related repositories without authorization.

## Start with the evidence

1. Determine whether this is a new dossier, an in-place refresh, or a targeted artifact request.
2. Inventory the supplied sources before drafting claims. Register unavailable, duplicate, superseded, and intentionally excluded items as well as reviewed sources.
3. Read the most current first-party sources first, then use older or external sources to enrich, corroborate, or expose conflicts.
4. Inspect enough of each source to state its actual scope. Do not call a folder or repository reviewed after seeing only its name or README.
5. Ask a compact batch of follow-up questions only after the initial review reveals missing information that would materially change chronology, positioning, search constraints, authorization, or claim strength.

Do not block useful synthesis on optional details. If the person does not answer, record the gap under missing facts, label any practical assumption as a working default, and avoid turning it into a fact. Stop only when permission or a user-owned decision is necessary to proceed safely.

## Choose the dossier depth

Use `professional-profile/` unless the user supplies another destination.

- **Lean dossier:** `PROFILE.md`, `SOURCES.csv`, and `README.md`. Add `JOB_SEARCH_CRITERIA.md` when the objective involves employment, founder matching, consulting, or opportunity discovery.
- **Full dossier:** the lean dossier plus `CAREER_HATS.md` and, when repositories are supplied or authorized, `REPOSITORY_EVIDENCE.md`.
- **Targeted update:** change only the requested artifact and any source or claim references that must remain consistent.

Prefer the lean dossier when evidence is sparse or the user only needs canonical career context. Prefer the full dossier when tailoring across materially different role families, evaluating opportunities, or demonstrating hands-on capability from code. Never pad the result to reach a predetermined number of hats or sources.

Before drafting, read [references/dossier-contract.md](references/dossier-contract.md). When repository evidence is in scope, also read [references/repository-evidence.md](references/repository-evidence.md). When the objective involves finding or evaluating work, also read [references/job-search-criteria.md](references/job-search-criteria.md).

## Evidence rules

- Cite material claims with stable source IDs such as `[SRC-001]` or `[REPO-001]`, resolved in `SOURCES.csv`.
- Prefer current first-party chronology over older self-reported chronology, but preserve conflicts instead of silently choosing the more impressive version.
- Treat quantified impact, team size, revenue, adoption, scale, and ownership as claims requiring direct support. Retain qualifiers when only self-reported.
- Repository evidence can demonstrate attributable implementation, architecture, testing, operations, and technical judgment. It does not alone prove production use, commercial results, sole authorship, or organizational ownership.
- Separate observation from inference. Use phrasing such as `the repository demonstrates`, `the source reports`, or `the evidence suggests` at the appropriate confidence level.
- Do not copy secrets, credentials, private contact data, home addresses, compensation history, or unrelated personal information into the dossier. Keep useful job constraints only when the person asks for them or supplies them for that purpose.
- State dates and the dossier's `as of` date explicitly. Preserve existing source IDs during refreshes; add new IDs rather than renumbering the ledger.

## Follow-up questions

Prioritize questions in this order:

1. identity or chronology conflicts that affect the master timeline;
2. the intended use and primary objective;
3. authorization or contribution boundaries for shared/private work;
4. desired positioning and identities the person does not want emphasized;
5. practical search constraints such as location, work authorization, compensation, travel, or commitment type.

Ask only what improves the current deliverable. Sensitive job-search details may remain explicitly unknown and must not prevent creation of the professional profile.

## Finish

Cross-check every high-confidence achievement and timeline row against the source ledger. Confirm that excluded and partially reviewed sources are described truthfully, conflicts remain visible, and no positioning outruns its evidence. Summarize which artifacts were created, which were omitted as unnecessary, and the most consequential missing facts.
