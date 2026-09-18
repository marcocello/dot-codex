# Shared Feature Status Mechanics

Read when Shape registers, Ship claims/completes, or Fix reopens a material feature. `feature_status.py` owns normal mutations; its `--help` lists arguments. This reference supplies shared schema, migration, and ownership semantics.

## Schema

Adopted repositories require version-2 `docs/features/status.json`; the gate uses `--require-feature-status` (automatic for this harness). A feature entry has exactly `id`, `feature_dir`, `priority`, `status`, `owner`, `proof_run`, `notes`, inside `{"version": 2, "features": [...]}`. IDs/directories/priorities are unique; paths are safe repository-relative. Use a stable task id (unique task token if unavailable) as owner, nonempty only while active. Notes are concise lifecycle context, not a task list or evidence store.

Every persisted entry owns FEATURE, PROOF and executable `proof/run.sh`. `done` points to the latest official run physically under its own `proof/runs/`, with `result.json` PASS; foreign, symlinked, missing, malformed, stale, failed, or newer-incomplete evidence cannot qualify. Explicit regression-kind results never qualify; historical proof-only results may omit kind. Other states have null proof pointers; retain prior files.

## Mutation And Ownership

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/feature_status.py" --root REPO --id FEATURE --owner TASK --from new --to draft
"${CODEX_HOME:-$HOME/.codex}/scripts/feature_status.py" --root REPO --id FEATURE --owner TASK --from ready --to active
"${CODEX_HOME:-$HOME/.codex}/scripts/feature_status.py" --root REPO --id FEATURE --owner TASK --from active --to done --proof-run docs/features/FEATURE/proof/runs/RUN
```

Normal states: draft (decisions/proof incomplete), ready (decision-complete runnable independent proof), active (owned work), blocked (necessary unresolved dependency), done (owning skill's proof/review completion satisfied). Reopen done->active for a contract defect or done->draft for accepted behavior changes, retaining history. Active work can return to draft/blocked or ready on explicit preemption; only the user can authorize acceptance changes. Independent setup repair stays active.

The helper locks, validates shared identities/ownership plus the target package, and atomically writes without displacing other entries. Register only after scaffolding; new priority is allocated under lock. Reread/retry lock contention, never bypass rejection with manual writes. Unrelated packages' defects do not authorize repair or takeover.

One owner per active feature and one active feature per task. Select explicit/current-task work first, then the task's resumable claim; global lowest ready priority applies only to requested queue continuation. Coordinate overlapping files/runtime writes; stabilize only relevant verification inputs. Optional worktrees require reconciliation on integration. No automatic takeover/lease exists: user-authorized handoff confirms the prior task stopped, releases its claim active->ready with its recorded owner, then the receiver claims it. Owner tokens coordinate; they are not authentication.

Feature state and Goal state are distinct. Interruption/exhaustion is unfinished, never done or automatically a native blocked state. Apply native tool criteria independently. A completion pointer write after final review needs the gate, not new proof solely for metadata.

## Automatic Migration

If absent, initialize the empty v2 index. If older/unversioned, archive its exact original under `docs/harness/migrations/`, then use a one-off conversion under the helper's same sidecar lock: reread, validate identities/priorities/ownership, and atomically replace. Never replace existing data with an empty index. Preserve identities, relative priorities, owners, contracts, and evidence. Preserve done only with valid current proof; otherwise blocked with a reason and null pointer. Add only missing historical scaffold explicitly marked incomplete with a failing runner; do not rebuild/re-prove history. Corruption or conflicting ownership needs resolution, not invented values.

Migration is authorized local setup, not another approval/Goal question. After conversion, return to the helper for registration/transitions; do not add compatibility readers.
