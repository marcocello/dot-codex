# Cross-Task Commit Scope

## Goal
Allow a user to invoke `coding-commit` from any task in a project and create one or more coherent local commits for repository changes, even when those changes were produced outside the current task.

## Behavior
- Commit scope is determined by the user's current commit request and the repository's Git state, never by which task, chat, agent, or earlier session produced the changes.
- An explicitly scoped request commits only the named paths or concern.
- An unscoped commit request covers the repository's complete local change set: staged changes, unstaged changes, and relevant untracked files.
- The skill partitions an unscoped change set into the smallest number of coherent, independently reviewable commits and may create multiple commits when the repository contains independent concerns.
- The skill does not exclude, refuse, or require confirmation for a change solely because it predates the current task or is unrelated to the task's subject.
- Existing staging, partial-file changes, ambiguous mixed concerns, and unsafe scope choices retain the skill's current safeguards.
- Every commit group is inspected and staged with explicit paths. The skill never uses `git add .` and never pushes.
- Message-only requests continue to leave Git state unchanged.

## Constraints
- A local commit still requires an explicit user request to commit.
- User-stated scope overrides the unscoped repository-wide default.
- A coherent existing staged selection remains the first or only group; ambiguous user staging is not silently rewritten.
- Dependent implementation, tests, documentation, migrations, configuration, and retained proof remain together.

## Non-Goals
- Pushing commits or changing remote state.
- Committing ignored files, files outside the current repository, or changes excluded by the user.
- Guaranteeing deterministic instruction compliance by every future model version.
