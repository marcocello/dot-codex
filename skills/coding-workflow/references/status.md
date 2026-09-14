# Status

`docs/features/status.json` is mandatory for every repository after this harness is adopted. Before registration or a transition, initialize the current schema if absent or automatically migrate an old-format index as described below. This local setup is explicitly authorized; do not ask whether to migrate or stop with `NEED_INPUT` merely because the format is old. Run the gate with `--require-feature-status` in adopted application repositories so deletion of the whole feature directory cannot bypass validation; the harness profile always enables this requirement.

## Schema

```json
{
  "version": 2,
  "features": [
    {
      "id": "short-feature-id",
      "feature_dir": "docs/features/short-feature-id",
      "priority": 1,
      "status": "draft",
      "owner": null,
      "proof_run": null,
      "notes": ""
    }
  ]
}
```

Only these seven entry fields are allowed. Paths are safe repository-relative paths. IDs, directories, and priorities are unique. `owner` is a stable task id (or unique task-local token when no id is exposed), nonempty only while active. `notes` contains concise lifecycle context. Normal operations accept only version 2; older formats must be converted once, not supported through compatibility aliases or fallback readers.

Every entry owns a complete `FEATURE.md`, `PROOF.md`, and executable `proof/run.sh` in every persisted state. Every `done` entry requires `proof_run` pointing to the newest official run directory physically inside that feature's `proof/runs/`, containing a valid `result.json` with `PASS`. Missing, foreign, failed, malformed, symlinked, or older evidence is rejected, including when the newer run is unfinished. There is no legacy exception. Non-done entries have a null pointer; old run files remain retained. New capture results identify `kind`; only `proof` qualifies for completion. Regression results under `tests/runs/` are supporting evidence and do not supersede official proof. Explicitly non-proof results are rejected even if relocated into `proof/runs/`; historical results from the original proof-only format may omit `kind`.

## Automatic Migration

Detect an older or unversioned index before calling `feature_status`. Use a one-off conversion script to archive the exact original under `docs/harness/migrations/`, map all entries to version 2, and atomically replace the index. Acquire the same sidecar lock used by `feature_status`, reread the source under that lock, and validate shared schema, identities, priorities, and ownership before replacement. An existing index must never be replaced with an empty one.

Preserve feature identities, relative priority, active ownership, and retained evidence. Resolve field mappings from the existing index and repository context; do not invent owners or passing results. Preserve `done` only with evidence meeting the current contract; otherwise use `blocked` with a concise explanation and null `proof_run`. Preserve existing contracts and runners. Where historical packages are incomplete, add only missing documents explicitly marked incomplete and a failing runner; do not reimplement or re-prove historical features during migration.

Then register or transition the requested feature through `feature_status` and continue the authorized work. Mention the completed migration briefly. An old format is not a blocker; corrupt data or conflicting active ownership still requires safe resolution rather than discarded records or another task's displacement. Conversion does not require Goal authorization and must not be bundled into a Goal permission question.

## States

- `draft`: material feature or proof decisions remain unresolved.
- `ready`: accepted behavior and executable proof are decision-complete.
- `active`: the accountable task owns unfinished Ship or package-owned Fix work; an interrupted or budget-limited native Goal can retain this claim while execution is stopped.
- `blocked`: safe local recovery is exhausted and one exact user-owned approval or external dependency remains; historical unsupported completion claims may be held here explicitly for evidence reconciliation, never silently treated as done.
- `done`: target-valid realistic proof, affected regression verification, fresh final reviewer `PASS`, and unchanged relevant inputs apply. Evidenced unrelated pre-existing test failures are reported separately.

Multiple entries may be active with distinct owners. Each task owns at most one active material feature. Standalone focused fixes do not need queue entries.

## Transitions

```text
draft -> ready
ready -> active
active -> done | blocked | draft
blocked -> ready | draft
done -> active            for a clear defect without contract change
done -> draft             for changed behavior or proof meaning
active -> ready           when a clearly replacing request preempts unchanged work
```

