# Contact save, reopen and export journey

Done for this check means all deterministic assertions in `proof/check.py` pass through the real CLI. This author execution establishes local runnable acceptance; it is not implementation completion or an independent final review.

Command from repository root: `docs/verification/contact-journey/proof/run.sh`. Requires Python 3 with standard-library sqlite3, csv and json; no external services or credentials. Target: `local-cli-python3`, using the repository's actual `contacts.py`. The runner creates and removes a temporary SQLite database outside the source tree. Every action launches a separate Python process with the documented `--db`, `--owner` and subcommand arguments. State belongs to SQLite; observations are public list JSON and parsed export CSV on stdout. There are no fakes or seeded rows.

| Criteria | Starting state / activation | Independent consumer read-back | Defect caught |
| --- | --- | --- | --- |
| save-owner-contacts AC1 | Absent database; add three contacts through separate CLI invocations | New list process returns exactly the submitted values | No commit, process-local state, missing or changed contact |
| export-owner-csv AC1 | Same persisted contacts; run export in another process | Standard-library CSV parser returns header and exact submitted names/emails | Missing rows, hand-joined CSV, broken quote/comma/newline escaping, Unicode corruption |
| export-owner-csv AC2 | Export before any add; export unused owner after populating database | Exactly one name/email header in both cases | Missing first-use header or nonempty result for empty owner |

The name/email header and JSON pair list reuse the existing public representation as a compatibility assumption; row order and exact diagnostic wording are not promised. Inputs contain ordinary text, a comma, quotes, newline and non-ASCII text. Exact record comparisons detect both missing and extra records. One deterministic run is appropriate for this local sequential contract; it does not claim concurrency, crash durability, broad encoding compatibility or performance reliability.

Proves save -> fresh process -> list/export composition and empty exports against the candidate. Does not prove caller authentication, deployment, multiwriter concurrency, inaccessible/corrupt database recovery, email normalization, or spreadsheet formula safety; these are not accepted outcomes. The separate contact-isolation package supplies duplicate and permission negatives. A implementation tailored to these finite samples could still pass; no claim of exhaustive input coverage is made.

Independent acceptance author: `/root/forward_trial`; feature specification author: parent task `/root`, grounded in README. No application behavior was changed. Capture is partial: the native task conversation owns dialogue; `proof_run_capture.py` retains output, snapshots and candidate fingerprints for executed checks. Determining inputs are README, contacts.py, both FEATURE/COVERAGE packages and this check tree; broad repository capture is used. No implementer or final-reviewer attribution has been asserted.
