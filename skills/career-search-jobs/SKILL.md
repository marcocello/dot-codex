---
name: career-search-jobs
description: Search configured job sources, evaluate current vacancies against a supplied professional profile and criteria, and merge URL-unique findings into a dated CSV. Use to execute and record job discovery.
---

# Run Job Search

Search configured sources one at a time and leave an auditable cumulative findings file. Never submit an application, contact an employer, or mutate an external account.

## Resolve the run

Locate these workspace inputs or use paths supplied by the user:

- `job_directories.csv`;
- `professional-profile/PROFILE.md`;
- `professional-profile/JOB_SEARCH_CRITERIA.md`.

Read them completely before searching. Read `CAREER_HATS.md` when present so queries can use distinct credible positionings without blending them into one generic identity. If a required input is absent, ask for its location. Use `$career-curate-job-sources` when the source list itself must be created or materially refreshed.

The user may name a source by `Rank`, `Platform`, or `URL` using an exact case-insensitive match. Search only that source when the match is unique. Otherwise, process every row sequentially by ascending `Rank`; do not pause for confirmation between sources. Record access limitations or zero-result outcomes and continue.

Use `job_findings.csv` in the workspace root as the cumulative output unless another path is supplied. Read existing findings to avoid re-analysis, but never present old judgments as new work.

## Search each source

Build queries from the role families, capabilities, domains, geography, seniority, and constraints in the supplied profile and criteria. Use only the combinations that fit the current source; do not collapse incompatible positionings into one broad query.

Use an appropriate mix of browser interaction and link extraction:

- Dynamic, authenticated, or filter-heavy source: establish the result state in the browser, then extract listing URLs from the rendered page or DOM.
- Static or indexable source: extract listing URLs from result pages first, then inspect credible listings and confirm filters or pagination.
- JavaScript shell or suspiciously few links: switch to browser navigation.
- Repeated cards or infinite scroll: extract and deduplicate links before detailed review.
- Mostly excluded roles: refine terms or filters once, then reassess the result set.

Stop when the visible result surface yields no new credible URLs or access prevents further verification. State partial coverage honestly.

Open each credible listing and capture only facts supported by the actual page. Prefer active direct job pages over snippets, category pages, repost summaries, or expired listings. Keep the source listing URL as the finding identity. Do not bypass authentication, paywalls, anti-bot controls, or CAPTCHAs. Leave unavailable fields blank and put material unknowns in `missing_constraints`.

## Gate and score

Apply confirmed hard constraints before scoring:

- Set `fit` to `reject` when the listing violates an explicit exclusion or confirmed practical constraint.
- Do not reject for an unresolved user-owned constraint. Record the unknown and score only supported evidence.

For a new findings file, use four generic components:

- `role_scope_points` (0–30): match to desired work, responsibility, ownership, and seniority;
- `experience_evidence_points` (0–25): match to capabilities, achievements, and domains supported by the profile;
- `objective_alignment_points` (0–20): match to the current objective and preferred positioning;
- `practical_conditions_points` (0–25): company, location, work mode, compensation when known, and other practical conditions.

`overall_points` is their sum. Unless rejected, assign `strong` for 80–100, `good` for 65–79, `possible` for 50–64, and `weak` for 0–49. Use the full ranges and award no points for missing evidence.

When `job_findings.csv` already exists, preserve its exact header and scoring component names. The merge helper supports the earlier scorecard as a compatibility format. Do not mix schemas in one file or silently reinterpret historical scores.

## Build and merge the CSV

For a new file, use this exact header:

```text
analysis_date,provider,provider_rank,job_title,company,location,work_mode,employment_type,job_url,listing_date,role_scope_points,experience_evidence_points,objective_alignment_points,practical_conditions_points,overall_points,fit,reason,missing_constraints
```

For an existing file, use its exact header. Create one temporary incoming CSV per source containing only listings analyzed during this run. Use the source's `Platform` and `Rank`, the current local date in `YYYY-MM-DD`, and one concise evidence-based `reason`. Sort incoming rows by descending `overall_points`. Do not manufacture an empty finding row for a zero-result source.

Merge after each source:

```bash
python3 <skill-directory>/scripts/merge_findings.py \
  --existing <workspace>/job_findings.csv \
  --incoming <temporary-incoming.csv>
```

The helper validates supported schemas, dates, component totals, and URLs; preserves historical order; appends only unseen canonical URLs; and atomically replaces the target. Correct invalid incoming data rather than editing around a validation failure.

## Return the receipt

Report the analysis date, sources processed in rank order, per-source verified/appended/duplicate counts, zero-result or access status, output path, strongest new matches with direct URLs, remaining constraints, and whether coverage was partial. Say explicitly when no new URLs were added.
