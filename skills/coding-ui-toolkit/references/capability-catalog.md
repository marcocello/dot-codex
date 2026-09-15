# UI capability catalog

This catalog selects approaches; the current specialist skill and tool documentation owns execution. Sources below were curated from installed skill entrypoints and the existing local source-routing reference on 2026-09-15. Catalog inclusion does not establish live tool availability or grant installation permission. Check availability and current APIs when using an entry.

| Approach | Select when | Strength and boundary | Provenance |
|---|---|---|---|
| Impeccable (`impeccable:impeccable`) | Visual direction, UI critique/audit, hierarchy, typography, responsive design, accessibility, or refinement needs specialist guidance. | Broad design playbooks; preserve review-only scope and existing identity for refinement. Does not own repository lifecycle or replace component API documentation. | Installed Impeccable plugin SKILL.md and its command references; provider-managed. |
| ReUI (`reui`) | A registry component such as a data grid, kanban, filters, or a worked example fits the existing stack. | Component-specific APIs, examples, and reuse. Inspect project compatibility and free/premium licensing; a component recommendation does not authorize installation. | Installed provider bundle SKILL.md and rules; [ReUI](https://reui.io). |
| Existing project components / shadcn registry | Existing primitives already solve the task or conventional controls are sufficient. | Minimizes new dependencies; inspect actual local APIs and tokens before composing. | Project source, components.json, configured registry tools, [shadcn documentation](https://ui.shadcn.com/docs). |
| LandingFolio | A landing-page composition or section needs concrete shipped references. | Visual inspiration rather than a ready-made implementation; access and rate limits may apply. | Existing source-routing reference and configured LandingFolio MCP; verify live availability. |
| OriginKit / React Bits / Canvas UI | A named interaction needs richer motion or expressive components. | Use only when motion serves the task; check license, dependencies, accessibility, browser support, and fallback requirements. | Existing source-routing reference and official/registry sources listed there. |
| Agentation | The user supplied annotations or feedback on the running UI. | Evidence intake, not design authority. Read only during critique; never acknowledge, resolve, or dismiss annotations automatically. | Existing source-routing reference and current Agentation tool schemas. |
| Bento / Remotion / Visualize / Draw.io | The output is a presentation, video, interactive explanation, or native editable diagram. | Artifact-specific workflows; do not treat them as application component libraries. | Installed matching skill catalog and entrypoints. |

## Common combinations

- Critique an existing settings page: Impeccable critique/audit, existing UI evidence, and optional component-specific handoff. No component installation.
- Implement a sortable data grid: inspect local components first; select ReUI if suitable. Add Impeccable only if design decisions need it. Continue under the coding workflow and frontend conventions.
- Explore a landing-page visual direction: Impeccable plus a focused LandingFolio reference search when useful. Do not query all registries.
- Fix a small spacing issue: existing tokens and the relevant specialist only if needed; no broad redesign or research tour.

For additional candidate URLs and access boundaries, use [source routing](mcp-routing.md). New catalog entries should record source, review date, task fit, limitations, license/access notes, and whether the approach has actually been exercised. Do not copy provider playbooks into this catalog.
