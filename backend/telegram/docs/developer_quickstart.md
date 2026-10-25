# Developer quickstart

```bash
uv sync --extra dev
uv run pytest
uv run ruff check src/telegram_to_agents tests/features tests/transcription
uv run mypy src/telegram_to_agents
```

The executable tracked proof is:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" \
  --feature-dir docs/features/telegram-to-agents-gateway \
  --timeout-seconds 180 \
  --note "telegram-to-agents candidate"
```

The proof replaces only external Telegram, OpenAI HTTP, Codex App Server, and Claude CLI boundaries. It exercises the real dispatcher, authorization, media routing, provider- and backend-safe session persistence, managed WebSocket proxy and embedded stdio serializers, lost-ack at-most-once behavior, progress/cancellation state, package build, and installed-wheel entrypoint.
