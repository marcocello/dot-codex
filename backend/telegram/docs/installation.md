# Installation

## Prerequisites

- Linux VM with Python 3.11+ for the background service, or macOS for foreground source use
- authenticated `codex` or `claude` CLI available to the service user
- Telegram bot token, allowed numeric user ID, and existing project directory
- optional OpenAI API key for voice/audio transcription

## Install

```bash
pipx install .
telegram-to-agents onboarding
```

Onboarding selects and verifies the native harness, collects Telegram and project settings, optionally stores the transcription key in `~/.telegram-to-agents/.env`, and can install a systemd user service.

Run `telegram-to-agents` in the foreground. For the installed service use `telegram-to-agents status`, `telegram-to-agents stop`, and `telegram-to-agents restart`.

Codex transport selection is automatic. A live `<CODEX_HOME>/app-server-control/app-server-control.sock` (or `~/.codex/app-server-control/app-server-control.sock` when `CODEX_HOME` is empty) selects `codex app-server proxy`; without an actual Unix socket, the gateway runs `codex app-server --listen stdio://`. Remote Control is optional, and there is no transport option in onboarding or `config.json`.

For a local macOS source run, use `uv sync --extra dev`, `uv run telegram-to-agents onboarding`, then `uv run telegram-to-agents`. This uses the `codex` executable and native Codex configuration inherited from that shell. macOS foreground execution is supported; service installation remains Linux systemd-only.

Configure model, reasoning, tools, skills or agents, sandbox, approvals, permissions, and repository instructions through Codex or Claude itself. telegram-to-agents does not accept or translate those settings.
