---
name: coding-commit
description: Stage selected local changes and create a local Conventional Commit with a clear subject and compact body. Use when the user wants to commit, stage and commit, create a local commit, or draft a commit message for staged, unstaged, or recent changes. Never push.
metadata:
  short-description: Stage and create a local conventional commit
---

# Commit

Purpose: inspect local changes, stage selected files when appropriate, write a clear Conventional Commit message, and create a local commit when the user asks to commit.

## Default behavior
- Never push. Do not run `git push`.
- Create a local commit only when the user explicitly asks to commit.
- If the user only asks for a commit message, do not stage files and do not commit.
- Stage selected files for the requested scope; do not use `git add .`.
- If the scope is ambiguous, inspect changes and choose the smallest coherent set. Ask only when choosing would risk committing unrelated user work.
- Prefer staged changes. If nothing is staged, inspect unstaged changes. If the worktree is clean, inspect the most recent commit.
- Default to a short full commit message: subject, blank line, then one compact paragraph.
- Make the subject clear enough for a reviewer scanning history to understand the actual change.
- Keep the subject lowercase, imperative, specific, concise, and without a trailing period.
- Keep the subject line at 72 characters or less; prefer 50-60 when clarity is not lost.
- Add a scope only when one area clearly owns the change.
- Avoid vague summaries such as `update changes`, `fix stuff`, `misc cleanup`, or `improve code`.
- The body paragraph should explain why the change matters, what behavior or guidance changed, or any reviewer-relevant constraint instead of restating the diff.
- Keep the body to one compact paragraph unless the user asks for more detail or footers are needed.
- Omit the body only when the user explicitly asks for a subject-only answer.
- Draft one honest commit message even if the change set spans multiple concerns.
- If the change set spans multiple concerns, use a broad but truthful subject and explain the grouped changes in the body.
- Suggest splitting only when the user asks for commit organization or one message would be materially misleading.

## Workflow
1. Inspect the change set in this order:
   - `git status --short`
   - If staged changes exist: `git diff --cached --stat` then `git diff --cached`
   - Else if unstaged changes exist: `git diff --stat` then `git diff`
   - Else: `git show --stat --format=medium HEAD`
2. Decide the operation:
   - Message-only request: draft the message and stop.
   - Commit request with staged files: commit the staged files.
   - Commit request without staged files: stage selected files that match the requested scope.
3. Stage selected files only when committing:
   - Use explicit paths with `git add <path>...`.
   - Use `git add -p` only when partial-file staging is needed and interactive use is practical.
   - Do not stage unrelated files just because they are present.
4. Classify the change using Conventional Commits:
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
5. Reserve `!` and `BREAKING CHANGE:` for explicit breaking changes supported by the diff.
6. Write the message as `<type>[optional scope]: <description>`.
7. Describe the outcome, not the mechanics.
8. Prefer concrete nouns and verbs from the diff over broad verbs like `update`, `change`, or `improve`.
9. If the diff mixes concerns, still draft one honest commit message by default. Use the body to explain the grouped changes instead of pretending the commit is narrower than it is.
10. For a local commit, run `git commit` with the final message. Do not push.

## Output
- For a simple request, output only the final commit message in a `text` fence: subject, blank line, and one compact paragraph.
- For a subject-only request, output only the final subject line in backticks.
- For a full-message request with footers, include the subject, body, and footer.
- For a completed local commit, report the commit hash and message. Do not suggest pushing unless the user asks.
- Do not add explanation unless the user asks for it.

## Examples
```text
feat(auth): add passkey sign-in fallback

Describe the sign-in behavior now covered and why the fallback matters for users.
```

```text
feat(skills): add autonomous execution guidance

Add Goal-based execution guidance and commit-message defaults so Codex can run repeatable checks and draft reviewer-friendly commit messages.
```
