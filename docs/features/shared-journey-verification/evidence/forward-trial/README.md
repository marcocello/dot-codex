# Local contact registry

Run `python3 contacts.py --db PATH --owner OWNER add NAME EMAIL`, `list`, or `export`. The CLI receives an already-authenticated owner from its caller; it is not a login system. The SQLite database persists between invocations. No external services.

Accepted outcomes for the next delivery round: (1) save contacts for an owner, list them after restarting the CLI, reject duplicate emails within that owner without losing existing contacts; (2) export that owner's contacts as CSV with correct escaping and a header even when empty. Other owners must never appear in list/export; the same email may belong to two different owners.

The current script is a candidate, not evidence that these outcomes pass.
