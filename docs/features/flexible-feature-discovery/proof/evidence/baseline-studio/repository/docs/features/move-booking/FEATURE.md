# Move one booking

## Outcome

A member replaces one existing booking with a reservation in an eligible destination class.

## Proposed observable behavior

Choose the booking and destination, review any credit consequence, and confirm. On success, the original place is released and exactly one destination booking is saved. If the destination fills, is ineligible, or the change fails, the original booking and balance remain intact. Repeated confirmation cannot create multiple destination bookings or extra charges. Only the owner can move the booking.

## Boundaries and prerequisites

Depends on `book-class`, the settled cancellation/move policy, and transactional state updates. This slice moves one booking at a time. It does not offer an implicit cancel-then-book operation that risks losing the original place.

## Decisions

Confirmed: members need to move sessions. Recommended: same-cost moves preserve the credit balance and use the same cutoff policy as cancellation, unless the studio deliberately distinguishes them. Pending: allowed destinations, differing credit costs, cutoff, late-move treatment, and whether any exceptional bookings are immovable. See [discovery decision 2](../../DISCOVERY.md).

## Intended demonstration

Move through the member entry, read back the original and destination class plus the credit state, and repeat with a destination that fills during confirmation. Independent acceptance remains to be authored.
