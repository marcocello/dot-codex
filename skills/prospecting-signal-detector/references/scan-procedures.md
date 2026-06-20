# Scan Procedures

Detailed product-agnostic procedures for each scanning surface.

## Before Scanning

1. Load product context, sector context, ICP, competitors, and signal criteria from user-provided text or files.
2. Generate the scan plan from that context: platforms, communities, search queries, target roles, competitor terms, pain phrases, and disqualifiers.
3. Create `signals-database.json` if missing.
4. Confirm logged-in surfaces are available before using browser automation.

## LinkedIn Scan Procedure

### Feed Scan

1. Navigate to `linkedin.com/feed` when the user is logged in.
2. Read visible post content using browser or accessibility tools.
3. Scan a bounded set of recent visible posts.
4. Compare each post against the user-provided signal criteria.
5. Extract author name, title, company, profile URL, post summary, post URL, engagement count, and relevant quoted evidence.

### Search Scan

1. Navigate to LinkedIn content search.
2. Run generated pain, category, competitor, and trigger-event queries.
3. Scan a bounded number of recent results per query.
4. Filter by recency when useful.
5. Extract the same fields as feed scan.
6. Run people or job searches only when the user-provided ICP makes them relevant.

### Notification Scan

1. Navigate to LinkedIn notifications when the user asks for it.
2. Check for profile views, post engagement, connection requests, mentions, and replies from ICP-matching people or accounts.
3. Extract person, company, action type, and source URL where available.

## Reddit and Community Scan Procedure

1. Navigate to communities named by the user or identified from the provided sector context.
2. Sort by new or recent when possible.
3. Scan posts since the last scan or within the user-requested window.
4. Search using generated pain, category, competitor, and trigger terms.
5. Check comments for additional first-person pain, tool requests, or competitor dissatisfaction.
6. Extract title, author, community, summary, URL, comment count, and quoted evidence.

## Data Storage Format

Every signal is stored as a JSON object:

```json
{
  "id": "sig_YYYYMMDD_HHMMSS_NNN",
  "timestamp": "2026-02-25T10:30:00Z",
  "scan_session": "2026-02-25-morning",
  "source": "linkedin-search",
  "signal_class": "HIGH",
  "signal_type": "pain",
  "person": {
    "name": "Example Person",
    "title": "Example Role",
    "company": "Example Company",
    "profile_url": "https://example.com/profile"
  },
  "content": {
    "summary": "ICP-matching person described a high-urgency problem from the brief.",
    "url": "https://example.com/post",
    "full_text": "Relevant quoted evidence or a concise paraphrase."
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

## Storage Location

All signals are stored in `signals-database.json` at the workspace root:

```json
{
  "metadata": {
    "last_scan": "2026-02-25T10:30:00Z",
    "total_signals": 42,
    "total_scans": 15
  },
  "signals": []
}
```

Always append new signals. Before adding a signal, check if a similar signal already exists by person/account, source, and week.
