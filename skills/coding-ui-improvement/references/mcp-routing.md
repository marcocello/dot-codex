# Design source routing

Use this map after inspecting the target interface and repository. Use every configured server through read-only discovery and inspection. Discover the live tool schema before calling a server; tool names can change independently of this skill.

## Configured MCP servers

| Server | Use it for | Constraints |
| --- | --- | --- |
| `agentation` | List sessions and read pending visual annotations as evidence for the written brief. | The toolbar must send to `http://localhost:4747`. Never call reply, acknowledge, resolve, dismiss, or other state-changing Agentation tools from this skill. |
| `landingfolio` | Find shipped hero, pricing, testimonial, navigation, CTA, footer, and other landing-page section references with screenshots and source links. | Requires `LANDINGFOLIO_MCP_TOKEN`. Use screenshots as references, never as copy targets. The free service is rate limited. |
| `shadcn` | List and inspect the built-in `@shadcn`, configured `@canvas-ui`, and configured `@react-bits` registries, then cite relevant candidates in the written brief. | The MCP browses from the skill's catalog workspace. Record candidate identifiers, dependencies, browser support, and required fallbacks without running add commands or copying registry source. Some canvas effects require experimental browser capabilities and must degrade safely. |
| `originkit` | Call `list_components`, `search`, `get_component`, or `fetch` for stack-aware OriginKit components. | Requires `ORIGINKIT_API_KEY`. Prefer only when richer motion or a creative surface is justified. Review source, license, dependencies, and fallback behavior. |

If an authenticated server is unavailable, name the missing environment variable and continue with repository evidence and available sources. Never request a token in chat or write one into `config.toml`.

## Query sequence

For broad audits or redesigns:

1. Query LandingFolio with a specific product type, page section, user goal, and style constraint.
2. Query `@shadcn` for conventional accessible primitives, then search `@canvas-ui` or `@react-bits` only when expressive motion or rendering supports the goal.
3. Query OriginKit with the target framework and interaction need, not generic aesthetic terms.
4. Compare candidates against the existing design system, bundle cost, browser support, accessibility, and maintenance burden.
5. Use Agentation feedback as user evidence; do not let external inspiration override explicit annotations.

For a focused fix, skip unrelated sources. A form validation issue rarely needs LandingFolio or a WebGL component.

## Supplemental Designer sources

These are not separately configured MCP servers. Browse their official docs or machine-readable registries only when the task needs them:

- AICSS: `https://www.aicss.dev/llms.txt` and `https://www.aicss.dev/r/{slug}?format=md` for agent-native status, reasoning, diff, citation, streaming, and task UI.
- React Bits: `https://reactbits.dev/` and its shadcn registry for creative React effects.
- Thinking Orbs: `https://orbs.jakubantalik.com/` for compact agent-state indicators.
- Transitions.dev: `https://transitions.dev/skill.html` for transition critique and refinement guidance.
- GSAP: `https://gsap.com/docs/v3/` for deliberate, complex animation timelines.
- Beautiful UI: `https://beautiful-ui-five.vercel.app/` for manual AI-interface pattern references; treat copied code as unvetted.
- Remotion and Bento: use their installed skills for video or presentation artifacts, not application UI primitives.

Do not install a supplemental package. Do not run add commands or copy registry source. Never enter an implementation phase from this skill; leave installation, code changes, dependency recording, and rendered verification to a later separately requested task.
