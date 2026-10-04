# Shared Feature Status Mechanics

Read when Design Specs and Proof registers, Implement claims/completes, or Repair reopens a material feature. `feature_status.py` owns normal mutations; its `--help` lists arguments. This reference supplies shared schema, migration, and ownership semantics.

## Schema

Adopted repositories require version-2 `docs/features/status.json`; the gate uses `--require-feature-status` (automatic for this harness). A feature entry has exactly `id`, `feature_dir`, `priority`, `status`, `owner`, `proof_run`, `notes`, inside `{"version": 2, "features": [...]}`. IDs/directories/priorities are unique; paths are safe repository-relative. Use a stable task id (unique task token if unavailable) as owner, nonempty only while active. Notes are concise lifecycle context, not a task list or evidence store.

Every persisted entry owns a nonempty FEATURE. Draft and blocked entries may lack runnable coverage while decisions or prerequisites remain open. Ready/active/implemented packages require either a valid `COVERAGE.json` mapping to shared executable checks or the legacy nonempty PROOF and executable `proof/run.sh`. Structure does not establish semantic readiness, mapping completeness, or independent authorship. See [rounds](rounds.md).

`implemented` means saved implementation awaiting verification; it has null owner and proof pointer. `done` records historical verified completion. Its existing `proof_run` field points either to the newest owning `proof/runs/<run>` with PASS evidence and standalone review, or to `docs/verification/rounds/<id>/review.json` covering that feature. Other states have null pointers; retain old evidence. The name `proof_run` is retained for schema compatibility.

Every new transition to done requires current target-valid evidence and matching PASS review attribution. Standalone completion validates its current captured inputs; round completion checks mapped coverage, every required package, supporting evidence, and their determining inputs. Inventory reads prefer the portable `completion.json` written automatically after successful validation; older records fall back to retained runs. History remains valid without raw local logs, but new completion always validates those logs and current inputs. Use `verification_receipt.py check-round --root REPO --round-review PATH` to check a round's current validity. Reopened work requires fresh or still-current relevant evidence under the same completion rules.

Readiness also depends on [product discovery and autonomy](../../../skills/coding-product-partner/SKILL.md#discovery-and-autonomy): the agent checks that the outcome and authority are clear, consequential user-owned decisions are resolved, and remaining assumptions are justified. A `ready` label cannot establish these facts; a fixed question-and-answer round is not a prerequisite.

## Mutation And Ownership

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/feature_status.py" --root REPO --id FEATURE --owner TASK --from new --to draft
"${CODEX_HOME:-$HOME/.codex}/scripts/feature_status.py" --root REPO --id FEATURE --owner TASK --from ready --to active
"${CODEX_HOME:-$HOME/.codex}/scripts/feature_status.py" --root REPO --id FEATURE --owner TASK --from active --to implemented
"${CODEX_HOME:-$HOME/.codex}/scripts/feature_status.py" --root REPO --id FEATURE --owner TASK --from implemented --to done --round-review docs/verification/rounds/ROUND/review.json
# Existing standalone completion remains supported:
"${CODEX_HOME:-$HOME/.codex}/scripts/feature_status.py" --root REPO --id FEATURE --owner TASK --from active --to done --proof-run docs/features/FEATURE/proof/runs/RUN
```

Normal states: draft (decisions/coverage incomplete), ready (decision-complete executable coverage), active (owned work), implemented (implementation finished, verification pending), blocked (necessary unresolved dependency), done (recorded verified completion). Move active->implemented to release the claim and continue another feature in the round. Implemented may move to active, done, blocked or draft. Reopen done->active for a contract defect or done->draft for accepted behavior changes, retaining history. Active work can return to draft/blocked or ready on explicit preemption; only the user can authorize acceptance changes. Setup repair stays active.

The helper locks, validates shared identities/ownership plus the target package, and atomically writes without displacing other entries. Register a draft when its FEATURE is worth retaining; no placeholder proof files are needed. New priority is allocated under lock. Reread/retry lock contention, never bypass rejection with manual writes. Unrelated packages' defects do not authorize repair or takeover.

One owner per active feature and one active feature per task. Select explicit/current-task work first, then the task's resumable claim; global lowest ready priority applies only to requested queue continuation. Coordinate overlapping files/runtime writes; stabilize only relevant verification inputs. Optional worktrees require reconciliation on integration. No automatic takeover/lease exists: user-authorized handoff confirms the prior task stopped, releases its claim active->ready with its recorded owner, then the receiver claims it. Owner tokens coordinate; they are not authentication. After `implemented` releases a claim, `--owner` on completion identifies the actual implementer attributed by the reviewed evidence, which may differ from the coordinator recording it. The reviewer establishes that attribution from task history; no prior-owner lock or authentication is implied.

Feature state and Goal state are distinct. Interruption/exhaustion is unfinished, never done or automatically a native blocked state. Apply native tool criteria independently. A completion pointer write after final review needs the gate, not new proof solely for metadata.

## Automatic Migration

If absent, initialize the empty v2 index. If older/unversioned, archive its exact original under `docs/harness/migrations/`, then use a one-off conversion under the helper's same sidecar lock: reread, validate identities/priorities/ownership, and atomically replace. Never replace existing data with an empty index. Preserve identities, relative priorities, owners, contracts, and evidence. Preserve done with structurally valid retained historical proof; otherwise blocked with a reason and null pointer. Mark missing historical context incomplete without fabricating proof; do not rebuild/re-prove history. Corruption or conflicting ownership needs resolution, not invented values.

Migration is authorized local setup, not another approval/Goal question. After conversion, return to the helper for registration/transitions; do not add compatibility readers.
