# Member overview

## Outcome

An existing member can open the member experience and see their own upcoming bookings and remaining credits.

## Proposed observable behavior

After identity verification, show the member's bookings with class date/time in the studio timezone and a credit figure whose meaning matches the studio ledger. Reloading obtains the authoritative data. Members with no bookings see an empty state; unauthenticated users and other members cannot read this member's records. An unavailable source produces an explicit error rather than a misleading zero balance.

## Boundaries and prerequisites

This slice is read-only. It introduces the minimum member entry/access needed for the visible outcome; booking changes and online payments are excluded from this proposed slice. Preserve the existing sample-reader behavior while adopting production records through an agreed path.

## Decisions

Confirmed: members need to see bookings and remaining credits. Recommended: existing-member access through a mobile-friendly website. Pending: authoritative records and staff update path, identity verification, credit definition, studio timezone, and whether future bookings are already deducted. See [discovery decisions 1–2](../../DISCOVERY.md).

## Intended demonstration

A verified member opens the real entry point and sees records that match independently observed authoritative data; another member cannot obtain them. This describes the outcome only; independent acceptance remains to be authored.
