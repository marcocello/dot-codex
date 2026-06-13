---
name: prospecting-linkedin-content-manager
description: Product-agnostic LinkedIn content management converted from the Claude LinkedIn Content Manager plugin. Use when Codex needs to initialize a LinkedIn content knowledge base, analyze a profile or posts, define LinkedIn strategy, generate topics, research topics, craft LinkedIn posts, build campaign calendars, review campaign results, or maintain a LinkedIn content learning loop for any product, project, sector, or personal brand using user-provided context from text or files.
---

# LinkedIn Content Manager

Use this skill to run a persistent LinkedIn content workflow in the user's current workspace.
Represent the old Claude slash commands as workflow modes selected from the user's request.

## Context Intake

Keep this skill product, project, and sector agnostic. Before strategy, topics, research, or post
creation, load product context, project context, sector context, target audience, voice, goals, and
constraints from user-provided text or files.

Accept context from:

- The user's current message or pasted brief.
- Workspace files the user names, such as a product brief, positioning doc, website copy, ICP notes,
  research notes, campaign plan, or previous content.
- Existing `linkedin-kb/` files.

If required context is missing, ask only for the missing detail. Do not infer a product, sector,
audience, competitor set, or offer from this skill's examples.

## Knowledge Base

Create and maintain `linkedin-kb/` at the workspace root:

```text
linkedin-kb/
|-- profile/profile-data.md
|-- posts/post-history.md
|-- audience/audience-insights.md
|-- campaigns/campaign-log.md
|-- best-practices/learnings.md
|-- topics/topic-research.md
`-- strategy/current-strategy.md
```

Preserve existing files and append dated updates unless the user explicitly asks to rewrite them.
If LinkedIn data requires a logged-in browser session, use Codex Chrome/browser capabilities when
available. Never enter credentials; ask the user to log in manually when blocked.

## Reference Loading

- Read `references/linkedin-strategy.md` for strategy sessions, content pillars, growth levers,
  and metrics.
- Read `references/linkedin-algorithm.md` when optimizing for algorithm behavior, posting timing,
  hashtags, format selection, or distribution.
- Read `references/post-crafting.md` when writing, revising, or packaging posts.
- Read `references/post-templates.md` when the user wants post variants or reusable structures.
- Read `references/hashtag-strategy.md` when selecting or evaluating hashtags.
- Read `references/topic-research.md` when doing deep web research for selected topics.

## Workflow Modes

### Setup

Use when the user asks to set up or initialize the LinkedIn workflow.

1. Ask for the LinkedIn profile URL if missing.
2. Create the `linkedin-kb/` folder structure.
3. Use browser automation only after the user is logged in.
4. Capture profile basics: name, headline, about, current role, follower count, and connections.
5. Scrape the latest 20-30 visible posts when available, including text, date, reactions,
   comments, reposts, impressions when visible, media type, hashtags, and mentions.
6. Save profile data, post history, and initial audience notes.
7. Summarize what was captured and suggest the next useful mode, usually Analyze.

### Analyze

Use when the user asks for profile, post, engagement, or audience analysis.

1. Load profile, post history, audience insights, and learnings.
2. Offer to refresh LinkedIn data before analysis.
3. Analyze engagement rate, comment-to-like ratio, post type, topic, length, hooks, hashtags,
   timing, repeat engagers, and conversation quality.
4. Optionally benchmark 3-5 user-provided competitor or inspiration profiles.
5. Update `linkedin-kb/audience/audience-insights.md` and
   `linkedin-kb/best-practices/learnings.md`.
6. Return a concise report with profile health, top/bottom posts, content mix recommendation,
   audience patterns, opportunities, and risks.

### Strategy

Use when the user wants LinkedIn strategy, content pillars, audience targeting, goals, or schedule.

1. Load the current knowledge base and existing strategy.
2. Load or ask for user-provided product context, sector context, audience, positioning, objective,
   quantitative goals, voice, cadence, and campaign duration.
3. Define 3-5 content pillars mapped to expertise, audience need, and market relevance.
4. Define campaign cadence, format mix, success metrics, and posting schedule.
5. Save the complete strategy to `linkedin-kb/strategy/current-strategy.md`.

### Topics

Use when the user wants content ideas or a campaign topic backlog.

1. Require `linkedin-kb/strategy/current-strategy.md`; ask to run Strategy first if missing.
2. Load audience insights, post history, learnings, and previous topic research.
3. Research current trends, news, controversies, popular formats, and hashtags for the
   user-provided sector context.
4. Generate 5-8 topic ideas per content pillar.
5. Score each topic by strategic alignment, audience resonance, timeliness, differentiation,
   and effort.
6. Present the top 15-20 topics grouped by pillar and ask the user to select or revise them.
7. Save proposed, selected, rejected, and modified topics to
   `linkedin-kb/topics/topic-research.md`.

### Topic Research

Use when the user has selected topics and wants deeper research before writing.

1. Load selected topics from `linkedin-kb/topics/topic-research.md`.
2. Ask which topics to research if selection is ambiguous.
3. For each topic, gather recent sources, statistics, expert views, contrarian views, case
   studies, LinkedIn-specific angles, hashtag candidates, mention candidates, hooks, and visuals
   tied to the user-provided product context and sector context.
4. Save each research brief back to `linkedin-kb/topics/topic-research.md`.
5. Present the most compelling data, recommended angle, and strongest hooks.

### Create Posts

Use when the user wants publication-ready LinkedIn posts.

1. Load strategy, topic research, audience insights, learnings, and post history.
2. Ask which researched topics to turn into posts.
3. For each topic, produce a post package: primary post, 2 variants, hashtags, mentions, media
   recommendation, timing recommendation, and rationale.
4. Organize approved posts into a campaign calendar.
5. Save the campaign to `linkedin-kb/campaigns/campaign-log.md` and create individual post files
   when useful.
6. Remind the user that posts are ready for manual publishing unless they explicitly request
   browser-assisted publishing.

### Review

Use when the user wants campaign results or a learning-loop update.

1. Load campaign log, strategy, learnings, audience insights, and post history.
2. Identify the campaign to review; ask if multiple campaigns are plausible.
3. Use browser automation only after the user is logged in and agrees to scrape current metrics.
4. Capture impressions, reactions, comments, reposts, profile views, follower growth, DMs, and
   connection requests when visible or supplied by the user.
5. Compare each post against baseline averages and campaign goals.
6. Update learnings, audience insights, campaign log, and post history.
7. Propose the next campaign theme, topic ideas, format mix, timing adjustments, and growth
   tactics based on accumulated evidence.

## Output Rules

- Prefer concise briefs, tables, and saved markdown artifacts over long chat-only output.
- Keep strategy and campaign documents dated.
- Do not invent metrics. Mark missing LinkedIn analytics as unavailable or ask the user to provide
  them.
- Use web research for current topic and hashtag evidence; cite sources in research briefs.
