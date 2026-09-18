---
name: coding-frontend
description: "Own repository-local React and Next.js interface construction, bootstrap, and refactors, including generic web apps when Sites is enabled; preserve repo conventions and defer only to explicitly or previously established platforms."
metadata:
  short-description: React and Next.js frontend implementation
---

# Frontend

Purpose: implement, bootstrap, or refactor user-facing React/Next.js work while preserving the repo's design system and frontend conventions.

The coding lifecycle skills own routing, discovery, fixed acceptance, Goals, review, and recording. This skill supplies frontend technique; invoking it does not bypass Shape for undefined behavior or require a feature package for a focused Fix.

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

## Platform ownership
- Sites remains available but does not own generic frontend construction.
- Defer construction to Sites only when the user explicitly requests Sites or `.openai/hosting.json` existed before the task began.
- Treat repository state captured before the first initializer as the routing evidence. A Sites manifest created during the current task cannot change the selected structure owner.
- When Sites legitimately owns construction, follow the Sites skills instead of applying this skill's default baseline.

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
- Use `coding-prepare-environment` when setup or readiness is unknown; reuse a prepared environment.
- Reuse existing components before creating new ones
- Follow existing lint/build conventions
- No large refactors unless required
- Avoid backward compatibility work by default; do it only when explicitly requested

## Verification
- Reuse the existing test setup and select checks for affected components, shared hooks/state, API clients, and consuming screens.
- Add a focused regression test when a concrete behavior risk lacks coverage; reproduce the failure when practical. Small copy, spacing, or internal cleanup does not automatically require a new test.
- For material UI features, the separate proof author should exercise the real browser journey and assert observable DOM state, navigation, persisted data, or API effects. Screenshots alone do not establish interaction correctness.
- Implement against the fixed proof. Route proof defects through the [central proof procedure](../../docs/harness/coding/proof.md#fixed-acceptance), which distinguishes independent setup repair from user-owned acceptance decisions; this skill cannot rewrite frozen proof inputs. Repair introduced regressions within the current feature run.

## Reference repos (Frontend)
Use only when the current repository lacks a needed pattern.
When using a reference repo:
- Borrow patterns, not whole implementations.
- Mention repo + pattern reused (1 line).
