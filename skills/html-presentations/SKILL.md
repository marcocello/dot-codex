---
name: html-presentations
description: Create, edit, restyle, and validate standalone HTML, CSS, and JavaScript presentation decks, including keynote-style, scroll-snap, speaker, and demo formats.
---

# HTML Presentations

## Core Workflow

1. Clarify the delivery target from the request: new deck, edit existing deck, visual restyle, content amendment, interactive demo deck, or export/print prep.
2. Inspect any existing HTML deck before editing. Preserve its slide structure, navigation model, typography scale, and asset strategy unless the user asks for a redesign.
3. Set the audience and job, presentation mode, content density, visual register, fidelity, and useful interaction in working notes before coding.
4. When visual direction remains open or the deck contains wireframes, prototypes, plans, or diagrams, read `references/effective-html.md`. It locally summarizes and cites the relevant Effective HTML skills; do not require the user to install them or depend on network access at task time.
5. Load only the relevant bundled reference:
   - For a slide deck shell, read `references/thariqs.github.io/html-effectiveness/09-slide-deck.html`.
   - For choosing adjacent HTML artifact patterns, read `references/thariqs-reference.md`.
   - For visual systems, diagrams, interactive prototypes, or report-style decks, grep the bundled `references/thariqs.github.io/html-effectiveness/` files for matching patterns before inventing a new structure.
6. Treat selected references as contracts for technique, behavior, density, and explicitly named objects, not as a house visual style. Derive palette, type, composition, imagery, and motion from the user's direction, the project, and the subject.
7. Implement as a standalone HTML file by default: semantic `<section>` slides, embedded CSS, embedded JavaScript only when useful, and no build step unless the target repo already uses one.
8. Verify the deck in a browser. Check first slide, mid-deck slide, final slide, keyboard navigation, scroll or stage behavior, responsive fallback, and print/export readiness when requested.

## Creation Guidance

- Start with a deck outline before writing markup: title, narrative arc, slide count, per-slide job, and evidence/data needed.
- For source-heavy decks, first synthesize the source material into: audience, objective, thesis, proof points, objections, and desired next action. Use that narrative spine to decide what belongs in slides; do not paste source notes directly into the deck.
- For customer or sales decks, separate current product truth, credible roadmap, customer-specific diagnosis, and the concrete ask. Keep speculative roadmap language visibly distinct from already shipped capabilities.
- For critique/rewrite requests, review the deck at the narrative level before editing: remove weak framing, reduce generic AI commentary, tighten the point of view, and preserve only examples that support the audience's decision.
- Choose one presentation mode deliberately:
  - Use a fixed 16:9 stage scaled uniformly to the viewport for live talks, pitch decks, and reliable PDF or screenshot export.
  - Use responsive full-viewport scroll-snap slides for async reading, report-like decks, and interactive explainers that benefit from browser-native reflow.
- Choose a density mode: speaker-led decks use fewer words, stronger pacing, and more slides; reading-first decks carry enough structured context to stand alone without becoming documents pasted into slides.
- Choose a visual register before writing CSS: workmanlike for operational material, editorial for most explainers and narrative decks, and expressive only when the subject and occasion justify it.
- Use one dominant layout idea per slide. Avoid dense prose; split slides when the presenter would need to explain two separate points.
- Keep design tokens in `:root`, then compose slide-specific components below.
- Use inline SVG for simple charts, sparklines, ornaments, and diagrams when it keeps the deck portable.
- When a reference or user brief names objects, include those exact objects in the output. If the brief leaves room for invention, propose concrete, domain-specific objects that extend the same visual system instead of generic filler. For animation and interaction work, think like `07-prototype-animation.html`: pick small tangible UI or product objects, give each object a clear state change, and make motion reveal behavior.
- Add a fixed slide counter when the deck is navigated live.
- Keep essential information visible without hover. Use motion for sequence, comparison, continuity, or feedback, and provide a useful `prefers-reduced-motion` path.
- For a fixed stage, preserve its aspect ratio on narrow screens and provide a useful scaled or scrolling fallback. For scroll-snap mode, include responsive CSS that reflows without hiding critical content.

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
- Check the console, visible keyboard focus, direct slide links when present, reduced-motion behavior, and every interactive control or modeled state.
- Confirm no text or panels overlap, counters update, fixed stages scale without reflow, scroll snapping lands on whole slides when used, and narrow-screen fallbacks do not hide critical content.
- Run an originality check: if a neighboring subject could use the same visual premise unchanged, revise the composition, type, color, imagery, or interaction until the deck belongs to its brief.
- If print/PDF export is requested, add or verify `@media print` rules and check page breaks.

## Reference Use

The bundled `thariqs.github.io` copy is reference material, not a template to paste wholesale. Reuse its structural and interaction patterns where they fit: standalone HTML files, restrained design tokens, focused slide sections, inline SVG data visuals, compact JavaScript for navigation or interaction, and the same level of care in object choice. Do not flatten a rich reference into generic cards, placeholder shapes, stock icons, or unrelated decorative elements.

`references/effective-html.md` is a local synthesis with pinned citations, not an installed dependency or vendored copy. Use it to separate deck form from creative direction and to choose appropriate behavior for wireframes, prototypes, plans, and diagrams embedded in slides.
