# Frontend And Sites Routing

## Goal
Keep Sites available for intentional Sites work while ensuring ordinary repository-local React and Next.js application work follows the global coding kernel and the `coding-frontend` structure contract.

## Behavior
- Generic repository-local React or Next.js construction is owned by the applicable stack skill before any initializer runs.
- `coding-frontend` owns the default `frontend/app` and `satnaing/shadcn-admin` baseline when the user or repository has not selected a different starter.
- Sites remains enabled.
- Sites owns construction only when the user explicitly requests Sites or when `.openai/hosting.json` existed before the task began.
- A Sites manifest created during the current task cannot retroactively authorize Sites or replace the selected stack structure.
- Once Sites legitimately owns the task, its existing build and hosting workflow remains unchanged.
- Target repositories do not need a local `AGENTS.md` or `AGENTS.override.md`.
- The shared gate accepts a normal target repository without either instruction file.
- The dot-codex harness profile continues to require its own `AGENTS.md` as the global Codex kernel source.
- The dot-codex home contains no self-referential `.codex` symlink.

## Constraints
- Do not disable or uninstall `sites@openai-bundled`.
- Do not edit the versioned bundled Sites plugin cache.
- Do not create project-local agent instruction files merely to satisfy the shared gate or document a structure chosen during the task.
- Select the structure owner before scaffolding, dependency installation, route creation, tests, or application files.
- Preserve unrelated active configuration and feature work.

## Non-Goals
- Removing Codex support for repository-specific `AGENTS.md` files when a user explicitly wants them.
- Changing Sites behavior after Sites has legitimately been selected.
- Changing the shadcn-admin baseline beyond clarifying its ownership boundary.
- Proving deterministic compliance by every future model version.