Use the shared command for entry creation and transitions, not a whole-file editor:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/feature_status" --root REPO --id FEATURE --owner TASK --from ready --to active
"${CODEX_HOME:-$HOME/.codex}/scripts/feature_status" --root REPO --id FEATURE --owner TASK --from active --to done --proof-run docs/features/FEATURE/proof/runs/RUN
```

After initialization or migration and scaffolding a feature, `--from new --to draft` registers it and allocates the next priority under lock. `--notes` optionally supplies lifecycle context. Under a persistent OS sidecar lock, the command checks expected state, shared schema/identity/priority/ownership constraints, and only the target feature's package and proof, then atomically replaces the file. Another feature's invalid proof, absent artifact, or local notes cannot block this update; its entry remains untouched. Full internal validation still reports all features' defects. Malformed shared identity or conflicting ownership remains a conflict. The lock covers only the short update, not implementation. A busy lock fails after five seconds; reread and retry. The one-time migration above is the only direct conversion; do not bypass normal transition or ownership rejection with manual overwrites.

A defect invalidating a delivered feature's claim reopens its owning entry before repair. Regressions introduced during another feature's active Ship run are repaired within that run rather than opening a package for every affected feature. An agreed change to accepted behavior starts a new cycle: retain previous specification/proof versions and evidence, move the owning feature to `draft`, and use Shape. During implementation, acceptance changes require the user's decision before that transition can authorize a revision. Align the independent proof and native Goal before resuming; a transition never authorizes silent proof changes.

An independent author's setup repair under [proof.md](proof.md#fixed-acceptance) preserves acceptance and stays in the current Ship claim and Goal; do not move it through `blocked` or `draft` merely to permit the repair. A pending user decision pauses only dependent work; retain the active claim while useful independent work continues, then use `blocked` if the task cannot progress. Native Goal blocking still follows its own runtime criteria.

After final reviewer `PASS`, the `active -> done` write is completion metadata, not a candidate change; validate it with the gate without another proof attempt merely for the pointer write. Native Goal state and feature state are distinct. Keep stopped work unfinished and preserve its task association; never map budget exhaustion to success or silently start a new allowance.

## Parallel Work And Handoff

Same-checkout parallel work is the default. Separate tasks claim different features without displacing each other. Identify affected files and shared runtime resources, inspect the other active work, and let independent areas proceed. For overlap, coordinate one writer for the shared area using existing task communication; if ownership cannot be resolved, pause only the conflicting edit and ask. Reread the shared area after a handoff. Do not reset, restart, migrate, or otherwise change a shared server/database another task is using without coordination and any required approval. Package-free fixes obey the same rules.

Before proof through final review, arrange stability only for the affected code, proof data, and runtime inputs. Compare relevant input identities before and after; unrelated edits do not invalidate proof. Relevant concurrent changes or uncertain stability require coordination and a fresh affected proof. Do not freeze the whole checkout or add a scheduling system. Worktrees remain optional if explicitly chosen; their status copies require reconciliation and affected proof at integration. This helper protects cooperating local status writers, not source edits, arbitrary editors, remote hosts, or runtime state.

No automatic takeover or timeout-based lease exists. For explicit handoff, confirm the previous task has stopped, preserve its work, and release its claim `active -> ready` using the recorded owner only with user-authorized transfer; the receiving task then claims with its own id. An owner token is a coordination guard, not authentication.

## Selection

1. Explicitly requested unclaimed feature, or this task's own claim.
2. Current-task-created or reopened feature.
3. This task's resumable active feature; a foreign active owner requires explicit handoff.
4. Global priority, meaning the lowest numeric priority among `ready` entries, only when the user explicitly requests queue continuation.

Within one task, additive work waits behind its active feature unless explicitly delegated. A replacing request moves only that task's unchanged package `active -> ready`, recording why, then claims the replacement. Other tasks remain free to progress their independent work.

`status.json` is not a task list. Do not add subtasks, checkboxes, percentages, phase counters, requirements, proof prose, reviewer findings, hashes, dependency graphs, or implementation plans.
