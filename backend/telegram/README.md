# telegram-to-agents

A thin, authenticated Telegram interface to either Codex or Claude, deployable as a Linux service and runnable in the foreground on macOS.

Telegram owns transport, authorization, topics, files, temporary progress, cancellation, and optional audio transcription. The selected native harness owns the system prompt, model, reasoning, tools, skills or agents, repository instructions, sandbox, permissions, approvals, and environment configuration.

telegram-to-agents has no actor prompt or augmented mode. Ordinary text reaches the selected harness unchanged. Images remain original; Codex receives them through native `localImage` input and Claude receives their absolute path through one deterministic transport line. Audio transcription is the only optional model API call outside the selected harness.

## Requirements

- Linux VM with Python 3.11+ for service deployment, or macOS for foreground source execution
- authenticated `codex` or `claude` CLI
- Telegram bot token and allowed numeric user ID
- existing project directory
- optional `OPENAI_API_KEY` for voice/audio transcription

## Install

```bash
pipx install .
telegram-to-agents onboarding
```

Onboarding selects Codex or Claude, verifies that harness, collects Telegram and project settings, optionally enables transcription, and can install a systemd user service. Configuration is stored at `~/.telegram-to-agents/config/config.json`; see [`config.example.json`](config.example.json).

For Codex, transport selection is automatic and has no gateway setting. When the inherited Codex home contains the live native control socket, telegram-to-agents uses `codex app-server proxy` so the turn is handled by Remote Control. Otherwise it starts `codex app-server --listen stdio://` for that turn. Remote Control is optional; both paths use the installed Codex harness and its own authentication and configuration. The Codex GUI is not treated as a separate protocol.

On macOS, run the source checkout in the foreground:

```bash
uv sync --extra dev
uv run telegram-to-agents onboarding
uv run telegram-to-agents
```

The background service commands remain Linux systemd-only.

Run in the foreground with `telegram-to-agents`, or manage the installed service with:

```bash
telegram-to-agents status
telegram-to-agents stop
telegram-to-agents restart
```

## Message flow

```text
authorized Telegram update
  -> exact text plus structured original attachments
  -> selected native harness in the mapped project
  -> temporary commentary/tool progress
  -> delete progress, deliver one clean final answer, persist native session ID
```

`/new` forgets the current chat/topic session. `/stop`, `/interrupt`, and `/stop_all` cancel active work without changing harness configuration. Other retained commands are `/start`, `/help`, `/info`, `/status`, `/reset`, `/restart`, `/where`, `/leave`, and `/showfiles`.

The gateway never emits model, reasoning, tool, prompt, sandbox, approval, permission, repository-bypass, or provider-environment overrides. Telegram authorization and `file_access` remain enforced outside the harness.

See [`docs/config.md`](docs/config.md), [`docs/architecture.md`](docs/architecture.md), and the executable [feature proof](docs/features/telegram-to-agents-gateway/PROOF.md).

telegram-to-agents is based on Ductor by PleasePrompto and retains its MIT license and copyright notice.

Licensed under the [MIT License](LICENSE).
