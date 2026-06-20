---
name: html-presentations
description: Create, edit, amend, restyle, and validate presentation decks implemented as standalone HTML/CSS/JavaScript files. Use when Codex needs to build or revise browser-native slide decks, keynote-style HTML presentations, scroll-snap decks, speaker/demo decks, or presentation-like HTML artifacts using the bundled thariqs.github.io reference patterns.
---

# HTML Presentations

## Core Workflow

1. Clarify the delivery target from the request: new deck, edit existing deck, visual restyle, content amendment, interactive demo deck, or export/print prep.
2. Inspect any existing HTML deck before editing. Preserve its slide structure, navigation model, typography scale, and asset strategy unless the user asks for a redesign.
3. Load only the relevant bundled reference:
   - For a slide deck shell, read `references/thariqs.github.io/html-effectiveness/09-slide-deck.html`.
   - For choosing adjacent HTML artifact patterns, read `references/thariqs-reference.md`.
   - For visual systems, diagrams, interactive prototypes, or report-style decks, grep the bundled `references/thariqs.github.io/html-effectiveness/` files for matching patterns before inventing a new structure.
4. Treat the selected reference as a concrete style contract. Match its visual language, interaction model, component density, animation taste, object types, and all explicitly described objects unless the user asks to diverge.
5. Implement as a standalone HTML file by default: semantic `<section>` slides, embedded CSS, embedded JavaScript only when useful, and no build step unless the target repo already uses one.
6. Verify the deck in a browser. Check first slide, mid-deck slide, final slide, keyboard navigation, scroll behavior, responsive layout, and print/export readiness when requested.

## Creation Guidance

- Start with a deck outline before writing markup: title, narrative arc, slide count, per-slide job, and evidence/data needed.
- For source-heavy decks, first synthesize the source material into: audience, objective, thesis, proof points, objections, and desired next action. Use that narrative spine to decide what belongs in slides; do not paste source notes directly into the deck.
- For customer or sales decks, separate current product truth, credible roadmap, customer-specific diagnosis, and the concrete ask. Keep speculative roadmap language visibly distinct from already shipped capabilities.
- For critique/rewrite requests, review the deck at the narrative level before editing: remove weak framing, reduce generic AI commentary, tighten the point of view, and preserve only examples that support the audience's decision.
- Use one dominant layout idea per slide. Avoid dense prose; split slides when the presenter would need to explain two separate points.
- Prefer scroll-snap full-viewport slides with arrow-key navigation for simple browser-native decks, following the `09-slide-deck.html` reference.
- Keep design tokens in `:root`, then compose slide-specific components below.
- Use inline SVG for simple charts, sparklines, ornaments, and diagrams when it keeps the deck portable.
- When a reference or user brief names objects, include those exact objects in the output. If the brief leaves room for invention, propose concrete, domain-specific objects that extend the same visual system instead of generic filler. For animation and interaction work, think like `07-prototype-animation.html`: pick small tangible UI or product objects, give each object a clear state change, and make motion reveal behavior.
- Add a fixed slide counter when the deck is navigated live.
- Include responsive CSS for narrow screens even when the primary target is a 16:9 presentation viewport.

## Editing Guidance

- Make minimal, localized edits for amend requests. Do not rewrite the whole deck when the request is content, order, copy, or small visual changes.
- Preserve IDs and anchors unless changing slide order requires updates.
- Update slide counts, counters, bylines, agenda items, and navigation labels whenever slides are added, removed, or reordered.
- Keep repeated components consistent across slides by editing shared classes instead of duplicating one-off styles.
- When replacing content, check text fit at presentation size and mobile width. Shorten copy or adjust layout before reducing type below readable sizes.

## Validation Checklist

- Open the HTML in a browser or local server; do not rely only on static reading.
- Test `ArrowRight`, `ArrowDown`, Space, `ArrowLeft`, and `ArrowUp` when keyboard navigation exists.
- Screenshot or visually inspect at a presentation viewport such as `1440x900` and a narrow viewport such as `390x844`.
- Confirm no text overlaps, counters update, scroll snapping lands on whole slides, and responsive layouts do not hide critical content.
- If print/PDF export is requested, add or verify `@media print` rules and check page breaks.

## Reference Use

The bundled `thariqs.github.io` copy is reference material, not a template to paste wholesale. Reuse its patterns exactly where they define style: standalone HTML files, restrained design tokens, focused slide sections, inline SVG data visuals, compact JavaScript for navigation or interaction, and the same level of care in object choice. Do not flatten a rich reference into generic cards, placeholder shapes, stock icons, or unrelated decorative elements.
