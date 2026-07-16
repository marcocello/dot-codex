# Proof Lifecycle

This document holds the detailed proof policy. `AGENTS.md` keeps only the hard operating
contract.

## Contract Split

- `FEATURE.md` describes the product behavior.
- `PROOF.md` describes how completion is proven.
- Proof commands, fixtures, environment notes, and evidence stay out of `FEATURE.md`.
- Non-trivial features need one primary proof command plus at least one executable proof
  artifact.

## Primary Proof

The primary proof should exercise the public boundary that matters:

- API proof calls the route or app client and checks response, state, and side effects.
- UI proof renders or drives the UI and checks visible state or interaction.
- Provider proof uses realistic payloads and prefers safe live read-back when credentials and
  targets exist.
- Worker or scheduler proof seeds the same persisted row, queue message, status, event, or
  trigger input that production writes, runs the normal pickup path, and verifies persisted
  output plus side effects.
- Bug-fix proof starts as the smallest regression that fails before the fix.

Static source checks, string searches, lint, typecheck, and unit tests can support proof, but
they do not replace the primary proof for user-visible behavior.

Unit-level proof can be the right shape only when the unit is the claimed behavior boundary. If the real claim is "a transcript row exists and the transcript workflow processes it," a proof that directly instantiates the worker with a fake session is a secondary unit check, not the primary proof. The primary proof must seed the row or enqueue the item, let the scheduler or consumer select it, and read back the durable state.

Before writing `PROOF.md`, name the proof boundary: producer, activation path, consumer, durable state, read-back, and unsafe external edge. If the proof cannot identify those pieces, it is not ready.

Good primary proofs are realistic flows: clean and ingest provider fixtures, ask through the public app/test ingress, then provider read-back; seed transcript rows from the ingest boundary, run worker pickup, then verify phase transitions and idempotency; send signed webhook payloads or live safe messages and verify ack/final ordering; drive frontend flows with a browser and API stub; run OAuth/API flows against a test database and fake provider endpoints; disable workflow state through the public API and prove downstream writes do not happen; generate and render/extract reports; or cross a real CLI subprocess boundary with a fake executable at the unsafe external edge. Unit tests, source assertions, serializer assertions, and mocked service-return checks are secondary guards for these features, not primary proof.

## Evidence Bundle

For serious feature, issue, UI, API, provider, or workflow proof runs, proof artifacts should
write a run evidence bundle when practical:

```text
FEATURE_DIR/proof/runs/<timestamp>/
  command.txt
  stdout.txt
  stderr.txt
  result.json
  run-metadata.json
  oracle-scope.md
  attempts.json
  repair-notes.md
  agent-observation.md
  agent-observation.json
  screenshots/
  logs/
  provider-readback.json
  notes.md
```

Only create files that have real evidence. Do not fabricate empty screenshots, logs, or
provider read-back.

Minimum useful bundle:

- `command.txt`: exact primary proof command.
- `stdout.txt` and `stderr.txt`: bounded command output.
- `result.json`: machine-readable status, timestamps, and important evidence paths.
- `run-metadata.json`: behavior boundary, proof-scope summary, attempt number, failure class,
  repair action, changed files, and checks when available.
- `oracle-scope.md`: proof scope; what the proof proves, what it does not prove, false-green risks, and evidence strength. The filename remains for compatibility.
- `attempts.json`: prior proof attempts when the runner can record them.
- `repair-notes.md`: concise repair history when the proof pass depended on repair.
- `agent-observation.md`: concise agent-loop behavior when the run needed repeated repair,
  tactic change, `NEED_INPUT`, evaluator repair, green-but-broken handling, or contract repair.
- `agent-observation.json`: optional structured version of the same signal for harness review.
- `notes.md`: short human summary of what was proven and what remained unavailable.

Serious completion evidence uses schema version `3`. `run-metadata.json` records safe Git context plus hashes for `FEATURE.md`, `PROOF.md`, the proof runner, and explicitly declared source paths, while `contracts/` stores the exact non-secret contracts evaluated. Raw Git diffs and arbitrary source contents are not copied into evidence.

For browser proof, include screenshots or video paths when the browser tool can capture them.
For provider proof, include read-back output or a clear manual gap when live state is unavailable.
For local app proof, include relevant recent logs, not full noisy logs.

When a `FEATURE_DIR` exists, the primary proof must use captured evidence. The default and expected path is:

```bash
scripts/proof_run_capture \
  --serious \
  --feature-dir FEATURE_DIR \
  --source-path <implementation-or-proof-input> \
  --behavior-boundary "<producer -> activation -> consumer -> read-back>" \
  --oracle-scope "$(cat FEATURE_DIR/PROOF.md)" \
  --notes "<short proof result summary>" \
  -- <primary proof command>
```

The helper writes the evidence bundle and exits with the wrapped command's exit code. Proof
runners may still write richer browser, provider, or app-specific files into the same bundle
when the helper is too small for the whole scenario. Do not mark a contract `ready` when its
primary proof is only a raw command; wrap it in `proof_run_capture` first.

