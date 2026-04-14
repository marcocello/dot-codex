## dot-codex

Minimal structure around Codex to make autonomous development predictable.

The human defines the target: a feature spec (`docs/features/<id>/FEATURE.md`), constraints, and what “done” means at a high level. When asked to generate acceptance coverage, Codex translates behavior described in `FEATURE.md` (including any Gherkin scenarios) into executable black-box tests under the feature folder. Those tests become the concrete definition of success.

Codex then implements the necessary code, updates tests as needed, runs commands, fixes failures, and iterates until all checks pass. Correctness is enforced by scripts, not by the model.

`AGENTS.md` defines how Codex operates inside a repository: which files are authoritative, how specs are interpreted, and how optional project architecture (`docs/ARCHITECTURE.md`) is applied if present.

Skills provide reusable architectural patterns (for example, `python-backend` or `frontend`). They enforce cross-project consistency without polluting individual repos.

Determinism comes from two scripts. These scripts decide success.
    `$HOME/.codex/scripts/gate` runs repo-wide checks such as linting, tests, and builds.
    `$HOME/.codex/scripts/acceptance --feature <dir>` runs feature-scoped black-box tests derived from `FEATURE.md`.

Workflow guidance in this repo is skill-driven. Validation is script-driven
(`scripts/gate`, `scripts/acceptance`, `scripts/ensure_venv`). No in-repo orchestrator is present.

Specs define intent. Acceptance tests define “done.” Architecture defines structure. Scripts define correctness. Codex produces code.

Repo-level context lives in lightweight docs:
- `docs/APP.md` for overall app or project context
- `docs/ARCHITECTURE.md` for authoritative architecture
- optional `docs/CONVENTIONS.md` and `docs/TESTING.md` for repo-level guidance

These docs help Codex reason better without turning the repo into a workflow engine.

## Operator Guide

### 1) What controls Codex behavior (in order)
1. `AGENTS.md` (repo rules): source of truth for workflow, TDD, quality bar, and required checks.
2. `config.toml` (runtime mode): model, sandbox, approvals, and default search mode.
3. `skills/*/SKILL.md` (task playbooks): specialized workflows for feature writing, fixing issues, backend/frontend, and architecture reviews.
4. `prompts/*.md` (phase prompts): templates for feature implementation, gate-fix, and acceptance-fix tasks.
5. `scripts/*` (deterministic validators): these decide pass/fail, not the model.

### 2) Runtime knobs (no profiles)
- Default: safe and reproducible
  - `sandbox_mode = "workspace-write"`
  - `web_search = "disabled"`
- Per-run overrides when needed:
  - live search: `codex --search "..."`
  - temporary sandbox override: `codex -s danger-full-access "..."`
  - temporary config override: `codex -c web_search=\"live\" "..."`

Example:
```bash
codex
codex --search "your prompt here"
```

### 3) Core tools used by this repo
- `scripts/ensure_venv`
  - Creates/repairs `.venv`, installs baseline Python tooling, validates required tools.
- `scripts/gate`
  - Runs repo-wide checks.
  - Python path: `ruff format --check`, `ruff check`, `mypy`, `pytest`.
  - Runs `pip-audit` only when dependency manifest files changed.
- `scripts/acceptance --feature <FEATURE_DIR>`
  - Runs feature-scoped acceptance checks.
  - Fails if `FEATURE.md` is missing.
  - Fails if acceptance harness is missing.
- `skills/feature-execute`
  - Drives feature delivery with red/green TDD and deterministic checks.
- `skills/acceptance-author`
  - Translates `FEATURE.md` behavior into executable acceptance tests.
- `skills/auto-improve`
  - Repairs failing gate or acceptance checks with bounded, minimal fixes.
- `skills/research`
  - Gathers external evidence with Context7 first and live web search only when the task needs it.

### 4) Skills currently available
- `feature-execute`: implement one feature end-to-end inside Codex App
- `acceptance-author`: generate or repair feature acceptance coverage from `FEATURE.md`
- `auto-improve`: repair failing gate or acceptance checks with bounded fixes
- `research`: gather external docs and evidence before committing to assumptions
- `app-to-features`: greenfield bootstrap that creates `docs/APP.md`, optional repo docs, and
  multiple feature specs before returning to normal single-feature work
- `feature`: create/update `docs/features/<id>/FEATURE.md`
- `fix-issue`: minimal corrective change with regression checks
- `python-backend`: backend layering + pytest discipline
- `frontend`: React/Next.js UI implementation discipline
- `architecture-deep-dive`: deep component architecture analysis
- `compare-architectures`: compare current architecture vs reference
- `maintainability-review`: codebase maintainability and function-quality audit

### 5) Standard workflow (day-to-day)
1. Optional greenfield bootstrap:
```bash
codex "Use the app-to-features skill for this app idea"
```
2. Define feature directory and spec:
```bash
mkdir -p docs/features/<feature-id>
$EDITOR docs/features/<feature-id>/FEATURE.md
```
3. Prepare toolchain:
```bash
./scripts/ensure_venv
```
4. Create or refine the feature spec in Codex:
```bash
codex "Use the feature skill for docs/features/<feature-id>"
```
5. If discovery needs external evidence, run a focused research pass:
```bash
codex --search "Use the research skill to gather evidence for docs/features/<feature-id>"
```
6. If acceptance is missing, add it explicitly:
```bash
codex "Use the acceptance-author skill for docs/features/<feature-id>"
```
7. Implement with Codex:
```bash
codex "Use the feature-execute skill for docs/features/<feature-id>"
```
8. Validate repo:
```bash
$HOME/.codex/scripts/gate
```
9. Validate feature:
```bash
$HOME/.codex/scripts/acceptance --feature docs/features/<feature-id>
```
10. If a check fails, run a focused fix pass:
```bash
codex "Use the auto-improve skill for docs/features/<feature-id>"
```

### 6) What “good” looks like
- Feature behavior is documented in `FEATURE.md` with clear Gherkin scenarios.
- Red/green evidence exists for the changed behavior.
- `gate` passes.
- feature `acceptance` passes.

# Acknowledgments

This structure builds on ideas from:
- The Ralph Wiggum technique (looping an agent until it converges): https://ghuntley.com/ralph/
- Spec-driven development (spec as authoritative source of intent): https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- “Shipping at Inference Speed” by Peter Steinberger (structural autonomy): https://steipete.me/posts/2025/shipping-at-inference-speed
- OpenAI’s Harness engineering writeup (environment + feedback loops as the core system): https://openai.com/index/harness-engineering/

The implementation here is minimal, but the direction is informed by these approaches.
