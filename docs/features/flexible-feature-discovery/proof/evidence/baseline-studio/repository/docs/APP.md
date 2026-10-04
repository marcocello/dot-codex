# Studio member self-service

## Confirmed purpose

Let existing studio members manage their own bookings, move sessions, join waiting lists, and see remaining credits. The current request authorizes repository investigation, discussion, and narrow draft specifications only.

## Current evidence

`README.md` describes a staff-operated terminal booking desk and payments recorded at reception. The actual `studio.py` only reads `schedule.json` and prints it. There is no implemented booking operation, login, web interface, credit transaction history, or waiting list. The sample has one class, a booking identified by member name, and one member with five credits. It does not establish production rules or a source of truth.

## Proposed journey — awaiting decisions

An existing member opens a mobile-friendly member page, signs in, sees their bookings and credit balance, chooses a class, and receives a saved booking confirmation with the updated balance. Later slices allow cancellation, moving a booking, and joining or leaving a waiting list. Reloading the page must show the saved result. Staff need to see the same authoritative records.

Recommend keeping payment collection at reception for the first release. Online payment, public account registration, recurring bookings, attendance tracking, and reporting are outside the proposed scope. These are recommendations, not accepted exclusions.

## Proposed delivery slices

| Order | Outcome | Contract | Proof preparation |
| --- | --- | --- | --- |
| 1 | A member sees their own bookings and remaining credits | [Member overview](features/member-overview/FEATURE.md) | [Placeholder](features/member-overview/PROOF.md), [runner](features/member-overview/proof/run.sh) |
| 2 | A member books one available class | [Book a class](features/book-class/FEATURE.md) | [Placeholder](features/book-class/PROOF.md), [runner](features/book-class/proof/run.sh) |
| 3 | A member cancels one booking under studio policy | [Cancel a booking](features/cancel-booking/FEATURE.md) | [Placeholder](features/cancel-booking/PROOF.md), [runner](features/cancel-booking/proof/run.sh) |
| 4 | A member moves one booking without losing it if the destination is unavailable | [Move a booking](features/move-booking/FEATURE.md) | [Placeholder](features/move-booking/PROOF.md), [runner](features/move-booking/proof/run.sh) |
| 5 | A member joins or leaves a full class waiting list | [Waiting list](features/waiting-list/FEATURE.md) | [Placeholder](features/waiting-list/PROOF.md), [runner](features/waiting-list/proof/run.sh) |

Lifecycle status is recorded only in [status.json](features/status.json). Product questions and recommendations are in [DISCOVERY.md](DISCOVERY.md). None of these recommendations has been accepted yet.
