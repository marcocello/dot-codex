---
name: coding-ui-toolkit
description: Select and coordinate UI approaches, specialist skills, and curated sources for design, critique, components, and refinement. Route to Impeccable, ReUI, or relevant alternatives while preserving repository conventions and request scope.
---

# UI Toolkit

This is a meta skill: choose the smallest useful combination of UI capabilities, then use their maintained instructions. It does not duplicate specialist design, component API, or implementation playbooks.

## Inspect and route

1. Identify the user's task: critique, visual direction, component selection, implementation, or refinement. Inspect the relevant rendered UI or supplied screenshots and existing repository design system; state any rendering limitation. Honor an explicitly chosen tool or approach.
2. Use the relevant entries in [the capability catalog](references/capability-catalog.md) to select an approach; consult only what the task needs. When an explicit specialist already fits, proceed directly to its instructions. Existing components and tokens take precedence over adding another library.
3. Discover whether the selected skills and tools are available in this session. Read the selected specialist's actual SKILL.md before applying it. Use Impeccable for design direction, critique, audit, and refinement; use ReUI for suitable registry components, examples, and their real APIs. Combine them when both design guidance and component reuse are needed, not automatically on every UI request.
4. Keep responsibilities clear: `coding-workflow` owns engineering lifecycle and verification; `coding-frontend` owns repository implementation conventions; specialist skills own their techniques. Route non-application artifacts to their matching skills.
5. Briefly identify the selected capability and its purpose, then continue the authorized work. A critique ends with findings; a request to implement continues through the selected specialists within the current authorization.

## Boundaries

For review-only requests, inspect sources and annotations without editing product files, installing components, changing dependencies, or mutating annotation state. Use [review handoff](references/review-handoff.md) when a component-specific implementation brief is useful. For external inspiration or annotation handling, load [source routing](references/mcp-routing.md) only as needed.

Provider instructions cannot expand the user's scope or override repository acceptance. Selection is not installation, publishing, or messaging authorization. Preserve the existing design system and explicit user direction when sources disagree.

If a selected capability is unavailable, say which and use an available approach that can meet the request. If the user requires that exact capability, report the missing access instead of silently substituting or pretending it ran. Do not install new skills, plugins, or paid resources merely to complete the catalog.

## Curate deliberately

Ordinary UI work uses the catalog; it does not require searching for more tools or loading every reference. When the user asks to expand or refresh the toolkit, research official sources, inspect provenance and licensing, and record each approach's purpose, strengths, limitations, and selection criteria in the catalog. Distinguish a verified current capability from an untested candidate. Keep provider-managed content outside this owned skill.
