---
name: skills-registry-guide
description: Use the connected Skill Registry MCP server to find, inspect, download, publish, submit, and review reusable agent skills. Invoke when the user asks to use or manage the team skill registry.
---

# Skill Registry

Use the tools exposed by the connected `skills-registry` MCP server. Do not substitute local skill-management tools for Registry operations.

## Read and use skills

1. Start with `skills.list` when discovering or checking whether a skill already exists.
2. Use `skills.get` with the exact slug before using, downloading, or changing a skill.
3. When asked to use a Registry skill, read its complete bundle, follow its `SKILL.md`, and retrieve supporting files only as needed.
4. Preserve `.skill_id` when downloading an existing bundle.

## Create or update skills

1. Search before creating and read the current record before updating.
2. Send the complete bundle, including `SKILL.md` and every supporting file. Never invent omitted files, secrets, or credentials.
3. Use the write tool actually exposed by the server:
   - `skills.create` for a new slug on an open instance.
   - `skills.update` for a new immutable version on an open instance.
   - `skills.submit` for a create or update that requires administrator review.
4. Treat a submission as pending until approval. Never claim publication from submission alone.

## Review and report

- If proposal tools are exposed, read the proposal and its current revision before editing, approving, or rejecting it.
- Confirm the returned state, then read back the affected skill or proposal before reporting success.
- State clearly whether the result is published, pending review, rejected, or unchanged.
- Do not install, remove, or reconfigure local skills unless the user separately asks for that local action.
