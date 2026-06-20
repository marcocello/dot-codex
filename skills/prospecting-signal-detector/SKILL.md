---
name: prospecting-signal-detector
description: Product-agnostic GTM signal detection workflow converted from the Claude Signal Detector plugin. Use when Codex needs to scan LinkedIn, Reddit, or industry discussions for buying signals for any product, project, sector, or ICP; classify opportunities from user-provided signal criteria; maintain signals-database.json; generate signal reports; draft engagement actions; or safely execute LinkedIn engagement with explicit approval.
---

# Signal Detector

Use this skill to scan, classify, store, report on, and act on GTM buying signals for any product, project, sector, or ICP. Product context, sector context, ICP, competitors, and signal criteria must come from user-provided text or files.

## Context Intake

Before scanning, reporting, or engaging, load the user's context from the current message, pasted brief, or named workspace files. Useful inputs include:

- Product or project description.
- Sector context and target geographies.
- ICP roles, company types, and qualification rules.
- Pain points, triggers, jobs to be done, objections, and disqualifiers.
- Competitors, alternatives, and adjacent categories.
- Signal criteria for CRITICAL, HIGH, MEDIUM, and LOW.
- Approved positioning, banned claims, tone, and engagement constraints.
- Target platforms, communities, search queries, hashtags, and keywords.

If context is missing, ask for the smallest missing piece before proceeding. Do not infer the product, project, sector, competitor list, or signal criteria from this skill.

If the user wants Codex to generate this context, or if product context, sector context, ICP, competitors, alternatives, or signal criteria are too incomplete to scan reliably, use `prospecting-signal-context-builder` before scanning. Prefer loading `signal-context.md` when it exists.

## Data Store

Maintain `signals-database.json` at the workspace root:

```json
{
  "metadata": {
    "last_scan": "",
    "total_signals": 0,
    "total_scans": 0
  },
  "signals": []
}
```

Always append new signals, preserve existing engagement history, and update metadata after every scan or engagement session. Before adding a finding, deduplicate by same person, same source, and same week. Also check whether similar content from the same person was already engaged.

## Reference Loading

- Read `references/signal-detection.md` for product-agnostic signal classes, context intake, query generation, target surfaces, and classification rules.
- Read `references/scan-procedures.md` before running a scan.
- Read `references/response-templates.md` before drafting comments, posts, DMs, or follow-up actions.

## Safety Rules

- Never enter credentials. If LinkedIn requires login, ask the user to handle authentication.
- Never post, schedule, DM, or comment without explicit approval.
- Show the original post URL or search query before engaging.
- Take a screenshot or otherwise verify page state before browser-assisted posting.
- Stop immediately if the page, person, or post does not match the selected signal.
- Never repeat an action already present in `engagement.actions_taken`.
- Never pitch the user's product or project in Touch 1 comments.
- Treat competitor praise as intelligence only unless there is explicit dissatisfaction or an alternatives request.

## Workflow Modes

### Scan

Use when the user asks to scan for signals, detect opportunities, or check LinkedIn/Reddit.

1. Load `references/signal-detection.md` and `references/scan-procedures.md`.
2. Create `signals-database.json` if missing.
3. Use Codex Chrome/browser capabilities for LinkedIn surfaces only when the user is logged in.
4. Scan LinkedIn feed, LinkedIn content searches, relevant role-change searches, configured Reddit communities, industry forums, and keyword searches as scope allows.
5. Classify each signal as CRITICAL, HIGH, MEDIUM, or LOW and assign signal type and source.
6. Capture author, title, company, profile URL, summary, source URL, full text when available, timestamp, and scan session.
7. Deduplicate before writing.
8. Save all findings and show a quick summary with class breakdown and top 3 actions.

Use morning or afternoon scan session names based on local time: `YYYY-MM-DD-morning` before noon, `YYYY-MM-DD-afternoon` otherwise.

### Report

Use when the user asks for a signal report for `today`, `week`, or `all`.

1. Read `signals-database.json`; if missing or empty, tell the user to run Scan first.
2. Default to `week` when no period is specified.
3. Filter to the requested period: last 24 hours, last 7 days, or all data.
4. Save `signal-report-YYYY-MM-DD.md` with executive summary, class/type/source breakdown, critical and high actions, engagement pipeline, trend analysis, and weekly recommendations.
5. Show a concise chat summary with the most actionable items and the report path.

### Engage

Use when the user asks to engage signals, draft responses, post comments, send DMs, or turn market signals into LinkedIn posts.

1. Load `references/signal-detection.md` and `references/response-templates.md`.
2. Read `signals-database.json`; if missing or empty, tell the user to run Scan first.
3. Build an engagement ledger from every `engagement.actions_taken` entry.
4. Apply deduplication:
   - Remove fully engaged signals.
   - Remove signals with `next_step_date` in the future.
   - Remove competitor tracking signals from engagement actions.
   - Separate market-trend signals as content opportunities.
   - Respect Touch 1, Touch 2, Touch 3 ordering.
5. Present eligible signals with state, class, person, signal type, source, original post URL, and recommended action.
6. Ask the user which signals to engage.
7. Draft text using the matching response template and touch number.
8. Ask for approval or edits for each draft.
9. For browser-assisted LinkedIn actions, navigate to the original post/profile, verify it, show the draft in place before posting, and get final explicit approval.
10. Update `signals-database.json` for posted, scheduled, skipped, edited, or failed actions.

Every `actions_taken` entry should include:

```json
{
  "date": "YYYY-MM-DD",
  "type": "linkedin-comment | linkedin-post | linkedin-dm | skipped",
  "text": "The exact approved text or skip note",
  "platform": "linkedin",
  "original_post_url": "https://...",
  "our_action_url": "",
  "scheduled_time": null,
  "hashtags_used": []
}
```

## Signal Object Shape

Use this shape for new records:

```json
{
  "id": "sig_YYYYMMDD_HHMMSS_NNN",
  "timestamp": "2026-02-25T10:30:00Z",
  "scan_session": "2026-02-25-morning",
  "source": "linkedin-search",
  "signal_class": "HIGH",
  "signal_type": "data-frustration",
  "person": {
    "name": "",
    "title": "",
    "company": "",
    "profile_url": ""
  },
  "content": {
    "summary": "",
    "url": "",
    "full_text": ""
  },
  "engagement": {
    "status": "new",
    "touch_number": 0,
    "actions_taken": [],
    "next_step": "",
    "next_step_date": ""
  },
  "notes": ""
}
```

## Output Rules

- Keep scan summaries brief and action-oriented.
- Preserve raw source URLs so the user can verify every action.
- Record uncertainty rather than inflating signal class.
- Save partial scan results when a surface is blocked.
