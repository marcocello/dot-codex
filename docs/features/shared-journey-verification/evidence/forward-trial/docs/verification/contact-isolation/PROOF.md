# Owner isolation and duplicate failure check

Done for this check means all deterministic assertions in `proof/check.py` pass through the real CLI. This author run establishes the execution boundary only; it does not complete a feature or substitute for final review.

Command from repository root: `docs/verification/contact-isolation/proof/run.sh`. Requires Python 3 standard library. Target: `local-cli-python3`, actual repository `contacts.py`, a new temporary SQLite database, no external services, no fakes. Input producer is a caller supplying an authenticated owner; every add/list/export is an independent CLI process. SQLite owns persisted state; list JSON and CSV parsed independently with the standard library are the consumer read-backs. No rows are seeded through direct database access.

| Criteria | Activation / read-back | Defect caught |
| --- | --- | --- |
| save-owner-contacts AC2 | Add original and unrelated contacts, submit duplicate with changed name, require nonzero exit and a diagnostic, reread every owner, then add again | Silently accepted duplicates, replacement, prior-record loss, poisoned follow-up writes |
| save-owner-contacts AC3 | Two owners add the same email with distinct names, add private records, list each plus unknown owner and quoted owner | Global uniqueness instead of per-owner uniqueness; missing or unsafe owner filtering |
| export-owner-csv AC3 | Export each owner and unknown owner after duplicate failure; parsed CSV must equal only that owner's known inputs | Export leaks, all-owner query, divergence between list and export isolation |

Exact whole-set read-back observes originals, unrelated records and absent foreign rows, not merely success exits. A quoted SQL-like owner string checks that owner identity remains literal. Exact error text, exit number, ordering, email case normalization and invalid-email policy are deliberately not asserted because the accepted outcomes do not establish them. A nonempty diagnostic is the routine CLI rejection convention. Every owner action uses the same actual database, preventing accidental isolation by separate fixtures.

Proves sequential local CLI owner separation and duplicate rejection with state preservation/recovery. Does not prove caller authentication (explicitly delegated by README), arbitrary concurrent writers, malicious direct database access, deployments, crash recovery, or external services. A finite deterministic sample is sufficient for these scenarios but not a reliability benchmark. The separate contact-journey package covers saved CSV escaping, empty exports and persistence composition. No material accepted criterion is waived.

Independent acceptance author: `/root/forward_trial`; feature specification author: parent task `/root`, from original README outcomes. No behavior edits, implementer or reviewer identity, or completion claims. Native task history retains dialogue; evidence capture is partial and records actual output, snapshots and candidate fingerprints. Determining inputs are README, contacts.py, both FEATURE/COVERAGE packages and this check tree; broad repository capture is used.
