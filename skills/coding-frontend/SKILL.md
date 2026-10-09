---
name: coding-frontend
description: "Own repository-local React and Next.js interface construction, bootstrap, and refactors, including generic web apps when Sites is enabled; preserve repo conventions and defer only to explicitly or previously established platforms."
metadata:
  short-description: React and Next.js frontend implementation
---

# Frontend

Read [Coding writing](../../docs/harness/coding/writing.md) once per task and apply it to specifications, proof, reports, and human interaction.

Purpose: implement, bootstrap, or refactor user-facing React/Next.js work while preserving the repo's design system and frontend conventions.

The coding lifecycle skills own routing, discovery, fixed acceptance, Goals, review, and recording. This skill supplies frontend technique; apply [product discovery and autonomy](../coding-product-partner/SKILL.md#discovery-and-autonomy) to inspect surrounding interactions even for clear requests; keep focused Repairs lightweight.

## Scope
- Applies when:
  - The feature affects UI
  - React / Next.js project detected
  - Greenfield work needs a frontend skeleton or `frontend/app`
  - No existing frontend package exists and the feature requires user-facing UI
  - Feature includes user-facing interaction

## Structure expectations
- Separate rendering, reusable state, and external I/O when those responsibilities need independent ownership or testing; a small component need not acquire layers merely to match a diagram.
- Keep shared domain policy and permission decisions out of presentation components. Local display and interaction logic can stay with the component.
- Keep components focused and composable
- Follow the greenfield component locations owned by `coding-prepare-environment`: frontend application code lives in `frontend/app`.

## Platform ownership
- Sites remains available but does not own generic frontend construction.
- Defer construction to Sites only when the user explicitly requests Sites or `.openai/hosting.json` existed before the task began.
- Treat repository state captured before the first initializer as the routing evidence. A Sites manifest created during the current task cannot change the selected structure owner.
- When Sites legitimately owns construction, follow the Sites skills instead of applying this skill's default baseline.

## Default UI baseline
- Preserve an existing repo design system when one is already established.
- For new React/Next.js frontend work with no existing design system, use `shadcn/ui` by default.
- For an admin/dashboard product with no selected starter, consider [satnaing/shadcn-admin](https://github.com/satnaing/shadcn-admin) when its navigation, framework, and components fit the accepted experience. Inspect fit before cloning; a landing page or focused tool may be better served by a smaller scaffold.
- Explicit starter choices take precedence. Reuse useful patterns without importing unrelated demo pages or product behavior. A starter's People/Tasks pages do not determine the application's entities or workflows; resolve consequential mappings in Product Partner.

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
- Preserve established consumers and accepted contracts. Add compatibility machinery only for an actual supported consumer or migration need; ask before consequential breaking changes outside the request.

## Verification
- Reuse the existing test setup and select checks for affected components, shared hooks/state, API clients, and consuming screens.
- Add a focused regression test when a concrete behavior risk lacks coverage; reproduce the failure when practical. Small copy, spacing, or internal cleanup does not automatically require a new test.
- For material UI features, exercise the real browser journey and assert observable DOM state, navigation, persisted data, or API effects. Screenshots alone do not establish interaction correctness.
- Implement against the fixed proof. Route proof defects through the [central proof procedure](../../docs/harness/coding/proof.md#fixed-acceptance), preserving accepted behavior when repairing test setup or assertions. Repair introduced regressions within the current feature run.

## Reference repos (Frontend)
Use only when the current repository lacks a needed pattern.
When using a reference repo:
- Borrow patterns, not whole implementations.
- Mention repo + pattern reused (1 line).
