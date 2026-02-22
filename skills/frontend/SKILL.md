---
name: frontend
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics. Use when implementing frontend/UI changes (React / Next.js).
metadata:
  short-description: Optional user-facing description
---

## Scope
- Applies when:
  - The feature affects UI
  - React / Next.js project detected
  - Feature includes user-facing interaction

## Structure expectations
- UI components → hooks/state → API client → shared utils
- No business logic inside UI components
- Keep components focused and composable

## Design principles
- Avoid generic “AI-safe” layouts
- Use intentional typography (avoid default system stacks)
- Define CSS variables for colors/tokens
- Prefer small, meaningful animations over generic micro-interactions
- Ensure layout works on desktop and mobile

## Implementation rules
- Reuse existing components before creating new ones
- Follow existing lint/build conventions
- No large refactors unless required

## Tests (required if repo has frontend tests)
- Extend existing test setup (vitest/jest) if present
- Add meaningful assertions for new behavior
- Do not weaken or delete tests

## Acceptance harness (if feature includes UI behavior)
- If feature.yaml includes frontend acceptance criteria:
  - Add feature-scoped acceptance under `FEATURE_DIR/acceptance/`
  - Prefer test-based verification over snapshot-only tests
- Tests must assert observable behavior (DOM/state changes)

## Reference repos (Frontend)
Use only if current repo lacks a needed pattern.

- ~/software/.../nextjs-app
  - Next.js app structure
  - Lint/build scripts
  - Component conventions

- ~/software/.../design-system
  - Tailwind tokens
  - Layout patterns
  - Accessibility baseline

When using a reference repo:
- Borrow structure/patterns, not entire files
- Mention which repo and what pattern was reused (1 line)