After the primary proof, capture the gate with `scripts/record_completion_evidence gate --evidence-dir <run-dir> -- <gate-command>`. The done evaluator records its structured verdict with `scripts/record_completion_evidence evaluation --evidence-dir <run-dir> ...`.

Queue items marked `ready`, `in_progress`, `repairing`, or `done` must have `PROOF.md` that calls `scripts/proof_run_capture` and declares at least one `--source-path` for the primary proof. Queue items marked `done` store only `completion.latest_evidence`, pointing at one serious proof bundle containing command, result, notes, run metadata, proof scope, contract snapshots, declared source identity, `gate.json`, and `evaluation.json`. `docs/features/status.json` is only an index: `scripts/validate_feature_queue --feature <id>` derives completion validity from these artifacts and current contract, runner, and declared-source hashes without scanning unrelated items. `scripts/validate_feature_queue --all` is the strict whole-queue audit. Repeated or repaired attempts must also have `attempts.json` with the current attempt number plus failure class and repair action.

## Agent Observation

For serious autonomous runs, proof evidence should observe the agent loop as well as the app result when the loop behavior matters. `agent-observation.md` is required for repeated or repaired proof evidence, and should be written when one of these happens:

- primary proof fails more than once;
- Codex changes tactic;
- `NEED_INPUT` is reported;
- evaluator returns `FAIL`;
- green proof still looks weak or green-but-broken;
- contract repair is needed after implementation started.

Keep it short. It is not a transcript, token log, prompt dump, or full file list. Include only:

```md
# Agent Observation

Context loaded:
- <contracts/docs/runtime state actually read>

Routing decision:
- <skill/path chosen and why>

Failure pattern:
- <what failed at the real boundary>

Repairs attempted:
- <attempts that materially changed tactic or owner>

Tactic change:
- <what changed after repetition, or none>

Contract status:
- <frozen | returned to contract repair | not applicable>

Remaining risk:
- <live gap, setup gap, concurrency gap, or none>
```

This file exists so later review can tell whether Codex behaved well while getting to the result, not only whether the final command passed.

When the loop failure is likely to teach the project or harness, also write the optional machine-readable form:

```json
{
  "schema_version": 1,
  "triggers": ["repeated_proof_failure"],
  "context_loaded": ["FEATURE.md", "PROOF.md", "docs/ARCHITECTURE.md"],
  "routing_decision": "coding-repair because the primary proof failed at the API boundary",
  "failure_pattern": "wrong_layer_patch",
  "repairs_attempted": ["moved fix from helper to route boundary"],
  "tactic_change": "changed from unit-level patch to public API proof repair",
  "contract_status": "frozen",
  "remaining_risk": "none",
  "signals": {
    "asked_user_too_early": false,
    "skipped_local_recovery": false,
    "fake_proof_attempted": false,
    "repeated_same_tactic": false,
    "ignored_repo_architecture": false,
    "contract_changed_after_code": false
  }
}
```

The JSON exists for search and pattern detection. The markdown exists for human reading. Do not expand either into a transcript.

## Anti-Gaming Review

`PROOF.md` must name fake or incomplete implementations that could otherwise pass. Each fake
pass risk should map to a concrete proof step. If the proof cannot catch a plausible fake,
strengthen the proof before implementation starts.

## Proof Scope

Every non-trivial `PROOF.md` should include a `Proof Scope` section:

```text
Proves: exact behavior, state transition, side effect, or invariant the proof observes.
Does not prove: important live, scale, timing, concurrency, provider, UI, or edge-case paths outside this proof.
False-green risks: how a shallow, proxy, mocked, stale, or incomplete implementation could still pass.
Evidence strength: deterministic, probabilistic, live gap, or manual gap.
```

The proof scope is not a loophole for weak proof. It is the contract that lets the evaluator judge whether the proof is strong enough for the behavior being claimed. When proof passes but the proof scope is visibly too narrow, treat the result as green but weak: return to proof repair before marking done, even if no user-visible break has been observed yet.

Serious evidence validation rejects missing proof-scope headings and placeholder proof-scope content. The required headings are `Proves:`, `Does not prove:`, `False-green risks:`, and `Evidence strength:`. The run evidence file is still named `oracle-scope.md` so old bundles and scripts remain stable.

## Proof Change Guard

After implementation begins, treat `FEATURE.md`, `PROOF.md`, and proof artifacts as one active contract revision. If that revision is wrong:

1. Stop implementation.
2. Enter an explicit contract-repair state.
3. Record why the old proof was wrong.
4. Add the new failing proof or evidence requirement.
5. Demonstrate that the strengthened proof fails against the current implementation when practical.
6. Resume implementation against the new revision.
7. Capture final evidence whose contract, proof runner, and declared source identities match that revision.

The guard prevents retrofitting proof to already-written code. It is evaluated from recorded revision reasoning, red evidence, and final artifact identity, not from whether contract and implementation files appear in one diff.
