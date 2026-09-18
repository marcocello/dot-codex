# Four lifecycle skills

## Accepted outcome

Replace the discoverable `coding-workflow` skill with four normally discoverable skills: `coding-shape`, `coding-ship`, `coding-fix`, and `coding-operate`. Do not create `coding-analyze`. Analysis is inherent in domain work; architecture assessments, anti-pattern reviews, and workflow reviews remain directly invocable specialist skills. Ordinary explanation requests use the relevant domain expertise and end at the requested analytical deliverable.

## Journeys and boundaries

- New or unresolved behavior enters Shape; an authorized, specified feature with independent executable proof proceeds to Ship in the same task.
- A known defect or small maintenance enters Fix; preserve standalone versus reopened-feature obligations and active-Ship regression handling.
- An observed running-system symptom enters Operate even when worded as analysis or diagnosis only. Preserve read-only diagnosis scope and runtime read-back requirements.
- A code explanation, anti-pattern review, architecture assessment, or workflow review routes directly to relevant expertise without a general analysis skill or mandatory lifecycle package.
- Keep a concise routing table in AGENTS.md. Four skill entrypoints own their mode procedures; common domain selection, proof, status, evidence, research, steering, and completion rules have one maintained shared documentation home under docs/harness and are read only when relevant.
- Update the desired inventory using skill_inventory.py, replace old workflow discovery and UI metadata, and update current guidance and specialist links to the new owners. Retire the old skill directory after migrating all its useful current content and operational helpers.

## Compatibility to preserve

This is an organization and routing change. Preserve current proof independence, fixed acceptance, explicit Goal authorization, permission boundaries, feature status ownership, proportional regressions, final-review requirements, operational diagnostics, evidence capture, domain-skill selection, and existing user edits. Do not add new approvals or weaken existing ones. Preserve automatic discovery for the four skills. Preserve historical feature contracts, proof inputs, results, reviews, and unrelated work; historical references may remain as history and need not be rewritten to pretend the new structure existed previously.

## Consumption target and verification

The target is this checkout's local skill inventory, four skill entrypoints and their reachable guidance, AGENTS routing, and current specialist/document links. Verify actual inventory discovery and link resolution, plus realistic routing and scope cases reviewed independently against the new instructions. Report the distinction between on-disk readiness and discovery in a fresh app task. Global application refresh, deployment, commits, changes to unrelated inventory members, and re-proving historical features are outside scope.

## Decisions and source

Native task 01a0af8c-7363-7390-8e1f-a0d60b3d0d0e: the user proposed splitting the workflow; discussion rejected a generic coding-analyze as redundant; the user said “proceed” to the four-skill recommendation. Original conversation remains in native task history. Shared docs are documentation, not a fifth router skill. No Goal or token budget has been authorized in this task.
