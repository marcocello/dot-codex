---
name: coding-wordpress
description: "Implement, bootstrap, or maintain WordPress plugins, themes, Bedrock apps, Gutenberg blocks, WooCommerce extensions, deployment structure, and PHP or JavaScript tests."
---

# WordPress

Purpose: implement WordPress work while preserving the detected project shape and keeping WordPress-specific structure decisions inside this skill.

## Scope

- Applies when the task touches WordPress plugin, theme, block, shortcode, hook, REST endpoint, admin screen, WooCommerce extension, `wp-content`, `wp-cli`, or Bedrock-style code.
- Use `coding-php-legacy-maintainer` instead for generic PHP apps that are not WordPress.
- Use `coding-frontend` as well when the WordPress change includes substantial React/Next.js UI outside WordPress admin, blocks, or theme assets.

## Structure Expectations

- Preserve the existing WordPress layout first. Do not move a repo between classic WordPress, plugin-only, theme-only, Composer-managed, or Bedrock layouts unless explicitly requested.
- For greenfield WordPress work with no established WordPress layout, force this top-level tree:
  - `wordpress/app/` for all WordPress runtime and application code.
  - `wordpress/deployments/` for deployment YAML, hosting config, Docker, Helm, Kustomize, or environment-specific release assets.
  - `wordpress/pipelines/` for CI/CD pipeline definitions and release automation.
- Do not create WordPress application code outside `wordpress/app/` in a greenfield WordPress repo.
- Do not put deployment or pipeline files under `wordpress/app/` unless the platform requires it.
- Never edit WordPress core files for application behavior. Put custom behavior in a plugin, mu-plugin, theme, child theme, or Bedrock app package according to the repo's current pattern.
- For plugin work, prefer `wordpress/app/wp-content/plugins/<plugin-slug>/` in greenfield classic WordPress repos and `wordpress/app/web/app/plugins/<plugin-slug>/` in greenfield Bedrock repos. In brownfield repos, keep the plugin in the already-established plugin directory. Keep the plugin bootstrap file at the package root and put implementation under `src/` or `includes/` according to existing convention.
- For theme work, prefer `wordpress/app/wp-content/themes/<theme-slug>/` in greenfield classic WordPress repos and `wordpress/app/web/app/themes/<theme-slug>/` in greenfield Bedrock repos. In brownfield repos, keep the theme in the already-established theme directory. Keep templates, parts, functions, assets, and build source in the layout already used by the theme.
- For full-site work, identify whether the repo is classic WordPress, Bedrock, plugin-only, or theme-only before creating files. If no layout exists, create the forced `wordpress/` tree and then choose the smallest app layout that matches the requested deliverable rather than scaffolding a full WordPress install by default.
- Keep Composer, npm, PHPCS, PHPUnit, and build configuration at the owning plugin, theme, app, or repo root according to the existing project convention.

## Implementation Rules

- Use WordPress hooks, filters, capabilities, nonces, escaping, sanitization, and prepared queries appropriately for the change.
- Keep business logic out of template files when a plugin or service class is the clearer owner.
- Prefer activation/deactivation hooks, migrations, or idempotent setup routines over one-off admin side effects.
- Use `coding-prepare-environment` before running Composer, npm, wp-cli, PHPUnit, PHPCS, dev servers, containers, or database-touching commands.
- Do not install, activate, deactivate, or delete plugins/themes against a live database unless the user explicitly asks.
- Preserve secret-bearing `wp-config.php`, `.env`, and hosting/deployment files.

## Tests

- Add or extend the smallest relevant test when the repo has PHPUnit, WP test suite, Pest, PHPCS, Jest, Vitest, Playwright, or npm scripts.
- For plugin/theme PHP behavior, prefer repo-local PHPUnit or WP test suite conventions when present.
- For blocks or asset builds, use the existing JS test/build script.
- For user-visible WordPress behavior, use `coding-proof-author` to define black-box proof in `FEATURE_DIR/PROOF.md` when a feature directory is in scope.
- Do not weaken coding standards, lint rules, or bootstrap checks to get green.

## Reference Patterns

- Greenfield WordPress code lives under `wordpress/app/`; deployments and pipelines live under `wordpress/deployments/` and `wordpress/pipelines/`.
- Greenfield Bedrock app code lives under `wordpress/app/web/app/`; configuration usually lives under `wordpress/app/config/` and `wordpress/app/.env`.
- Greenfield classic WordPress custom code lives under `wordpress/app/wp-content/plugins/`, `wordpress/app/wp-content/mu-plugins/`, or `wordpress/app/wp-content/themes/`.
- Brownfield plugin-only repositories may keep the plugin package at the repo root. Preserve that shape when it already exists.
