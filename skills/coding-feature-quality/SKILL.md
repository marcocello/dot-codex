---
name: coding-feature-quality
description: Review FEATURE_DIR/FEATURE.md before non-trivial implementation for ambiguity, edge cases, testability, and architecture conflicts without adding framework phases.
metadata:
  short-description: Lightweight feature contract quality review
---

# Feature Quality

Purpose: improve a feature contract before implementation while staying inside the existing single
FEATURE_DIR workflow.

## Workflow
1) Read the contract
   - Treat `FEATURE_DIR/FEATURE.md` as the behavior source of truth.
   - Read `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when present.

2) Scan for quality gaps
   - Ambiguity: unclear actors, terms, outcomes, constraints, or unresolved assumptions.
   - Edge cases: missing error, empty, boundary, permission, concurrency, and recovery cases.
   - Testability: behavior that cannot be checked through public boundaries or deterministic tests.
   - Architecture conflicts: behavior that violates authoritative repo architecture or layer rules.

3) Decide what to do
   - If gaps materially affect scope or correctness, update `FEATURE_DIR/FEATURE.md` before
     implementation or ask only the blocking question.
   - If gaps are minor, record the assumption directly in `FEATURE.md` and continue.
   - For larger brownfield changes, optionally create or update `FEATURE_DIR/change.md` with
     intent, non-goals, design notes, and a task checklist.

4) Keep the workflow lightweight
   - Do not create Spec Kit or OpenSpec command phases.
   - Do not create `.specify/`, `openspec/`, or another orchestration root.
   - Keep Gherkin scenarios in `FEATURE.md`.
   - Keep executable checks under `FEATURE_DIR/acceptance/`.

## Output
- Findings only when there are material gaps.
- Otherwise a concise statement that the feature contract is ready for implementation.

## Rules
- Stay within the single FEATURE_DIR workflow.
- `FEATURE.md` remains the authoritative behavior contract.
- Deterministic gate and acceptance scripts remain the completion authority.
