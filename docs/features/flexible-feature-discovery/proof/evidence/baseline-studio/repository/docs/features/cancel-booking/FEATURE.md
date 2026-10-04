# Cancel one booking

## Outcome

A member cancels one of their own bookings and sees the released space and any credit refund allowed by studio policy.

## Proposed observable behavior

Show the cancellation consequence before confirmation. Apply the agreed cutoff and refund rule, then show the updated booking and credit result after reload. A repeated request cannot refund twice. Another member cannot cancel the booking. Unavailable persistence leaves the original booking and balance consistent.

## Boundaries and prerequisites

Depends on `book-class` and the agreed cancellation rules. Cancellation is proposed as a narrow interpretation of “manage bookings,” requiring confirmation; it is distinct from moving a booking. Staff exceptions and waiting-list promotion belong to separately agreed boundaries.

## Decisions

Recommended: release capacity on a successful cancellation and restore credit only when eligible. Pending: whether late cancellation is allowed, its credit consequence, cutoff, timezone, and cancellation treatment for legacy/payment types. See [discovery decision 2](../../DISCOVERY.md).

## Intended demonstration

Cancel through the real member experience on both sides of the agreed cutoff, inspect persisted capacity and credit outcomes, and retry safely. Independent acceptance remains to be authored.
