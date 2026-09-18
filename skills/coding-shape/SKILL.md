---
name: coding-shape
description: Understand new or changed behavior, start the user-requested default Goal, and shape consequential product decisions into a specification with independent acceptance proof.
---

# Shape

Turn the requested outcome into decision-complete behavior and independent acceptance before implementation. Routing and announcements belong to [AGENTS.md](../../AGENTS.md).

## Start The Goal

The user's standing explicit request authorizes a native Goal by default on entering Shape; do not ask again. Reuse a matching Goal or create one through the available tool. Scope it to the requested deliverable: a build covers discovery through verification and final review; specification-only work ends at the specification and never grants build permission.

Set a numeric budget only if explicitly provided. Never replace an unrelated unfinished Goal, reset/extend limits, or create substitute persistence loops. Preserve other ownership and continue independent authorized work; surface an actual conflict. If Goal tools are unavailable, continue ordinary authorized execution and report the limitation once when relevant. Honor explicit Goal overrides, actual tool authority, interruptions, and runtime limits; stopped is not complete.

## Discover And Decide

Inspect the request, supplied references/PR, current implementation/contracts, and relevant repository context. Understand the relevant end-to-end journey: actors, triggers, outcomes, saved state, defaults/overrides, permissions, important empty/failure/unavailable states, existing data, compatibility, and affected consumers. These are investigation lenses, not a questionnaire. State the practical outcome you infer and propose a direction grounded in what you find. Current implementation explains what happens, not necessarily what should happen. Challenge the obvious patch: in which ordinary starting state would it still leave the user’s problem unsolved?

Resolve discoverable facts and routine technical choices yourself. Preserve behavior outside the request; do not announce preserved permissions and then ask to reconfirm them without a conflict. Ask about remaining consequential product choices using concrete scenarios, practical tradeoffs, and a recommended direction when supported. Use focused rounds as needed; no one-question cap, but no questions already answered by code or references. A clear request may need none. Disclose consequential assumptions; resolve material choices before freezing acceptance. Continue independent investigation while answers are pending.

For defaulting or automation, trace first use and missing configuration through to a usable result. Check relevant eligibility/capabilities, unavailable or invalid defaults, timing, saved overrides, repeated actions, and existing records. Select cases from the actual journey. Copying a default that may be empty does not establish automatic selection. Investigate fallback policy; do not silently choose an arbitrary, paid, destructive, or permission-expanding alternative. When policy remains open, ask a concrete scenario question with its consequence and an evidence-supported recommendation. Keep adjacent enhancements optional.

Keep one package per independently valuable outcome with runnable proof. Include accepted prerequisites, constraints/non-goals, and existing behavior to preserve; do not split by file count. Material refactors specify invariants or equivalence.

## Specify And Prepare Proof

Write `FEATURE.md` with accepted outcomes, journeys, decisions, boundaries, and compatibility notes, including the consequential cases uncovered during discovery. Before freezing, compare the proposed scenarios with the original practical outcome; resolve gaps rather than narrow the promise to the easiest implementation. Use [status mechanics](../../docs/harness/coding/status.md) to scaffold/register `draft`; migrate an old index safely without asking permission.

Delegate `PROOF.md`, dedicated acceptance, and executable `proof/run.sh` to a separate author using the specification, relevant original dialogue/corrections, repository context, and named consumption target. The [proof contract](../../docs/harness/coding/proof.md) owns authorship, realism, input freezing, and repair. Missing decisions return here; unavailable independent authorship cannot be replaced by the implementer.

Keep `draft` until the contract is decision-complete and independent proof is runnable. Record author/input versions, then mark `ready`. Human document sign-off is optional. A specification-only request stops at its requested deliverable, completing its Goal when satisfied. An authorized build continues in the same task through [coding-ship](../coding-ship/SKILL.md), carrying the matching Goal without renewed approval.

Later behavior changes normally start a new cycle after completion; honor explicit interruption and retain prior contracts/evidence. During implementation, a consequential acceptance decision pauses dependent work, then the separate author revises proof after user agreement. Independent setup repair follows the proof contract without reopening discovery.
