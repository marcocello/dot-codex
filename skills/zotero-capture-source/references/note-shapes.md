# Note shapes

Use these structures after reading the complete available source. Keep each note valid HTML because Zotero stores rich-text notes.

## Video source note

Title the note exactly `Raw_Transcript`:

```html
<h1>Raw_Transcript</h1>
<p><em>Source: Official YouTube captions. Light punctuation cleanup only.</em></p>
<p>[00:00] First transcript segment...</p>
<p>[00:30] Next transcript segment...</p>
```

State whether the transcript came from official captions, a publisher transcript, a verified public mirror, or local speech-to-text. Preserve the source's spoken wording and timestamps. Do not insert analysis into this note.

## Article source note

Title the note exactly `Source_Outline`:

```html
<h1>Source_Outline</h1>
<p><em>Canonical source reviewed in full.</em></p>
<h2>Opening section</h2>
<p>Grounded paraphrase of the section's argument.</p>
<h2>Named article heading</h2>
<p>Grounded paraphrase of the section's argument and evidence.</p>
```

Preserve the article's real heading names when useful. Do not copy the full article. Use short quotations only when the exact wording is analytically important.

## Highlights note

Title the note exactly `Highlights`:

```html
<h1>Highlights</h1>
<p><em>Source-grounded synthesis. Timestamps refer to the original video.</em></p>
<h2>1. Clear statement of the idea (12:30–14:10)</h2>
<p>Explain the mechanism, argument, or example used by the source. Preserve qualifications and limits.</p>
<p><strong>Interpretation:</strong> State a useful implication only when needed, and label it as interpretation.</p>
```

For articles, replace the timestamp with the real article heading, for example `(Section: “A new operating model”)`.

## Grounding test

Before saving each highlight, verify:

1. A timestamp or article section points to the supporting source material.
2. The explanation can be reconstructed from that source material.
3. An example is attributed to the source rather than generalized beyond it.
4. Any inference not stated by the source is labeled `Interpretation`.
5. The point adds substance rather than restating the title.
6. No quotation is presented from memory.
