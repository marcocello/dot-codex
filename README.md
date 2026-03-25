## dot-codex

Minimal structure around Codex to make autonomous development predictable.

The human defines the target: a feature spec (`docs/features/<id>/FEATURE.md`), constraints, and what “done” means at a high level. When asked to generate acceptance coverage, Codex translates behavior described in `FEATURE.md` (including any Gherkin scenarios) into executable black-box tests under the feature folder. Those tests become the concrete definition of success.

Codex then implements the necessary code, updates tests as needed, runs commands, fixes failures, and iterates until all checks pass. Correctness is enforced by scripts, not by the model.

`AGENTS.md` defines how Codex operates inside a repository: which files are authoritative, how specs are interpreted, and how optional project architecture (`docs/ARCHITECTURE.md`) is applied if present.

Skills provide reusable architectural patterns (for example, `python-backend` or `frontend`). They enforce cross-project consistency without polluting individual repos.

Determinism comes from two scripts. These scripts decide success.
    `$HOME/.codex/scripts/gate` runs repo-wide checks such as linting, tests, and builds.
    `$HOME/.codex/scripts/acceptance --feature <dir>` runs feature-scoped black-box tests derived from `FEATURE.md`.

Orchestration in this repo is script-driven (`scripts/gate`, `scripts/acceptance`, `scripts/ensure_venv`). No in-repo `press.py` wrapper is currently present.

Specs define intent. Acceptance tests define “done.” Architecture defines structure. Scripts define correctness. Codex produces code.

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

### 4) Skills currently available
- `feature`: create/update `docs/features/<id>/FEATURE.md`
- `feature-discovery`: quick breadth-first discovery before coding
- `fix-issue`: minimal corrective change with regression checks
- `python-backend`: backend layering + pytest discipline
- `frontend`: React/Next.js UI implementation discipline
- `architecture-deep-dive`: deep component architecture analysis
- `compare-architectures`: compare current architecture vs reference
- `maintainability-review`: codebase maintainability and function-quality audit

### 5) Standard workflow (day-to-day)
1. Define feature directory and spec:
```bash
mkdir -p docs/features/<feature-id>
$EDITOR docs/features/<feature-id>/FEATURE.md
```
2. Prepare toolchain:
```bash
./scripts/ensure_venv
```
3. Implement with Codex (default mode):
```bash
codex "Implement docs/features/<feature-id>/FEATURE.md"
```
4. Validate repo:
```bash
$HOME/.codex/scripts/gate
```
5. Validate feature:
```bash
$HOME/.codex/scripts/acceptance --feature docs/features/<feature-id>
```
6. If a check fails, run a focused fix pass:
```bash
codex "Fix gate failures only. Do not add scope."
codex "Fix acceptance for docs/features/<feature-id> only."
```

### 6) What “good” looks like
- Feature behavior is documented in `FEATURE.md` with clear Gherkin scenarios.
- Red/green evidence exists for the changed behavior.
- `gate` passes.
- feature `acceptance` passes.
- Final handoff ends with `READY`.

# Acknowledgments

This structure builds on ideas from:
- The Ralph Wiggum technique (looping an agent until it converges): https://ghuntley.com/ralph/
- Spec-driven development (spec as authoritative source of intent): https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- “Shipping at Inference Speed” by Peter Steinberger (structural autonomy): https://steipete.me/posts/2025/shipping-at-inference-speed
- OpenAI’s Harness engineering writeup (environment + feedback loops as the core system): https://openai.com/index/harness-engineering/

The implementation here is minimal, but the direction is informed by these approaches.
