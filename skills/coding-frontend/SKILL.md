---
name: coding-frontend
description: "Implement, bootstrap, or refactor React and Next.js interfaces with strong layout, interaction, responsive behavior, and visual quality while preserving repo conventions."
metadata:
  short-description: React and Next.js frontend implementation
---

# Frontend

Purpose: implement, bootstrap, or refactor user-facing React/Next.js work while preserving the repo's design system and frontend conventions.

## Scope
- Applies when:
  - The feature affects UI
  - React / Next.js project detected
  - Greenfield work needs a frontend skeleton or `frontend/app`
  - No existing frontend package exists and the feature requires user-facing UI
  - Feature includes user-facing interaction

## Structure expectations
- UI components -> hooks/state -> API client -> shared utils
- No business logic inside UI components
- Keep components focused and composable
- In the default greenfield layout, frontend application code lives in `frontend/app`.

## Default UI baseline
- Preserve an existing repo design system when one is already established.
- For new React/Next.js frontend work with no existing design system, use `shadcn/ui` by default.
- When the task requires creating a frontend and the user/repo does not specify a different starter, clone [satnaing/shadcn-admin](https://github.com/satnaing/shadcn-admin) as the default UI baseline and modify that cloned codebase as the frontend baseline.
- Do not recreate a generic shadcn app from scratch when this default applies; adapt the cloned `satnaing/shadcn-admin` project in place.
- If `frontend/app` is missing or has no existing frontend package, clone before adding package scaffolding, tests, routes, or UI files. Clone the baseline into `frontend/app` first, then make feature changes inside that cloned codebase.
- Do not create a minimal Vite, Next.js, or generic React skeleton when the default clone applies.

## Design principles
- Avoid generic “AI-safe” layouts
- Use intentional typography (avoid default system stacks)
- Define CSS variables for colors/tokens
- Prefer small, meaningful animations over generic micro-interactions
- Ensure layout works on desktop and mobile

## Implementation rules
- Before installing packages, starting dev servers, or running frontend checks, use `coding-prepare-environment`.
- Reuse existing components before creating new ones
- Follow existing lint/build conventions
- No large refactors unless required
- Avoid backward compatibility work by default; do it only when explicitly requested

## Tests (required if repo has frontend tests)
- Extend existing test setup (vitest/jest) if present
- Red phase: add/update the smallest relevant frontend test and confirm it fails first
- Green phase: implement the minimal UI/code change and make that same test pass
- Add meaningful assertions for new behavior
- Do not weaken or delete tests

## Feature Proof (if feature includes UI behavior)
- If `FEATURE_DIR/PROOF.md` is missing or weak, use `coding-proof-author`.
- For user-facing UI behavior, prefer browser E2E proof that exercises the app as a user.
  - Prefer test-based verification over snapshot-only tests.
- Tests must assert observable behavior such as DOM state, navigation, persisted data, or API effects.

## Reference repos (Frontend)
Use only if current repo lacks a needed pattern.

- `$HOME/software/marcocello/meshify-frontend`
  - Next.js app structure
  - lint/build scripts
  - component conventions

When using a reference repo:
- Borrow patterns, not whole implementations.
- Mention repo + pattern reused (1 line).
