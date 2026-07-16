---
name: coding-app-improvement-review
description: "Review feature contracts, evidence, evaluator results, and user corrections to suggest project improvements, proof hardening, or reusable harness lessons without applying changes."
---

# App Improvement Review

Purpose: read existing feature/proof/evidence history and produce suggestions only. Do not edit project code, proof contracts, queue status, or harness policy unless the user explicitly asks for implementation. Use the review for both project improvement and dot-codex harness improvement, but keep those lessons separated.

## Inputs

- Target repo or current checkout.
- Optional scope: one `FEATURE_DIR`, all `docs/features`, recent proof runs, or one suspected weak area.
- Optional conversation context: current chat, pasted transcript, rollout summary, or a short user-provided correction history.

## Review

1. Load current repo context: `AGENTS.md`, `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when present.
2. Inspect feature contracts: `docs/features/*/FEATURE.md`; check behavior is the source of truth, observable, realistic, and detailed enough. Ask the user only when product intent is genuinely missing.
3. Inspect proof contracts: `PROOF.md` and proof artifacts; verify public or real boundary coverage, DB/API/provider/UI/read-back evidence, proof scope, anti-gaming pressure, and no fake/source-only checks for user-visible behavior.
4. Inspect evidence: latest `proof/runs`, `result.json`, `command.txt`, `stdout.txt`, `stderr.txt`, `oracle-scope.md`, `agent-observation.md`, `agent-observation.json`, notes, screenshots, logs, and provider read-back when present. Treat missing evidence as a suggestion, not a verdict.
5. Inspect successful tests, gates, and evaluator output; ask whether success proves the actual behavior or only a proxy.
6. Inspect user corrections and repeated repair attempts from available conversation context, proof notes, commit history, and run evidence. Identify whether the agent misunderstood intent, overrode user constraints, changed strategy repeatedly, or proved the wrong thing. If no conversation context is available, say that explicitly instead of inferring it from source alone.
7. Generate suggestions, grouped by owner:
   - project feature suggestion;
   - spec clarification;
   - proof hardening;
   - implementation/design logic;
   - readiness/diagnostic;
   - harness lesson.
8. Classify each material lesson before suggesting a destination:
   - `project-specific`: behavior, architecture, style, setup, or proof detail owned by the target repo.
   - `proof-specific`: a concrete `FEATURE_DIR/PROOF.md`, proof runner, fixture, or evidence bundle needs repair.
   - `harness-level`: repeated cross-project or cross-feature evidence shows a dot-codex skill, doc, script, test, evaluator fixture, or `AGENTS.md` rule allowed the failure.
   - `personal-preference`: stable user preference; suggest memory only when the user explicitly asks to preserve it.
   - `no-reusable-lesson`: one-off failure that should stay local.
9. Promote a harness lesson only when repeated evidence across features, runs, or repos shows a harness instruction, skill, doc, script, or test allowed the same failure.
10. When suggesting a harness lesson, name the reusable observation signal: weak proof scope, skipped recovery, fake proof, repeated same tactic, ignored architecture, contract drift, missing readiness, or evaluator overreach.

## Accepted Learning Placement

During review, suggest the destination for accepted learning but do not write it unless the user asks for implementation.

- Project-specific behavior, architecture, or style rule: target repo `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, or `docs/TESTING.md`.
- Proof or evidence pattern: target repo `docs/TESTING.md`, feature proof template, or the relevant `FEATURE_DIR/PROOF.md` when a concrete feature owns it.
- New product capability: `docs/features/status.json` queue item or a new `FEATURE.md`/`PROOF.md` pair only after the user accepts the suggestion.
- Repeated cross-project harness lesson: dot-codex skill, harness doc, evaluator fixture, or narrow script/test.
- Stable personal preference: memory only when the user explicitly asks to preserve it.

## Output

```text
App improvement review: PASS|SUGGESTIONS|NEED_INPUT
Scope: <repo/feature dirs/evidence inspected>
Strong signals:
- <what is already sound>
Conversation signals:
- <none|material|unavailable> - user corrections: <short count/summary> - rejected approaches: <short list> - final understood intent: <one sentence> - review impact: <how this changes suggestions>
Suggestions:
- [app|spec|proof|logic|readiness|harness] <specific change> - classification: <project-specific|proof-specific|harness-level|personal-preference|no-reusable-lesson> - evidence: <file/run/check>
Missing evidence:
- <only material gaps>
Harness lessons:
- <candidate dot-codex rule/skill/doc/script/test/evaluator-fixture change, or none>
Project-specific lessons:
- <target-repo behavior/doc/proof/test/readiness change, or none>
Accepted learning placement:
- <where an accepted suggestion should live, or none>
Next action:
- <one concrete action>
```

## Rules

- Suggest only; do not auto-apply.
- Current source beats memory.
- Conversation context is evidence for intent drift and correction handling; current source remains the authority for what was actually implemented.
- Successful tests are evidence only if the proof check matches the behavior.
- Prefer fewer high-confidence suggestions over broad roadmaps.
- Do not create a new feature by default; suggest one when evidence shows real product value or repeated pain.
- Do not turn one repo-specific issue into harness policy without recurrence.
