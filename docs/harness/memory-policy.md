# Memory Policy

Use the right durable layer for the job.

## Durable Layers

- Codex memories: stable personal preferences, recurring corrections, repeated workflow habits,
  and project pitfalls that should help future chats without becoming hard rules.
- Global or repo `AGENTS.md`: instructions that must reliably apply.
- Skills: reusable workflows with steps, scripts, references, examples, or domain-specific
  judgment.
- Repo docs: project context such as app architecture, conventions, testing, and harness policy.

## Rules

- Do not store secrets, credentials, raw private tokens, or sensitive private details as memory
  candidates.
- Promote repeated operational patterns into a skill when they need procedure.
- Promote hard safety or completion rules into `AGENTS.md`.
- Keep one-off task notes out of durable memory unless the user explicitly asks to preserve them.
