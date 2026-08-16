# Input extraction

## Format routing

- XLSX/XLS/CSV/TSV: use the spreadsheet skill. Inspect all sheets, tables, headers, values, formulas, and relevant formatting.
- DOCX: use the documents skill. Render and inspect every page, then run `scripts/extract_docx_signals.py` to capture paragraph, table, style, color, and highlight evidence.
- PDF: use the PDF skill. Extract text and tables, render pages, and preserve page numbers.
- Screenshot or scan: inspect the image and use OCR when available. Preserve uncertain text as uncertain instead of silently correcting it.
- Markdown, email, or pasted text: preserve headings, list structure, URLs, tags, and surrounding notes.

Do not assume that every company appears in a table. Sources may contain primary lists, refined lists, raw lists, backups, narrative verification notes, exclusions, and personal-contact additions.

## Normalized candidate fields

Capture when available:

- `id`: stable generated identifier.
- `company`: canonical display name.
- `sourceFile`, `sourceSection`, and `sourceLocation` (row, paragraph, list item, or page).
- `originalText` and all duplicate provenance locations.
- Description, category/capability, city/region, original address, phone, website, and contact notes.
- Membership/association flags, verified/unverified status, employee/revenue notes, strategic-fit notes, primary/backup status, and explicit priority.
- Formatting signals such as highlight color, font color, bold, labels, or placement in a refined list.
- Routing city/address, address status, and verification URL.

## Deduplication

Normalize punctuation and corporate suffixes for comparison, but preserve the chosen display name. Merge records only when company identity is sufficiently clear from name plus city, website, address, or contextual evidence. Do not conflate similarly named local and national entities.

When the same company appears in refined, raw, and backup sections, create one candidate with multiple provenance records. Prefer the most specific description and explicit user-curated status, but retain conflicting facts for review.

## Priority signals

Treat source formatting as evidence, not automatic meaning. A highlight color or red font may indicate include, exclude, verify, or urgency depending on the document. Use a legend or nearby prose when available. If a formatting signal materially changes a limited-day selection and its meaning is unclear, ask the user.

When no explicit ranking exists, use this limited-day order:

1. User-mandated companies and fixed appointments.
2. Explicit primary/refined-list companies or personal contacts.
3. Verified target-fit companies.
4. Candidates that complete compact geographic clusters.
5. Backups, uncertain entities, or candidates without routable addresses.

Record a human-readable selection reason for every scheduled and unscheduled candidate.
