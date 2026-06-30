---
name: coding-project-improvement-review
description: "Review a target project's feature specs, proof plans, proof evidence, successful tests, evaluator results, and user corrections to suggest project-specific improvements, new features, proof hardening, and reusable harness lessons without applying changes. Use when Codex should manually analyze whether features, proofs, and successful checks make sense and produce suggestions for the project or for dot-codex harness evolution."
---

# Project Improvement Review

Purpose: read existing feature/proof/evidence history and produce suggestions only. Do not edit project code, proof contracts, queue status, or harness policy unless the user explicitly asks for implementation.

## Inputs

- Target repo or current checkout.
- Optional scope: one `FEATURE_DIR`, all `docs/features`, recent proof runs, or one suspected weak area.

## Review

1. Load current repo context: `AGENTS.md`, `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when present.
2. Inspect feature contracts: `docs/features/*/FEATURE.md`; check behavior is the source of truth, observable, realistic, and detailed enough. Ask the user only when product intent is genuinely missing.
3. Inspect proof contracts: `PROOF.md` and proof artifacts; verify public or real boundary coverage, DB/API/provider/UI/read-back evidence, proof scope, anti-gaming pressure, and no fake/source-only checks for user-visible behavior.
4. Inspect evidence: latest `proof/runs`, `result.json`, `command.txt`, `stdout.txt`, `stderr.txt`, `oracle-scope.md`, `agent-observation.md`, `agent-observation.json`, notes, screenshots, logs, and provider read-back when present. Treat missing evidence as a suggestion, not a verdict.
5. Inspect successful tests, gates, and evaluator output; ask whether success proves the actual behavior or only a proxy.
6. Inspect user corrections and repeated repair attempts; these are often stronger signals than green local checks.
7. Generate suggestions, grouped by owner:
   - project feature suggestion;
   - spec clarification;
   - proof hardening;
   - implementation/design logic;
   - readiness/diagnostic;
   - harness lesson.
8. Promote a harness lesson only when repeated evidence across features, runs, or repos shows a harness instruction, skill, doc, script, or test allowed the same failure.
9. When suggesting a harness lesson, name the reusable observation signal: weak proof scope, skipped recovery, fake proof, repeated same tactic, ignored architecture, contract drift, missing readiness, or evaluator overreach.

## Accepted Learning Placement

During review, suggest the destination for accepted learning but do not write it unless the user asks for implementation.

- Project-specific behavior, architecture, or style rule: target repo `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, or `docs/TESTING.md`.
- Proof or evidence pattern: target repo `docs/TESTING.md`, feature proof template, or the relevant `FEATURE_DIR/PROOF.md` when a concrete feature owns it.
- New product capability: `docs/features/status.json` queue item or a new `FEATURE.md`/`PROOF.md` pair only after the user accepts the suggestion.
- Repeated cross-project harness lesson: dot-codex skill, harness doc, evaluator fixture, or narrow script/test.
- Stable personal preference: memory only when the user explicitly asks to preserve it.

## Output

```text
Project improvement review: PASS|SUGGESTIONS|NEED_INPUT
Scope: <repo/feature dirs/evidence inspected>
Strong signals:
- <what is already sound>
Suggestions:
- [project|spec|proof|logic|readiness|harness] <specific change> - evidence: <file/run/check>
Missing evidence:
- <only material gaps>
Harness lessons:
- <candidate rule/skill/doc/script/test change, or none>
Accepted learning placement:
- <where an accepted suggestion should live, or none>
Next action:
- <one concrete action>
```

## Rules

- Suggest only; do not auto-apply.
- Current source beats memory.
- Successful tests are evidence only if the proof check matches the behavior.
- Prefer fewer high-confidence suggestions over broad roadmaps.
- Do not create a new feature by default; suggest one when evidence shows real product value or repeated pain.
- Do not turn one repo-specific issue into harness policy without recurrence.
