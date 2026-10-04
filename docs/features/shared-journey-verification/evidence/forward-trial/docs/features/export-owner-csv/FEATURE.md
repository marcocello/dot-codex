# Export owner contacts as CSV

Accepted from README: export an owner's persisted contacts through the public CLI.

- AC1: Export the owner's persisted name and email values with correct CSV escaping and a name/email header.
- AC2: An empty owner exports the header with no contact records.
- AC3: Another owner's contacts never appear in this export.

Export composes with saved contacts in the same database. The caller supplies an authenticated owner; this feature adds no login mechanism.
