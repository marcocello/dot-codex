# Architecture context

## Existing application

`python3 studio.py` invokes `schedule()`, loads the adjacent `schedule.json`, and prints the complete document. The JSON file currently owns all sample state. There are no third-party dependencies, server routes, write paths, or declared tests in this checkout. The directory has no Git metadata.

The member name links a booking to a member. Class start times omit a timezone. The `credits` field has no definition of reserved, spent, refundable, or expiring credits; `payment: class-pass` does not establish when a debit happened. Do not infer those rules from this fixture.

## Proposed boundaries — not an implementation decision

Recommend retaining Python for business rules and adding a mobile-friendly browser entry point. Authenticate an existing member, apply server-side ownership checks, read or change authoritative booking/credit records, and return a confirmation that can be read back after reload. Use stable member and class-occurrence identifiers rather than display names.

The source of truth is unresolved. If another live booking system exists, its supported interface and permissions must be established before replacing or duplicating it. If this app will own records, booking capacity, credit updates, and session moves need transactional persistence; the current JSON reader is insufficient for concurrent member writes. Resolve the studio timezone before interpreting cutoffs.

Staff booking and reception credit updates must use the same state owner as the member experience. The checkout does not implement those staff operations. Their real workflow is a prerequisite, not an assumed integration.

Member identity verification and any waiting-list notifications may require a provider. No provider has been selected or contacted. Access, delivery reliability, cost, and live verification remain prerequisites where applicable. Do not treat sample data as proof of production access.

No application changes are authorized in this discovery task.
