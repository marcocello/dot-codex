# Proof Capture

Owner: `"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture"`.

## Command
```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir FEATURE_DIR --timeout-seconds N --note "reason"
```

- Executes exactly `FEATURE_DIR/proof/run.sh` from repo root.
- Caller chooses positive timeout.
- No substitute command, source list, checks, gate, evaluation metadata.
- Resolved feature, accepted-input, and attempt-base paths must remain inside the repository. Accepted inputs and the attempt base may not use symlink components; rejection happens before execution or retained writes.

## Run Directory
Created before runner start:

```text
attempt-start.json
FEATURE.md
PROOF.md
run.sh
notes.md
stdout.txt
stderr.txt
result.json
```

Start/result context:
- command; cwd; UTC start/end; duration; timeout;
- capture PID; runner PID/PGID;
- return/status; interrupt signal;
- safe platform, release, machine, capture Python executable/version, shell;
- process-group cleanup result.
- accepted proof-input changes detected after runner exit.

No full environment dump. No hashes/receipts/schema graph.

The generic runner cannot infer the application stack. `proof/run.sh` prints the relevant non-secret actual application runtime and readiness facts to stdout, such as the executable path/version, selected mode, or service versions used by the scenario.

## Process Safety
- Runner starts new session/process group.
- Cleanup runs after success, failure, timeout, KeyboardInterrupt, SIGHUP, SIGTERM, SIGQUIT.
- TERM group; grace; KILL group when needed.
- Cleanup failure makes attempt fail.
- Runner must not daemonize, `setsid`, `disown`, or escape group.
- Before runner start, capture holds independent in-memory state for current and retained `FEATURE.md`, `PROOF.md`, and `proof/run.sh`, including content, mode, inode, and change time. A would-be pass that changes either surface, including change-then-restore, fails with code `126` and names the live or retained input.
- Hard SIGKILL/host crash cannot run cleanup. Start record remains when filesystem write completed.

Statuses: `PASS`, `FAIL`, `TIMEOUT`, `INTERRUPTED`.

## Retention
- Keep every official attempt. Narrow debugging checks are not official attempts.
- For new behavior or a known defect, official evidence normally includes one meaningful red attempt when practical, materially distinct official failures, and the final passing attempt.
- Git-trackable. Related feature commit includes all attempts.
- Attempt note: why run; after mechanical proof change, what changed + why strength unchanged.
- Full stdout/stderr retained. Secret redaction/size cap deferred.
