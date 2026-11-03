# dot-codex

In December 2025, I stopped writing and reading code. Codex now does the implementation work.

That changed where I put my engineering effort: understanding the problem, deciding what should happen, and checking whether the result works. A convincing response or a passing test suite can still leave the user's problem unresolved. Completion needs evidence from the place where the software is actually used.

I built dot-codex to make that workflow repeatable. It gives Codex a shared set of instructions, skills, and checks for investigating rough ideas, clarifying consequential choices, implementing accepted behavior, and retaining enough evidence to explain what worked and what still needs attention.

The aim is dependable delegation. Codex should carry the work through implementation and verification while bringing decisions about scope, cost, permissions, and external effects back to me when needed. Small corrections should remain small; material features need explicit acceptance and realistic proof.

The agent is also a sparring partner: understand the surrounding context, challenge weak assumptions, and discuss product direction before settling on an implementation.

Codex supplies the runtime; the harness organizes how its capabilities are used.

## Pillars

- **Spec-driven:** accepted behavior gives implementation and verification a shared target.
- **Proof-driven:** realistic checks establish whether the intended behavior works where it is used.
- **Proactive execution:** investigate the surrounding goal, challenge assumptions, propose useful improvements, and carry authorized work through verification.
- **Evidence and reflection:** retained decisions and results support diagnosis and deliberate improvement.

## Workflow

Start by understanding the request and its surrounding context. Resolve consequential choices, define the accepted behavior, and choose checks that demonstrate it. Implement the change, verify the result where it is used, and retain useful evidence.

Scale the work to the problem: a small correction needs a focused fix and check; a feature needs explicit acceptance and realistic proof.

[`AGENTS.md`](AGENTS.md) defines the operating rules. [`skills.toml`](skills.toml) declares the skills and optional plugins. The [harness design guide](docs/harness/overview.md) explains the workflow.

## Install

With Codex already installed:

```bash
git clone https://github.com/marcocello/dot-codex.git
cd dot-codex
./install.sh
```

The installer links this checkout to `~/.codex`, exposes its skills, and creates configuration only when absent. Existing configuration and unrelated skills are preserved.

With the default link, `CODEX_HOME` is optional. For an explicit current-shell export, run `eval "$(./install.sh --print-env)"`.

The [installation guide](docs/harness/installation.md) covers optional external skills and the development-tool plugins packaged in [`integrations/`](integrations/).
