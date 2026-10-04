# Join and leave a waiting list

## Outcome

A member records interest in one full class, sees that interest after reload, and can withdraw. A released place follows the studio's chosen promotion process.

## Proposed observable behavior

The full-class view offers one waiting-list entry per eligible member and class. Joining does not itself confirm a booking. Leaving removes the interest safely, including after retries. Show the member's current state clearly and protect other members' details. The chosen promotion path must lead to a visible saved booking or a clear expired/withdrawn offer, without overbooking or charging twice.

## Boundaries and prerequisites

Depends on booking and cancellation capacity updates and the chosen promotion policy. Recommend keeping the first scope to one-class interest plus the smallest operationally complete promotion handoff. If automated offers are selected, separate their delivery/expiry work into another narrow feature instead of hiding it inside joining a list.

## Decisions

Confirmed: members need to join waiting lists. Recommended: no joining debit and an offer to the next eligible member rather than immediate automatic booking. Pending: staff-managed versus automated promotion, priority, credit eligibility, notification channel, offer expiry, interaction with direct bookings, and withdrawal while an offer is outstanding. See [discovery decision 3](../../DISCOVERY.md). Do not call a queue complete without settling how freed spaces reach members.

## Intended demonstration

Join and leave through the member entry, read back the durable list state, then free a place and observe the agreed promotion handoff and eventual booking/credit result. Independent acceptance remains to be authored.
