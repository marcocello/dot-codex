# thariqs.github.io Reference Index

Use this index to choose the smallest relevant reference file from the bundled
`thariqs.github.io/html-effectiveness/` copy.

- `09-slide-deck.html`: Start here for browser-native presentations. Shows a
  full-viewport scroll-snap deck, semantic slide sections, design tokens, slide
  counter, arrow-key navigation, inline SVG charting, and mobile adjustments.
- `05-design-system.html`: Use for tokenized visual systems, palette structure,
  typography scales, and reusable UI component presentation.
- `10-svg-illustrations.html`: Use for custom inline SVG visuals and diagrams
  that must remain portable inside one HTML file.
- `13-flowchart-diagram.html`: Use for process, decision, or architecture
  diagrams inside a deck.
- `14-research-feature-explainer.html` and `15-research-concept-explainer.html`:
  Use for explanatory decks with research framing, side navigation, and concept
  walkthroughs.
- `16-implementation-plan.html`: Use for roadmap, plan, milestone, mockup, and
  risk slides.
- `11-status-report.html` and `12-incident-report.html`: Use when the deck is
  closer to an executive status, incident, or operational review artifact.
- `07-prototype-animation.html` and `08-prototype-interaction.html`: Use when
  slides need interactive or animated demonstrations.
- `18-editor-triage-board.html`, `19-editor-feature-flags.html`, and
  `20-editor-prompt-tuner.html`: Use for product/tool mockups embedded in
  presentation-like HTML.

Search tips:

```bash
rg "scroll-snap|slide|counter|keydown|@media print|svg|grid-template" \
  references/thariqs.github.io/html-effectiveness
```

Prefer reading one or two matching files deeply instead of loading the entire
reference tree.
