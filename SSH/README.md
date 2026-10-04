# SSH — Stupidly Simple Harness

An alternative Codex home built around four pillars, Pi-inspired coding skills, and an opinionated web-app starter. The model chooses how to solve the product problem; routine stack choices are already made.

```text
SSH/
├── AGENTS.md       # Four pillars and the default stack
├── config.toml     # No configuration overrides
├── skills/         # Optional coding capabilities and the working web-app template
├── docs/           # Pi source mapping, attribution, and verification
├── .gitignore      # Keep generated runtime state out of Git
└── README.md       # This guide
```

The four pillars from the parent harness survive as understand the outcome (spec), own the work (proactivity), prove the outcome (proof), and leave useful evidence (reflection). Specifications can be a clear conversation; evidence can be a concise result. More structure should earn its place through the task.

The [Pi adaptation](docs/pi-adaptation.md) takes its useful coding patterns and rewrites them as portable Codex skills. Only relevant skills need loading; there is no prescribed sequence:

| Capability | Skill | Example request |
| --- | --- | --- |
| Explore or plan | [code-explore](skills/code-explore/SKILL.md) | “Trace this bug and propose the smallest fix.” |
| Review or requested simplification | [code-review](skills/code-review/SKILL.md) | “Review this diff for regressions.” |
| Prove real behavior | [code-verify](skills/code-verify/SKILL.md) | “Check that saving survives a restart.” |
| Release preparation and authorized delivery | [code-release](skills/code-release/SKILL.md) | “Prepare this version for release; don't publish.” |
| Continue or hand off | [code-handoff](skills/code-handoff/SKILL.md) | “Give me the context to continue tomorrow.” |
| Start a new web app | [react-fastapi-scaffold](skills/react-fastapi-scaffold/SKILL.md) | “Build a new internal web tool.” |

Ordinary coding uses the model and native tools directly. You can explicitly invoke a capability with `$code-review` or another skill name. Reviews stay read-only unless fixes are requested; releases carry only the authority actually given. Session management, permissions, tool execution, and available delegation belong to Codex, not these Markdown files. Pi itself is not required.

[Verification](docs/verification.md) covers native Codex discovery and independent diagnosis/release-preparation scenarios. Start a fresh SSH session to load the added capabilities; this existing conversation retains its original harness context.

Use [react-fastapi-scaffold](skills/react-fastapi-scaffold/SKILL.md) for a new web app: React + TypeScript + Vite, Tailwind/shadcn-compatible components, FastAPI, SQLAlchemy + Alembic, PostgreSQL, npm + uv, and Docker Compose + Caddy. It includes a persistent notes demo, tests, CI, local development, and a single-host HTTPS deployment configuration. Existing projects and explicit user choices take precedence. Authentication for a real multi-user product remains a product decision; the deployment baseline protects the demo with an access gate.

Generate a standalone project from this repository root:

```sh
python3 SSH/skills/react-fastapi-scaffold/scripts/scaffold.py /path/to/new-app
cd /path/to/new-app
make up
```

Open `http://127.0.0.1:8080`. See the [starter README](skills/react-fastapi-scaffold/assets/template/README.md) for development, checks, and deployment. The generator refuses nonempty destinations and does not copy credentials or install dependencies. Running `make up` creates private local settings and starts the stack.

These skills package reusable code and focused guidance. There are no lifecycle registries, mandatory review stages, or required feature documents. Codex supplies its own capabilities and underlying instructions. The “90% model” idea is a design direction, not a measured capability claim.

To try this with the CLI, start a fresh session against a separate project:

```sh
CODEX_HOME="/absolute/path/to/dot-codex/SSH" codex --cd "/absolute/path/to/project"
```

Replace both paths. SSH is the Codex home itself; do not add another `.codex` directory inside it. Authentication and integrations may need separate setup in this new home. Existing credentials, plugins, and machine-specific settings have not been copied. This command affects that launch; it does not switch the current desktop session.

Project instructions still apply. Testing inside this dot-codex checkout would also load its repository instructions, so use another project to assess the smaller harness. See the official [instruction discovery and alternate Codex home documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

For a first comparison, try a small repair and a request with a consequential ambiguity. Look for appropriate questions, autonomous follow-through, and evidence of the actual result. File validation alone cannot establish improved model behavior.

Verified on 2026-09-24 in an independently generated project: dependency installation, Python API tests and lint, TypeScript checks, production build, PostgreSQL migrations, container startup, HTTP smoke, browser save/reload and failed-save handling, persistence across container recreation, and database outage/recovery. Desktop/mobile rendering was inspected. Production Compose/Caddy configuration and its shared access gate were validated locally. Public DNS, certificate issuance, and deployment to a real host were not exercised. The host's automatic Docker network pool was exhausted, so runtime verification used a disposable explicit subnet and port 18080. The reusable template keeps normal Compose networking.
