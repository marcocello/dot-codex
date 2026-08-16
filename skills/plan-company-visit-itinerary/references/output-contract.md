# Output contract

## Workbook sheets

### Trip Overview

Include:

- Workday start and end.
- Visit and lunch durations.
- Starting point, return-to-start choice, planning mode, and maximum days when limited.
- Extracted, deduplicated, scheduled, and unscheduled company counts; day count; total visit hours; estimated drive hours; and latest planned finish.
- One row per day with area/route label, stop count, departure time, first visit, planned finish, visit hours, start/inter-stop/return drive minutes, lunch minutes, buffer minutes, Google Maps directions URL, and appointment note.
- A visible call-ahead warning.

Drive, visit, finish, and buffer outputs must be formulas referencing itinerary cells or explicit assumption cells where practical.

### Daily Itinerary

Include one row per visit:

- Day and stop number.
- Visit start and end.
- Travel minutes from the previous stop.
- Company, city, category, routing address, phone, and stable source identifier.
- Address status and visit note.

Keep days contiguous and ordered. Freeze headers, use readable time formats, and highlight corrected or completed addresses.

### Unscheduled

Create this sheet whenever any company is omitted from the route. Include source identifier, company, city, priority/source signals, address status, omission reason, selection rank, and suggested next cluster/day. Distinguish day-limit omissions from missing-address or unresolved-identity blockers.

### Source Companies

Preserve:

- Stable source identifier.
- Company and original source fields.
- Original city and address.
- Routing city and address.
- Address status.
- Plain-text verification URL for researched corrections.
- Source file, source section/location, original text, duplicate provenance, extracted priority/verification signals, and selection reason.

Never overwrite the original address with the routing address.

## Google Maps directions URL

Generate one daily route URL with this structure:

```text
https://www.google.com/maps/dir/?api=1&origin=<encoded starting point>&destination=<encoded final location>&waypoints=<encoded stop 1>|<encoded stop 2>&travelmode=driving
```

When the route does not return, use the final company as destination and put all earlier companies in waypoints. For a round trip, use the starting point as destination and put every company in waypoints. Store the complete URL as a cell value if workbook rendering does not support `HYPERLINK`; do not leave formula-engine diagnostic text in the workbook.

## Validator input

`companies.json` is an array with unique `id` values:

```json
[
  {"id": 1, "company": "Example Manufacturing", "address": "100 Main St, Dallas, TX 75201"}
]
```

`plan.json` has this shape:

```json
{
  "mode": "limited",
  "maxDays": 3,
  "workdayStart": "09:00",
  "workdayEnd": "18:00",
  "visitMinutes": 90,
  "lunchMinutes": 30,
  "lunchAfterStop": 2,
  "startLocation": "Austin Convention Center, Austin, TX",
  "returnToStart": false,
  "days": [
    {
      "day": 1,
      "startTravelMinutes": 20,
      "returnTravelMinutes": 0,
      "stops": [
        {"id": 1, "travelFromPreviousMinutes": 0},
        {"id": 2, "travelFromPreviousMinutes": 15}
      ]
    }
  ],
  "unscheduled": [
    {"id": 3, "reason": "Outside the three-day capacity after higher-priority geographic clusters"}
  ]
}
```

`lunchAfterStop: 2` means lunch occurs after the second visit and before travel/arrival for the third visit.

Use `mode: "all"` with no day limit to require full scheduling. Use `mode: "limited"` with a positive `maxDays`; the union of scheduled and unscheduled identifiers must then equal the company list exactly.

## Workbook verification

Before export:

1. Inspect summary and representative itinerary ranges with values and formulas.
2. Scan for `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, and `#N/A`.
3. Reconcile extracted mentions, deduplicated companies, scheduled and unscheduled identifiers, and day-summary totals.
4. Render every sheet at least once.
5. Fix clipped headers, unreadable URLs, excessive wrapping, broken links/formulas, blank sheets, and visually hidden corrections.
6. Export exactly one final workbook unless variants were requested.
