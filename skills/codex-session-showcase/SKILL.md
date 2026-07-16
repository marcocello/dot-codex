---
name: codex-session-showcase
description: "Turn completed Codex work into a grounded showcase recap with technical outcomes, optional screenshots, and concise proof-of-work framing."
---

# Codex Session Showcase

Purpose: turn a Codex session into a sharp, credible recap that shows real work through evidence, not hype.

## Workflow

1. First thing: capture the current Codex desktop app screenshot before drafting.
   - The required target is the Codex app window or the visible Codex app on the user's screen.
   - Browser screenshots do not satisfy this requirement unless they capture the Codex app itself.
   - Use the available desktop, app-window, or full-screen capture tool that can capture the visible Codex app.
   - If no screenshot tool is obvious, call `tool_search` for screenshot, current app window, desktop screen capture, or screen screenshot tools.
   - On macOS, if shell execution is available, request approval and run `/usr/sbin/screencapture -x /tmp/codex-session-showcase.png`.
   - After shell capture, verify the file exists and is non-empty before using it.
   - If screenshot capture requires approval, request it before drafting.
   - If capture is unavailable or denied, say that briefly and continue without claiming a screenshot exists.
   - Do not report that no current Codex app screenshot tool was available until tool discovery and the macOS fallback are unavailable, fail, or are denied.
   - Keep the screenshot path or URL available for the final output.
2. Identify the audience and surface:
   - LinkedIn post, private DM, portfolio note, website blurb, internal update, case-study snippet, or short chat reply.
   - If the user does not specify, write a short public-facing recap.
3. Gather only concrete material:
   - actual user goal
   - skills or tools used
   - files changed
   - commands run
   - verification evidence
   - before/after behavior
   - decisions, tradeoffs, blockers, or constraints
   - real screenshots, chat exports, or snapshot links when available
4. Decide the output shape:
   - **One-liner**: one compact sentence for a caption or DM.
   - **Short post**: 2-4 short paragraphs.
   - **Case-study note**: problem, approach, evidence, result.
   - **Snapshot card copy**: title, subtitle, evidence bullets, optional image note.
5. Draft in a confident, concrete voice.
6. Remove filler, generic AI language, and explanations of internal process that do not help the reader.

## Evidence Rules

- Never invent screenshots, file changes, commands, tests, metrics, model behavior, user outcomes, customer names, time saved, or production impact.
- If the user mentions a screenshot but no file or URL is available, refer to it only as a planned or optional snapshot slot.
- If a screenshot or chat artifact exists, describe what it proves in plain terms.
- Use command results and test outcomes only when they were actually run or provided by the user.
- Do not expose secrets, private paths, tokens, or raw logs that may contain sensitive data.
- If evidence is thin, write a smaller recap instead of inflating the story.

## Style

- Lead with the real work, not with "I used AI".
- Make Codex visible as the working method when relevant. Do not explain Codex mechanics unless the user asks.
- Show seriousness through concrete nouns: feature contracts, failing tests, file diffs, proof checks, migrations, operational constraints, review findings, deployment gates, or screenshots.
- Keep the language cool but not theatrical.
- Avoid corporate phrases, motivational framing, clickbait, hashtags, emojis, and grand claims.
- Prefer short paragraphs and natural rhythm over formal sections unless the user asks for structure.

## Snapshot Handling

When the user wants a snapshot or screenshot included:

- The default screenshot is the current Codex desktop app; capture it first when tooling is available.
- Include the screenshot path or URL before the written copy when capture succeeds.
- Use an existing local image path, browser screenshot, chat export, or user-provided URL when available.
- Mention the visual only if it exists or the user explicitly asks for a placeholder.
- For a placeholder slot, use direct copy such as: `Snapshot: Codex session showing the feature spec, failing test, fix, and green check.`
- Do not claim that a snapshot was captured unless it was actually captured.

## Output Defaults

Unless the user asks for another format, return only the finished copy. Do not add an explanation of the rewrite or a checklist.
