# Book one class

## Outcome

A member reserves one eligible upcoming class and can see the saved booking and resulting credit balance.

## Proposed observable behavior

Starting from the member overview, choose a class with a space, review its credit cost, and confirm. Read-back shows exactly one booking and the corresponding balance. Reject insufficient credit, ineligible or started classes, duplicate booking, and a class that filled during confirmation without changing credits. Two members competing for the final space cannot overbook it; retrying confirmation cannot debit twice.

## Boundaries and prerequisites

Depends on `member-overview` and an authoritative transactional booking/credit path shared with staff. One-off bookings only; packages, online payments, and recurring reservations are outside this proposed slice. No change to reception payment collection is assumed.

## Decisions

Confirmed: members need to manage bookings. Recommended: debit/reserve at successful booking. Pending: credit cost and eligibility, booking window, credit expiry, authoritative records, and member access. See [discovery decisions 1–2](../../DISCOVERY.md). Existing bookings must not be charged again when adopting the new path.

## Intended demonstration

Use the protected member entry to make a booking and read the persisted booking, remaining capacity, and balance after reload. Exercise the final-space conflict and repeated confirmation. Independent acceptance remains to be authored.
