## dot-codex

Minimal structure around Codex to make autonomous development predictable.

The human defines the target: a feature spec (`features/<id>/FEATURE.md`), constraints, and what “done” means at a high level. When asked to generate acceptance coverage, Codex translates behavior described in `FEATURE.md` (including any Gherkin scenarios) into executable black-box tests under the feature folder. Those tests become the concrete definition of success.

Codex then implements the necessary code, updates tests as needed, runs commands, fixes failures, and iterates until all checks pass. Correctness is enforced by scripts, not by the model.

`AGENTS.md` defines how Codex operates inside a repository: which files are authoritative, how specs are interpreted, and how optional project architecture (`docs/ARCHITECTURE.md`) is applied if present. It works with or without `press.py`.

Skills provide reusable architectural patterns (for example, `python-backend` or `frontend`). They enforce cross-project consistency without polluting individual repos.

Determinism comes from two scripts. These scripts decide success.
    `$HOME/.codex/scripts/gate` runs repo-wide checks such as linting, tests, and builds.
    `$HOME/.codex/scripts/acceptance --feature <dir>` runs feature-scoped black-box tests derived from `FEATURE.md`.

`press.py` is an optional wrapper that runs Codex, persists the session, executes gate and acceptance, and re-launches Codex if checks fail. It adds orchestration, not logic.

Specs define intent. Acceptance tests define “done.” Architecture defines structure. Scripts define correctness. Codex produces code.

# Acknowledgments

This structure builds on ideas from:
- The Ralph Wiggum technique (looping an agent until it converges): https://ghuntley.com/ralph/
- Spec-driven development (spec as authoritative source of intent): https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- “Shipping at Inference Speed” by Peter Steinberger (structural autonomy): https://steipete.me/posts/2025/shipping-at-inference-speed
- OpenAI’s Harness engineering writeup (environment + feedback loops as the core system): https://openai.com/index/harness-engineering/

The implementation here is minimal, but the direction is informed by these approaches.
