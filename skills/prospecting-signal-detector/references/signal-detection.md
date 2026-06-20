# Signal Detection Reference

Use this reference for product-agnostic signal classification, query generation, and target surfaces. Product context, sector context, ICP, competitors, and signal criteria must come from user-provided text or files.

## Required Context

Load or ask for:

- Product or project description.
- Sector context, target geography, and target account types.
- ICP roles, buying committee, user personas, and disqualification rules.
- Pain points, trigger events, objections, and urgency markers.
- Competitors, alternatives, incumbent tools, and replacement signals.
- Approved positioning, proof points, claims, and claims to avoid.
- Signal criteria for CRITICAL, HIGH, MEDIUM, and LOW.
- Target platforms, communities, keywords, hashtags, and search queries.

If the user provides a file, treat it as the source of truth for classification and engagement. If multiple files conflict, ask which one wins.

## Default Signal Classes

Use these defaults only until the user supplies more specific signal criteria.

### CRITICAL

Respond within 2 hours.

- Direct request for recommendations in the user's product category.
- Explicit high-urgency pain that the provided product context can credibly address.
- Complaint about a named competitor or incumbent with intent to switch.
- Public request for vendors, consultants, tools, partners, or implementation help.

### HIGH

Respond same day.

- Strong pain signal from an ICP-matching person or account.
- Trigger event that plausibly creates need: new role, funding, launch, expansion, regulation, migration, outage, deadline, hiring, or budget cycle.
- Mention of manual work, process failure, cost pressure, risk, lost revenue, slow delivery, or poor customer/user experience tied to the user's problem space.
- Hiring or roadmap language that matches the user-provided category.

### MEDIUM

Respond within 48 hours.

- Active discussion around the user's category, problem, or market shift.
- Skepticism or objection that the user's positioning can address.
- Event, conference, community thread, or research release relevant to the provided sector context.

### LOW

Add to watch list.

- General discussion without visible buying intent.
- Competitor praise without dissatisfaction.
- Broad market commentary that may inform content but does not merit direct engagement.

## Classification Fields

| Field | Values |
| --- | --- |
| Signal Class | CRITICAL, HIGH, MEDIUM, LOW |
| Signal Type | question, pain, competitor, trigger-event, hiring, funding, conversation, skepticism, event, content-opportunity |
| Source | linkedin-feed, linkedin-search, reddit, industry-forum, community, web |
| Engagement Status | new, touch-1, touch-2, touch-3, converted, archived, skipped |

## Query Generation

Generate searches from the user's context instead of using fixed sector queries.

Pain-based query patterns:

- `"[pain phrase]" AND ("struggling" OR "frustrated" OR "problem" OR "challenge")`
- `"[job to be done]" AND ("manual" OR "slow" OR "expensive" OR "broken")`
- `"[category]" AND ("recommendations" OR "alternatives" OR "tools" OR "vendor")`

Role-based query patterns:

- `"[ICP role]" AND ("new role" OR "just started" OR "hiring")`
- `"[target account type]" AND ("expanding" OR "launching" OR "migrating")`

Competitor-based query patterns:

- `"[competitor]" AND ("alternative" OR "switching" OR "problem" OR "replacing")`
- `"[incumbent category]" AND ("too expensive" OR "not working" OR "failed")`

## Target Surfaces

Use only surfaces relevant to the user's provided sector context:

- LinkedIn feed, content search, people search, profile activity, and notifications.
- Reddit communities named by the user or found through research.
- Public industry forums, Slack/Discord communities with user approval, review sites, job boards, conference pages, newsletters, and web search.

When a surface requires authentication, never enter credentials. Ask the user to log in manually.
