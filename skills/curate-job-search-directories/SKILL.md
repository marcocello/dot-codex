---
name: curate-job-search-directories
description: Create or update job_directories.csv from a supplied professional profile, search objective, constraints, and source suggestions. Use to choose and rank job-search sources; not to search vacancies.
---

# Curate Job Search Directories

Build a current, deduplicated, ranked source plan for a person's actual search. The plan is an input to `$run-job-search`, not a list of vacancies.

## Inputs

Accept any combination of:

- a `professional-profile` dossier or path to it;
- the user's objective, desired roles, domains, geography, work mode, seniority, company stage, or engagement type;
- sources the user wants included, excluded, or investigated;
- an existing `job_directories.csv` to refresh;
- other artifacts that clarify experience or constraints.

All are optional. Start with what is available. Locate `professional-profile` and `job_directories.csv` in the current workspace unless the user supplies other paths. Do not search unrelated personal directories.

When present, read `professional-profile/PROFILE.md` and `JOB_SEARCH_CRITERIA.md` completely. Read `CAREER_HATS.md` when distinct positioning affects where opportunities are likely to appear. Read repository evidence only when it materially changes the relevant technical ecosystems or communities.

## Resolve missing information

Inspect existing inputs before asking questions. Ask one compact batch only for gaps that materially change source selection, especially:

- the primary objective or role families;
- geography, time-zone, work authorization, remote or relocation boundaries;
- employment, founder, contract, fractional, or other engagement types;
- sectors, communities, or company stages to prioritize or exclude;
- paid, authenticated, or invite-only sources the user is willing to use.

If the user does not answer, proceed with clearly stated working defaults from the dossier and keep uncertain sources broad enough for discovery. Never infer a hard constraint from location or career history alone.

## Research and select sources

Provider coverage, names, URLs, access models, and regional usefulness change over time. Verify current facts online using official provider pages where possible. Do not create accounts, subscribe, pay, or change external settings.

Choose a deliberate mix rather than a generic directory dump:

- broad primary platforms with relevant inventory;
- geography- or work-mode-specific boards;
- role, domain, seniority, or company-stage specialists;
- direct company, accelerator, community, association, or funding-portfolio sources when they match the objective;
- supplemental aggregators only when they add coverage beyond the primary set.

Evaluate each source on current inventory fit, geographic eligibility signals, search/filter quality, listing freshness, directness, duplication risk, access friction, and relevance to supported experience and desired positioning. Do not treat popularity as sufficient fit.

## Create or update the CSV

Use this exact header for a new file:

```csv
Rank,Platform,Category,URL,Notes,Recommended combination
```

- `Rank`: consecutive positive integers; lower means search earlier.
- `Platform`: current recognizable source name.
- `Category`: a small set of useful groupings derived from this search, not a universal taxonomy.
- `URL`: canonical source or pre-filtered search URL when stable and genuinely helpful.
- `Notes`: concise evidence-based explanation of coverage, strengths, access limits, or duplication risk. Do not embed private profile facts.
- `Recommended combination`: `Yes` for the compact complementary set that should be searched most often, otherwise `No`.

For an update, preserve user-added sources and notes unless they are superseded, duplicate, inaccessible, or explicitly excluded. Verify changed URLs and provider names. Deduplicate by canonical URL and platform identity, then rerank the complete file. Do not leave gaps or duplicate ranks.

The recommended set should cover the main objective with complementary sources; it is not simply the top N rows. Keep the overall list proportionate to the search rather than targeting a fixed count.

Write with a CSV-aware tool and validate that every row has six columns, a unique positive rank, an absolute HTTP(S) URL, and a `Yes` or `No` recommendation.

## Return the receipt

Report the output path, sources added, updated, removed, or retained, the logic behind the recommended combination, working defaults, unresolved constraints, and any source whose current status could not be verified. Do not run the vacancy search unless the user also asks for it.
