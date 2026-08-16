---
name: plan-company-visit-itinerary
description: Create verified company visit itineraries from spreadsheets, documents, PDFs, images, or pasted lists, with address research, planning questions, routing, schedules, map links, prioritization, and validation.
---

# Plan Company Visit Itinerary

Turn a company list into a practical, auditable route workbook. Optimize for a schedule a person can actually drive, not merely the theoretical maximum number of visits.

## Required companion skills

Use the `spreadsheets:Spreadsheets` skill for every spreadsheet input or output. Follow its import, formula, rendering, verification, and export requirements. Use its bundled runtime and `@oai/artifact-tool`; do not substitute another workbook library.

Use the matching artifact skill for each source format: `documents:documents` for DOCX, `pdf:pdf` for PDF, and image inspection/OCR capabilities for screenshots or scans. Read [references/input-extraction.md](references/input-extraction.md) when the source is not already a clean table.

## Mandatory planning preflight

Before extracting addresses, researching companies, routing, or building the workbook, send one concise preflight that confirms supplied inputs and asks for every missing answer below:

1. What time should each travel day start?
2. What time should each travel day end?
3. What address or place should each day start from, and should the route return there at day end?
4. What is the average visit duration per company?
5. Should the plan use as many days as needed, or is there a maximum number of days?

Ask only for values the user has not already supplied, but provide a concrete recommended value for each missing decision. Briefly explain recommendations when the tradeoff is material. Use the request, source geography, normal company hours, and other available context. When context does not indicate otherwise, recommend:

- a 09:00–18:00 travel day;
- a neutral, routable hub near the target area as the daily start and end point, clearly identified as a proposed meeting point rather than the user's home or hotel;
- 90 minutes per company;
- as many days as needed when the stated goal is to visit every company; and
- a 30-minute lunch after stop 2.

Present the result as a compact **Recommended plan**, followed by any questions that still require attention. End with: **Reply `Proceed` to use these recommendations, or send the values you want changed.** Treat `Proceed` (or an equivalent unambiguous confirmation) as explicit authorization for all proposed values and continue without asking again. Recommendations are not active until the user confirms them; never silently apply them.

If no safe, routable starting-point recommendation can be derived from the source geography, say so and require that one value before treating `Proceed` as complete authorization.

If the user sets a day limit, explain that the itinerary will include only the companies that fit. Use explicit user priorities first; otherwise maximize feasible visits while favoring source priority signals and geographic efficiency. Keep every omitted company visible in an `Unscheduled` sheet.

## Workflow

1. Inspect every supplied source completely. Render formatted workbooks, DOCX files, PDFs, and scans before deriving records. For DOCX, run `scripts/extract_docx_signals.py` to preserve paragraphs, sections, tables, emphasis, colors, and highlights for classification.
2. Normalize every candidate into a stable record with a source identifier, company, source file/section/location, original text, city, category, original address, phone, priority signals, verification notes, and any useful source fields. Merge repeated mentions only after preserving every provenance location.
3. Audit address quality before routing:
   - Trim tabs and accidental whitespace.
   - Flag missing streets, malformed duplicated numbers, city/address disagreement, misspelled cities, residential-unit wording for industrial businesses, and duplicates.
   - Verify flagged records with the company's official contact page first. Use authoritative directories or mapping listings only when no official source is available.
   - Preserve the original value. Store the routing city, routing address, correction status, and plain-text verification URL separately.
   - Never claim all addresses were verified unless every address was checked.
4. Apply the answers from the mandatory planning preflight. Include travel from the stated starting point to the first company inside the workday. Include the return trip only when the user requested a return to the starting point.
5. Group companies geographically, then order each day to avoid backtracking. Prefer compact city/industrial clusters. Allow a cross-city boundary only when it improves full-list coverage without making the day fragile.
6. Estimate inter-stop driving:
   - Use live route data when an authorized mapping capability is available.
   - Otherwise use conservative planning estimates based on the listed addresses and explicitly label them as estimates.
   - Do not upload the full list to a third-party geocoder without explicit user permission.
7. Simulate each day from the starting point at the workday start: drive to stop 1, visit, drive, visit, lunch at the chosen boundary, then continue. Add the return drive when required. Keep the complete day inside the work window and preserve useful contingency. In unlimited mode, add days until every company is scheduled. In limited mode, stop at the maximum day count and record the remainder as unscheduled.
8. Generate one Google Maps directions URL per day. Use the provided starting point as `origin`. Use the last company as `destination`, or the starting point when the route returns. Put ordered company addresses in `waypoints` as required. Build query strings with a URL encoder and place the route URL beside the day's schedule.
9. Create the workbook defined in [references/output-contract.md](references/output-contract.md).
10. Validate plan coverage and timing with `scripts/validate_itinerary_plan.mjs`, then run workbook formula-error scans and visual checks.

## Address decisions

Make corrections only when evidence is strong. Treat these cases differently:

- Typographic cleanup: normalize whitespace and obvious city spelling while preserving the original.
- Address completion: add a street only from a traceable source.
- Conflicting sources: retain the source address, flag the conflict, and require a phone confirmation.
- Same address for multiple companies: retain both companies and flag the shared location; do not deduplicate businesses by address alone.
- Missing address: research an official street address before routing. If no reliable address is found, keep the candidate unscheduled with a clear blocker rather than inventing a location.

Include a call-ahead note for appointment confirmation, visitor access, parking/loading access, and actual opening hours. Do not infer that a published address accepts unscheduled visitors.

## Route and schedule quality

- In unlimited mode, schedule every normalized company exactly once.
- In limited mode, schedule each selected company once and account for every remaining company in `Unscheduled`.
- Use stable source identifiers instead of row positions after sorting.
- Keep zero-minute travel only for identical or credibly co-located addresses.
- Keep the final planned visit within the workday. Show daily finish and remaining buffer.
- Include start-to-first travel and any required return travel in the schedule, summary, and map route.
- If dates are requested, avoid weekends by default and check opening hours for late-afternoon stops.
- If the user supplies a home base, hotel, dates, priorities, or mandatory appointment times, incorporate them before optimizing.

## Deterministic validation

Write normalized companies and the route plan as JSON using the schema documented in [references/output-contract.md](references/output-contract.md). Run:

```bash
node scripts/validate_itinerary_plan.mjs --companies companies.json --plan plan.json
```

Do not export a final workbook until the validator reports:

- zero unaccounted companies across scheduled and unscheduled records;
- zero duplicates or unknown identifiers;
- every first stop has zero inter-stop travel;
- every day finishes within the work window;
- limited plans do not exceed `maxDays` and account for every unscheduled company;
- the computed company and day totals match the workbook summary.

## Completion

Deliver one polished `.xlsx` workbook unless the user asks for another format. Report extracted candidates, deduplicated companies, scheduled and unscheduled counts, number of days, key assumptions, corrected or unresolved addresses, selection logic, and whether travel times are live or estimated. Never describe a planning estimate as an exact drive time.
