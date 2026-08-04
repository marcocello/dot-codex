# Effective HTML Upstream Guidance

Use this reference to apply and cite relevant guidance from [Plannotator's Effective HTML](https://github.com/plannotator/effective-html) without installing its plugin or copying its skills into this repository.

## Provenance and authority

The sources below were reviewed at commit [`acb4d2a863f10d5d310080cdcbd60ef1cbffd1f9`](https://github.com/plannotator/effective-html/tree/acb4d2a863f10d5d310080cdcbd60ef1cbffd1f9), dated 2026-08-03, and are MIT licensed. The links are pinned for reproducibility; they are provenance, not runtime dependencies.

`html-presentations` remains authoritative for deck narrative, slide pacing, presentation modes, editing, and validation. Effective HTML informs creative direction, artifact fidelity, accessibility, and adjacent visual forms. Do not ask the user to install Effective HTML and do not assume its skills are available locally.

## Source map

| Upstream source | Apply to presentations |
| --- | --- |
| [`html`](https://github.com/plannotator/effective-html/blob/acb4d2a863f10d5d310080cdcbd60ef1cbffd1f9/skills/html/SKILL.md) | Establish audience and job, form, register, fidelity, and interaction; keep the artifact self-contained, accessible, and grounded in real content. |
| [`design-artifact`](https://github.com/plannotator/effective-html/blob/acb4d2a863f10d5d310080cdcbd60ef1cbffd1f9/skills/design-artifact/SKILL.md) | Derive palette, type, composition, and motion from the project and subject instead of reproducing a recurring house style. |
| [`html-wireframe`](https://github.com/plannotator/effective-html/blob/acb4d2a863f10d5d310080cdcbd60ef1cbffd1f9/skills/html-wireframe/SKILL.md) | Keep structural explorations visibly low fidelity; compare genuinely different hierarchy or navigation directions rather than cosmetic variants. |
| [`html-prototype`](https://github.com/plannotator/effective-html/blob/acb4d2a863f10d5d310080cdcbd60ef1cbffd1f9/skills/html-prototype/SKILL.md) | Give an interactive demo slide one bounded credible flow, relevant states, complete keyboard behavior, visible focus, and honest production boundaries. |
| [`html-plan`](https://github.com/plannotator/effective-html/blob/acb4d2a863f10d5d310080cdcbd60ef1cbffd1f9/skills/html-plan/SKILL.md) | Preserve source commitments, ordering, ownership, dependencies, assumptions, and open questions in roadmap or implementation-plan slides. |
| [`html-diagram`](https://github.com/plannotator/effective-html/blob/acb4d2a863f10d5d310080cdcbd60ef1cbffd1f9/skills/html-diagram/SKILL.md) | Select the visual model from the relationship being explained: topology, sequence, process, state, hierarchy, timeline, matrix, or quantity. |
| [`documents-and-presentations`](https://github.com/plannotator/effective-html/blob/acb4d2a863f10d5d310080cdcbd60ef1cbffd1f9/skills/html/references/documents-and-presentations.md) | Pace rather than merely paginate, keep one job per screen, expose essential content without hover, and distinguish a deck from a reading document. |

## Presentation synthesis

Before implementation, record a short design decision in working notes:

- **Audience and job:** who will experience the deck and what decision, understanding, or action it should produce.
- **Mode:** fixed 16:9 stage for live presentation and stable export, or responsive scroll-snap for reading and interactive explanation.
- **Density:** speaker-led or reading-first.
- **Register:** workmanlike, editorial, or expressive.
- **Premise:** one organizing visual idea drawn from the subject's materials, notation, environment, history, or language.
- **Interaction:** the one place, if any, where input or motion materially improves understanding.

Let the project design system outrank personal taste. When no system exists, make the visual premise specific enough that replacing the subject with a neighboring topic would make the design feel wrong.

For adjacent artifacts embedded in slides, borrow only their owning invariant: low fidelity from `html-wireframe`, bounded stateful behavior from `html-prototype`, traceability from `html-plan`, and relationship-first notation from `html-diagram`. The presentation skill still owns pacing, screen fit, navigation, and the audience experience across the whole deck.
