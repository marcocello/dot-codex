# Named Permission Profile

## Goal
Use the current Codex permission-profile configuration model for Marco's active local configuration and its reusable template without changing the access the existing workspace sandbox intentionally grants.

## Behavior
- The active configuration selects a custom `projects-write` permission profile.
- The profile extends Codex's built-in `:workspace` profile.
- The active profile adds `/Users/marcocello/software`, `/Users/marcocello/Documents`, and `/Users/marcocello/.azure` as reusable workspace roots.
- The template defines the same profile shape with portable placeholder workspace roots.
- The profile enables network access.
- Neither configuration contains `sandbox_mode` or `sandbox_workspace_write`, because either legacy key would override the selected permission profile.
- The existing `multi_agent = false` behavior remains unchanged.

## Constraints
- Preserve the existing model, reasoning effort, personality, approval reviewer, live web search, MCP server, plugin, project trust, notification, and desktop settings.
- Do not add removed feature flags such as `js_repl`.
- Do not copy unrelated settings from the reference example, including disabling tool suggestions.
- Keep credentials and other secrets unchanged.

## Non-Goals
- Narrowing or expanding the current writable roots.
- Adding domain-level network restrictions.
- Migrating MCP credentials to environment variables.
- Changing the permission profile selected by an already-running task.
