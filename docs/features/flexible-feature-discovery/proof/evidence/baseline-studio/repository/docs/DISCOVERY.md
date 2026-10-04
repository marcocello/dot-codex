# Direction and open decisions

## Recommendation

Start with a read-only member overview to establish identity and trustworthy existing records. Then deliver one-class booking, cancellation, session moves, and waiting lists as separate outcomes. This order makes each interaction demonstrable without bundling all four workflows into a single release.

## Decisions to discuss

1. **Entry and authoritative records:** Is this checkout the intended operational booking system, or do staff currently use another app, spreadsheet, or ledger? Recommend a mobile-friendly member website for existing members, with payments still recorded at reception. We need to know how members will be invited or verified and how staff changes will reach the same records before the first slice is deliverable.
2. **Credits and cancellation:** Does one booking use one credit immediately, and what happens for a cancellation or move? Recommend reserving/deducting the credit at booking, restoring it only for an eligible cancellation, and keeping a same-price move neutral. The studio must supply its actual cancellation/move cutoff, late-cancellation treatment, credit expiry/package restrictions, and timezone. For example, moving a class shortly before it starts could otherwise bypass a late-cancellation charge. The sample's five credits do not tell us whether an existing booking is already charged.
3. **Waiting-list promotion:** When a space opens, should the next member receive an offer to accept, or be booked automatically? Recommend an offer in join order, with no credit charge merely for joining and a charge on acceptance. This avoids an unexpected reservation or debit, but requires a notification channel and an offer expiry policy. A staff-managed promotion queue is a smaller alternative if that matches the studio's current process. We need the chosen approach, timing, eligibility, and priority rules before this feature can be accepted.

## Evidence and scope

Inspected `README.md`, `studio.py`, and `schedule.json`. Ran `python3 studio.py` successfully and observed exactly the sample schedule. This verifies the local reader only; it does not demonstrate staff booking or member self-service. No application code or sample data was changed.

Draft contracts deliberately retain these unresolved decisions. Independent executable acceptance has not been authored: the associated proof files and failing runners are explicit placeholders, not evidence of readiness. After these decisions are answered, reconcile the contracts and have an independent author prepare proof against the agreed user entry point and persisted state before implementation.

## Local verification

The sample reader ran successfully. All relative documentation links resolve. Every placeholder proof runner exits with code 2 and an explicit not-ready message, so no placeholder can report feature acceptance.

The shared repository gate was run with the Python profile and required feature status. It reported existing setup gaps: no `.gitignore`, no Python project manifest, no source in its expected `src/`, `app/`, `backend/`, or `scripts/` directories, and no `.venv/bin/python`. The root-level `studio.py` exists and runs; the source-layout finding is the gate's convention, not absence of Python code. Git diff is unavailable because this checkout has no Git metadata. These setup findings were retained without restructuring the application during a discussion-only request.
