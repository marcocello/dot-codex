---
name: coding-repair
description: "Repair a clear defect or failing proof, gate, test, typecheck, lint, build, or evaluator result with the smallest verified change."
metadata:
  short-description: Disciplined issue and failing-check repair workflow
---

# Repair

Purpose: smallest correct fix, verified.

## Default
- Clear issue/failing check: proceed.
- Unclear expected behavior: ask before coding.
- Inherit the assurance lane selected under `AGENTS.md`; finding one matching `FEATURE_DIR` promotes the repair to `tracked`.

## Fast path for concrete failures
- For a specific proof, gate, typecheck, lint, build, or evaluator failure: reproduce,
  patch smallest owning path, rerun failing check, then lifecycle checks from `AGENTS.md`.
- Use the diagnostic workflow below only when behavior, root cause, or owner is unclear.

## Workflow
1. Read context
   - Read `docs/INDEX.md` or `docs/README.md` if present.
   - Otherwise scan relevant `docs/`.

2. Route through feature proof when possible
   - Before fixing, inspect `docs/features/*/FEATURE.md` for one clear matching feature
     unless user supplied `FEATURE_DIR`.
   - If exactly one feature matches, treat that `FEATURE_DIR` as in scope; read
     `FEATURE.md` and `PROOF.md`; run existing primary proof when practical.
   - If proof misses the bug, extend that feature proof package with a focused failing regression before implementation.
   - Use `coding-proof-author` when matching `PROOF.md` is missing, vague, stale, or cannot
     host the regression cleanly.
   - Multiple material matches: ask.
   - If no feature clearly matches, do not create `FEATURE.md` by default; create smallest
     local regression test/proof near affected code.
   - Create/update `FEATURE.md` and `PROOF.md` only when expected behavior itself needs
     durable definition or product behavior changes.

3. Reproduce/root cause
   - Quote exact errors/failing tests when available.
   - Follow the real call path before deciding the fix: entrypoint, parsing, routing,
     owner module, persistence, network, runtime boundary.
   - Missing credentials, secrets, tokens, provider setup, deployment mounts, or required
     configuration are root-cause configuration failures; do not convert them into
     success, skipped, fallback, or no-op behavior unless the feature contract explicitly
     defines that state as optional.
   - Identify the root cause and state confidence: `clear`, `likely`, `unknown`.
   - Unknown root cause: add smallest diagnostic/repro before production edit.
   - Prefer current source, executable proof, runtime evidence.

4. Runtime evidence
   - Reproducible local issue: check app/runtime logs before code.
   - Docker: bounded recent logs.
   - Running dev/test server: inspect terminal output.
   - Browser issue: use Browser/in-app browser when available; inspect console/network.
   - Capture relevant lines only. Redact secrets.

5. Locate existing logic
   - Search existing functions/components.
   - Reuse/extend; avoid duplicate logic.
   - Read adjacent tests and ownership-boundary code.

6. Red
   - Add/update smallest regression.
   - If `FEATURE_DIR` in scope, ensure `PROOF.md` covers regression or use
     `coding-proof-author`.
   - Run narrow command; confirm failure.

7. Green
   - Local fix only.
   - Avoid refactor unless required for correctness.
   - No unrelated code.
   - Do not hide required-runtime failures by catching and downgrading them. Fix the
     missing credential/configuration supply path, fail fast with a clearer diagnostic,
     or report the exact user-owned requirement.
   - Semantic/domain behavior: do not repair by adding ad hoc natural-language keyword lists,
     phrase gates, or tool hiding. Put invariant at owning boundary: parser schema, service
     validation, tool contract, persistence check, provider read-back, postcondition.
   - Rerun same test; confirm pass.

8. Verify/finalize
   - Add verification appropriate to touched surface.
   - Re-check logs/browser signals that exposed issue.
   - Run relevant checks or list exact unrun commands.
   - `lightweight`: require the focused regression or narrow check; do not require the evaluator or full repo gate unless the touched surface makes them relevant.
   - `tracked` or `autonomous`: require the primary proof, gate, and `coding-feature-evaluator` before completion.
   - Evaluator `FAIL`: repair input. Evaluator `NEED_INPUT`: exact user-owned input after
     recovery.
   - If a Codex Goal is active, keep it open until regression, broader check, and evaluator
     `PASS` prove completion.
   - If `FEATURE_DIR` in scope, run primary proof command from `PROOF.md`.
   - Do not commit/push/open PR/update changelog/close issues unless explicitly asked.

9. Escalate
   - If regression/narrow/broader check still fails after first focused fix, follow
     autonomous escalation policy in `AGENTS.md`.
   - During explicit autonomous execution, continue through `coding-autonomous-execute`
     while proof remains unsatisfied instead of returning terminal failure.

## Rules
- Reproduce or name missing evidence before editing.
- Root cause first.
- Local evidence before local app fixes.
- No speculative cleanup.
- Invariant first; examples are not behavior source of truth unless lexical search.
- Surgical change only.
- Connect fix to regression/proof.
- Follow autonomous escalation policy in `AGENTS.md`; no scope broadening, no orchestrator.

## Output
- Report using the `AGENTS.md` short receipt format for completed feature or issue work.
- Outcome, changed surface, verification, blockers.
- Include relevant Docker/runtime/browser evidence, or why not applicable.
