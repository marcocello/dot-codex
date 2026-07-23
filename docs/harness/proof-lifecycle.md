# Proof Capture

Owner: `"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture"`.

## Command
```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir FEATURE_DIR --timeout-seconds N --note "reason"
```

- Executes exactly `FEATURE_DIR/proof/run.sh` from repo root.
- Caller chooses positive timeout.
- No substitute command, source list, checks, gate, evaluation metadata.

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

Immediately after an attempt passes and before it enters the repository gate or managed evaluator, the parent initializes plain `completion.md` with `NOT RUN` stage context. It updates the same file with:

- gate command and outcome, or skip reason;
- evaluator output when run;
- material correction or repair context worth carrying forward.

`completion.md` is learning context. It is never parsed to derive completion, freshness, progress, or evaluator validity.

On resume, a prior passing attempt without `completion.md` has incomplete managed-stage history. Reconstruct exact gate/evaluator context when it remains available; otherwise record that the context is missing and do not claim the retained learning path is complete.

Start/result context:
- command; cwd; UTC start/end; duration; timeout;
- capture PID; runner PID/PGID;
- return/status; interrupt signal;
- safe platform, release, machine, capture Python executable/version, shell;
- process-group cleanup result.

No full environment dump. No hashes/receipts/schema graph.

The generic runner cannot infer the application stack. `proof/run.sh` prints the relevant non-secret actual application runtime and readiness facts to stdout, such as the executable path/version, selected mode, or service versions used by the scenario.

## Process Safety
- Runner starts new session/process group.
- Cleanup runs after success, failure, timeout, KeyboardInterrupt, SIGHUP, SIGTERM, SIGQUIT.
- TERM group; grace; KILL group when needed.
- Cleanup failure makes attempt fail.
- Runner must not daemonize, `setsid`, `disown`, or escape group.
- Hard SIGKILL/host crash cannot run cleanup. Start record remains when filesystem write completed.

Statuses: `PASS`, `FAIL`, `TIMEOUT`, `INTERRUPTED`.

## Retention
- Keep every official attempt.
- Git-trackable. Related feature commit includes all attempts.
- Attempt note: why run; after mechanical proof change, what changed + why strength unchanged.
- Full stdout/stderr retained. Secret redaction/size cap deferred.
