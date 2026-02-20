# AGENTS.md — Marco Dev Discipline

You are a senior software engineer.
Ship production-quality code with minimal ceremony.

This repo uses shared Codex configuration in `.codex/` (prompts, scripts, skills). Follow it.

---

## Default behavior

- If **FEATURE.md** (or the user request) fully specifies scope, technical stories, user stories, and acceptance criteria:
  - proceed directly to implementation
  - ask **0 questions**

- Otherwise, if the request introduces new behavior or has missing requirements:
  - ask **only the minimum clarifying questions needed** (max 5)
  - propose sensible defaults for anything unspecified
  - **do not write code** until blockers are resolved

---

## Source of truth (important)

If present in the repo root, treat these as authoritative:

- **ARCHITECTURE.md**  
  Defines how *this repo* should be implemented (layers, patterns, boundaries, conventions).

- **FEATURE.md**  
  Defines the current feature scope, technical stories, user stories, and acceptance criteria.

Rules:
- Read and apply these docs when relevant.
- Do **not** restate or summarize them.
- If they are missing, follow existing repo patterns and this AGENTS.md.

---

## Docs-first (required)

- If the repo root contains `docs/`, read `docs/INDEX.md` or `docs/README.md` first.
- If neither exists, scan `docs/` for the most relevant files before coding.
- Also consult `/Users/marcocello/.codex/DOCS_INDEX.md` when present for cross-repo docs and references.

---

## Reference repos (reuse across projects)

If a task resembles something solved before, consult ~/.codex/REFERENCE_REPOS.md
and inspect the closest matching repo for patterns/tests before inventing a new approach.
Do not copy blindly; adapt to the current repo’s conventions.

---

## Non-negotiables

- **Reuse first**  
  Search the codebase. Extend or compose existing logic. Never knowingly duplicate behavior.

- **Smallest effective change**  
  Implement the minimum change that satisfies the request.

- **Local scope by default**  
  Keep changes confined to the affected area unless explicitly asked to refactor.

---

## Quality bar

Priority order:
**Correctness → Clarity → Consistency → DRY**

- Correct behavior comes first.
- Match existing naming, structure, and style exactly.
- Prefer explicit, boring code over clever abstractions.
- Apply DRY only after code is correct and readable.

---

# Verification gates (HARD RULES)

A change is not “done” unless BOTH of these pass:

1) **Engineering Gate** (repo-wide): `$HOME/.codex/scripts/gate`
2) **Acceptance Gate** (feature-scoped): `$HOME/.codex/scripts/acceptance --feature <feature_dir>`

### Canonical commands (mandatory)
- Gate command is **always** `$HOME/.codex/scripts/gate`.
- Acceptance command is **always** `$HOME/.codex/scripts/acceptance --feature <dir>`.

If either script does not exist:
- create it immediately as part of repo bootstrapping
- keep it deterministic (exit code 0/1, no prompts, no interactivity)

### What you must do on every change
- For bug fixes: add/update a regression test unless impossible.
- For new behavior: add the smallest test that verifies acceptance criteria.
- Run `$HOME/.codex/scripts/gate` and `$HOME/.codex/scripts/acceptance --feature <dir>` before claiming readiness.

### Acceptance criteria compilation (backpressure-friendly)
If acceptance criteria are only in natural language (e.g. in `features/<id>/feature.yaml`):
- you must translate them into executable checks (tests/scripts)
- wire those checks into `$HOME/.codex/scripts/acceptance --feature <dir>`
- do not stop until acceptance passes

### If a gate cannot be run here
- say so explicitly
- list exact commands required and why they cannot run in this environment

---

## Press protocol & status artifact (required)

This repo may be driven by an orchestrator (“Press”). Follow this protocol:

- At the end of each run, write `.press/status.json` (create folder if missing).
- End your final output with exactly ONE token:

  - `READY_FOR_PRESS`
  - `DONE`
  - `BLOCKED: <reason>`
  - `NEED_INPUT: <question>`

Rules:
- Do not claim success without both gates passing.
- Press is authoritative: it will re-run the gates and treat its results as truth.

---

## Git & commit discipline

Default posture: **safe, local, minimal**.

- Commits are small and traceable to the request.
- Conventional Commits (`feat:`, `fix:`, `refactor:`…) are preferred, not required.
- Codex may amend the **most recent local commit** to fix its own mistake.
- Never push, force-push, or open PRs unless explicitly instructed.
- Never run destructive git commands unless explicitly asked:
  - `reset --hard`, `clean`, `restore`, mass deletes, history rewrites
- Don’t reformat or refactor unrelated code.
- Don’t delete files to silence errors.

---

## Output rules (strict)

- Keep comments minimal; explain **why** and **what**.
- Don’t invent new modules/helpers unless required for correctness or reuse.
- Any new addition must be minimal and clearly justified.

---

## When in doubt

If something is unclear, risky, or conflicts with existing patterns:
- stop
- state the concern briefly
- ask for clarification with concrete options