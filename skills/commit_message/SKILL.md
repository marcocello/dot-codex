---
name: commit_message
description: Draft a simple commit message from the latest local changes using Conventional Commits and git diff inspection. Use when the user wants a commit subject or full commit message for staged, unstaged, or most recent changes.
metadata:
  short-description: Draft a clean conventional commit message from recent changes
---

# Commit Message

Purpose: inspect the most relevant local changes and return a defensible commit message without
performing the commit.

## Default behavior
- Do not commit, push, or stage files.
- Prefer staged changes. If nothing is staged, inspect unstaged changes. If the worktree is clean,
  inspect the most recent commit.
- Default to a single-line subject unless the user explicitly asks for a body or footers.
- Keep the subject lowercase, imperative, concise, and without a trailing period.
- Aim for a subject line of 72 characters or less.
- Add a scope only when one area clearly owns the change.

## Workflow
1. Inspect the change set in this order:
   - `git status --short`
   - If staged changes exist: `git diff --cached --stat` then `git diff --cached`
   - Else if unstaged changes exist: `git diff --stat` then `git diff`
   - Else: `git show --stat --format=medium HEAD`
2. Classify the change using Conventional Commits:
   - `feat`: new capability or visible enhancement
   - `fix`: bug fix or behavior correction
   - `docs`: documentation-only change
   - `refactor`: structural change without behavior change
   - `test`: tests only
   - `perf`: performance improvement
   - `build`: build, packaging, or dependency tooling
   - `ci`: CI or automation pipeline change
   - `style`: formatting-only change
   - `chore`: maintenance work that does not fit the categories above
3. Reserve `!` and `BREAKING CHANGE:` for explicit breaking changes supported by the diff.
4. Write the message as `<type>[optional scope]: <description>`.
5. Describe the outcome, not the mechanics.
6. If the diff mixes unrelated concerns, say it should be split and provide two or three candidate
   commit subjects instead of pretending it is one clean commit.

## Output
- For a simple request, output only the final subject line in backticks.
- For a full-message request, include the subject, optional body, and optional footer.
- Do not add explanation unless the user asks for it.

## Examples
- `feat(auth): add passkey sign-in fallback`
- `fix(api): reject empty webhook signatures`
- `docs: clarify local setup steps`
