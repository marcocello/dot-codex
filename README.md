## dot-codex

Minimal structure around Codex to make autonomous development predictable.

The human defines the target: a feature spec (`features/<id>/feature.yaml`), constraints, and what “done” means. Codex reads the repository, implements changes, runs commands, fixes failures, and iterates until checks pass. Correctness is enforced by scripts, not by the model.

`AGENTS.md` defines how Codex operates inside a repository: which files are authoritative, how specs are interpreted, and how optional project architecture (`docs/architecture/overview.md`) is applied if present. It works with or without `press.py`.

Skills provide reusable architectural patterns (for example, `python-backend` or `frontend`). They enforce cross-project consistency without polluting individual repos.

Determinism comes from two scripts. These scripts decide success.
- `$HOME/.codex/scripts/gate` runs repo-wide checks such as linting, tests, and builds.  
- `$HOME/.codex/scripts/acceptance --feature <dir>` runs feature-scoped checks derived from `feature.yaml`.  

`press.py` is an optional wrapper that runs Codex, persists the session, executes gate and acceptance, and re-launches Codex if checks fail. It adds orchestration, not logic.

Specs define intent. Architecture defines structure. Scripts define correctness. Codex produces code.