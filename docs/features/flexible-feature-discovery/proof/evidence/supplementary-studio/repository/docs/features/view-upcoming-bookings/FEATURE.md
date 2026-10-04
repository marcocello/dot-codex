# View my upcoming bookings

Status: draft specification. Application implementation and acceptance-proof authoring are explicitly outside this task. This document records the agreed first feature and identifies the remaining delivery prerequisites; it does not declare implementation readiness.

## Outcome and context

Members can answer “Which upcoming classes am I booked into?” without messaging reception. They verify their email, see only their own upcoming bookings, and can judge how current the information is from a visible refresh time.

The repository is a prototype: `studio.py` reads and prints `schedule.json`. Reception's spreadsheet is the authoritative booking record. All sessions are group classes. This feature publishes a read-only copy of that record; it does not change bookings or replace reception's booking process.

## Confirmed scope

- Reception manually imports a CSV containing `member_email`, `member_name`, `class_id`, and `starts_at`.
- Each member has one unique email. Members sign in with a code sent to that email and only see their own bookings.
- The member view shows when the booking data was last refreshed.
- Payments stay at reception. Credit display, new bookings, moves, cancellations, and waiting lists are deferred. Credits are already net of existing bookings, but this feature does not consume or expose them.

## Member journey and visible behavior

1. A member opens the member booking page and enters their email. The page explains that a sign-in code will be sent by email and offers code entry and resend.
2. A valid, unused code establishes an authenticated session for that verified email. Invalid, expired, or already-used codes cannot grant access. A member can sign out; expired sessions require sign-in again.
3. The page reads the latest successfully imported data and displays that member's classes with future start times, ordered soonest first. Each entry shows `class_id` and its date and time, with an explicit time-zone label. The CSV contains no class title, venue, duration, or instructor, so this feature does not invent those details or require extra columns.
4. “Last refreshed” shows the time the latest import completed successfully. Adjacent text explains that the page reflects reception's latest import and directs members to reception if something looks wrong. This timestamp is not represented as the spreadsheet's last edit time.
5. A verified email with no matching upcoming bookings sees a clear empty state and the refresh time. A class ceases to be upcoming when its start time is reached; attendance and completed-class history are outside scope.

Before any successful import, show that booking information has not yet been published, without a fabricated refresh time or prototype sample bookings. A data-service failure shows an unavailable state with a retry route, rather than a misleading empty list.

## Manual refresh and data boundaries

Recommended import contract, pending confirmation with reception: every CSV is a complete snapshot of the bookings to publish. A successful import replaces the previous published snapshot, so bookings removed or corrected in the spreadsheet are reflected after refresh. Do not infer deletions from a partial export. The import mechanism must make the replacement behavior clear to its operator.

Use a staff-only operator import command for the first release, consistent with the current terminal workflow. A staff management interface, scheduled spreadsheet sync, and public upload endpoint are unnecessary for this outcome. Staff require access to the deployed data store; members receive no import permission.

Validate the entire file before publication: required headers and values, usable email addresses, and parseable, unambiguous start times. Reject invalid input with useful row-level errors. Treat a booking as the combination of member email, class ID, and start time; repeated identical rows do not create duplicate displayed bookings. Apply the same email normalization to import and sign-in, trimming surrounding whitespace and comparing consistently without rewriting aliases.

Publish the validated snapshot and its refresh timestamp together. Members must never see a partially imported file. An unsuccessful import preserves both the previous snapshot and its refresh time; the operator receives an explicit failure. A header-only file must not silently erase all published bookings: require an explicit operator confirmation of the empty replacement. Reimporting a valid snapshot is safe and updates its refresh time.

## Access and dependencies

Filter bookings on the server using the authenticated, verified email, including on reload and direct data requests. A requested email, member name, or class ID supplied by the browser cannot broaden access. Do not expose the raw CSV, member directory, other members' bookings, or sign-in codes to members. Keep imported files outside public web assets and avoid logging codes or full imported records.

Email-code delivery must use a real email service in the eventual deployed environment. Codes must expire, be single-use, and have bounded verification and resend attempts. Sign-in responses must not reveal whether another address appears in the booking data. Failure to request or deliver a code needs a recoverable message; no authentication fallback may skip email verification.

The read-only member interface, server-enforced sessions, shared persistent snapshot store, email delivery, and staff import path are necessary parts of this slice. The existing print-only program and sample JSON establish none of those capabilities. Keep payments and reception's spreadsheet workflow compatible; no write-back to the spreadsheet is included.

## Decisions and prerequisites before delivery

- Reception must confirm that its export is a complete replacement snapshot and supply a representative non-sensitive sample. If exports are partial, settle merge/removal behavior before implementation.
- Confirm the studio's time zone and the actual `starts_at` format. Prefer timestamps with explicit UTC offsets. Offset-free timestamps require a declared studio zone and handling for ambiguous daylight-saving times; do not infer the studio zone from the developer's machine. Member-visible times use the agreed studio zone.
- Establish the intended hosting environment, staff access to its import path, and an authorized email sender/service. Email provider capability and delivery have not been verified in this task. Provider choice, credentials, and deployment are not authorized by this specification alone.
- Author the independent acceptance proof in a subsequent task when requested. There are no proof scripts, fixtures, run results, or readiness claims in this package.

Only this first feature is specified. Later credit and booking-action features remain provisional and need their own business rules and acceptance boundaries.
