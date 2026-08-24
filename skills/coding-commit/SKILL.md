---
name: coding-commit
description: Stage coherent repository change sets and create one or more local Conventional Commits, or draft messages, regardless of which task or chat produced the changes. Use for commit requests. Never push.
---

# Commit

Purpose: inspect repository changes, select scope from the user's current request and Git state, plan coherent change sets, stage selected files, write clear Conventional Commit messages, and create one or more local commits when the user asks to commit.

## Default behavior
- Never push. Do not run `git push`.
- Create local commits only when the user explicitly asks to commit.
- If the user only asks for a commit message, do not stage files and do not commit.
- Task provenance is not a commit-scope boundary. Changes may predate the current task or come from other tasks, chats, agents, or sessions.
- Apply commit scope in this order:
  - Explicit scope: when the user names paths, a concern, an existing staged selection, or another clear subset, include only the named paths or concern.
  - Unscoped commit request: when the user asks to commit without narrowing the scope, include the complete repository change set: staged changes, unstaged changes, and relevant non-ignored untracked files.
- Treat repository ignore rules as an explicit scope boundary. Never stage an ignored path, never use `git add -f` or `git add --force`, and never use another command or option to bypass ignore rules.
- A request to commit all changes does not authorize overriding ignore rules. If the user explicitly names an ignored path, explain that it is ignored and require an explicit instruction to change the repository's ignore policy before staging it normally.
- If an ignored path is already staged, do not commit it. Report the conflict and ask before changing ambiguous user staging unless the current request already authorizes unstaging it.
- Do not exclude, refuse, or request confirmation for a change solely because it predates or is unrelated to the current task.
- Choose the smallest number of commits that keeps each commit coherent, independently understandable, and reviewable.
- Create one commit when the requested changes form one concern, even when that concern spans several files.
- Create multiple commits when the selected repository scope contains independently meaningful concerns that can be separated without leaving a misleading or broken intermediate state.
- Keep each concern's dependent implementation, tests, documentation, and non-ignored retained proof artifacts in the same commit. Do not split by file type merely to produce more commits.
- Stage selected files for each commit group; do not use `git add .`.
- For a feature commit, stage official failed, timed-out, interrupted, and passing directories under that feature's `proof/runs/` only when repository ignore rules allow them. Ignore rules take precedence over proof-retention guidance.
- Preserve an explicit existing staged selection. Treat a coherent staged set as the first or only commit group; if it mixes concerns and splitting it would require rewriting ambiguous user staging, ask before reorganizing it.
- After applying the explicit-versus-unscoped rules, ask only when the user's stated scope conflicts with the repository state or when proceeding would require rewriting ambiguous staging. Do not ask merely because selected changes came from outside the current task.
- Inspect both staged and unstaged changes in the selected scope before deciding the commit plan. If the worktree is clean, inspect the most recent commit.
- Default to a short full commit message: subject, blank line, then one compact paragraph.
- Make the subject clear enough for a reviewer scanning history to understand the actual change.
- Keep the subject lowercase, imperative, specific, concise, and without a trailing period.
- Keep the subject line at 72 characters or less; prefer 50-60 when clarity is not lost.
- Add a scope only when one area clearly owns the change.
- Avoid vague summaries such as `update changes`, `fix stuff`, `misc cleanup`, or `improve code`.
- The body paragraph should explain why the change matters, what behavior or guidance changed, or any reviewer-relevant constraint instead of restating the diff.
- Keep the body to one compact paragraph unless the user asks for more detail or footers are needed.
- Omit the body only when the user explicitly asks for a subject-only answer.
- Give every planned commit its own honest message describing only that group.
- Prefer one coherent commit over artificial file-by-file, implementation-versus-test, or formatting-only fragmentation.

## Workflow
1. Inspect the change set in this order:
   - `git status --short`
   - `git status --short --ignored` when untracked or generated artifacts may be relevant, so ignored paths are identified and excluded.
   - For staged changes: `git diff --cached --stat` then `git diff --cached`
   - For unstaged changes: `git diff --stat` then `git diff`
   - Inspect relevant untracked files named by `git status --short` without broad staging.
   - If no staged, unstaged, or untracked change exists: `git show --stat --format=medium HEAD`
2. Decide the operation:
   - Message-only request: plan the coherent group or groups, draft every message, and stop without changing Git state.
   - Explicitly scoped commit request: continue with only the named paths, concern, staged selection, or other clear subset.
   - Unscoped commit request: continue with the complete staged, unstaged, and relevant non-ignored untracked repository change set, regardless of which task produced it.
3. Partition the selected scope into commit groups before staging:
   - Use the smallest number of groups that gives each commit one clear purpose.
   - Keep dependent implementation, tests, documentation, migrations, configuration, and retained proof together.
   - Order dependent groups so every intermediate commit is coherent and reviewable.
   - Preserve a coherent staged selection; ask before reorganizing ambiguous staged work.
4. Classify each commit group using Conventional Commits:
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
6. Write each message as `<type>[optional scope]: <description>`.
7. Describe the outcome, not the mechanics. Prefer concrete nouns and verbs from the diff over broad verbs like `update`, `change`, or `improve`.
8. For each commit group:
   - Stage selected files only when committing; stage only that group's explicit paths with `git add <path>...`.
   - Never pass `-f` or `--force` to `git add`. If normal `git add` refuses a path because it is ignored, exclude it and follow the ignore-policy rules above.
   - If the group is already staged, preserve its index content and do not stage later unstaged edits from the same paths.
   - Use `git add -p` only when partial-file staging is needed and interactive use is practical.
   - If a safe partial-file split is impractical, keep the inseparable concern in one commit instead of forcing a split.
   - Do not stage unrelated files just because they are present.
   - Before committing, inspect `git diff --cached --stat` and inspect `git diff --cached` to confirm the index contains exactly that group and no ignored path is being newly introduced.
   - Run `git commit` with that group's final message to create that group's commit.
   - After each commit, re-run `git status --short` and confirm the remaining changes still match the plan.
9. Stop immediately if staging or committing a group fails. Report the commits already created and the exact remaining issue; do not continue into later groups.
10. Do not push.

## Output
- For a one-message request, output only the final commit message in a `text` fence: subject, blank line, and one compact paragraph.
- For a multi-message request, list the planned messages in creation order using one labeled `text` fence per commit.
- For a subject-only request, output only the final subject line in backticks.
- For a full-message request with footers, include the subject, body, and footer.
- For completed local commits, report every commit hash and message in creation order. Do not suggest pushing unless the user asks.
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

For two independently reviewable concerns:

```text
fix(parser): reject incomplete provider responses

Fail closed when a provider omits required fields so invalid data cannot enter the normal processing path.
```

```text
docs(parser): document provider failure handling

Explain the observable error behavior and recovery boundary for operators integrating the provider.
```
