# Configuration

Runtime configuration lives at `~/.telegram-to-agents/config/config.json`. Run `telegram-to-agents onboarding` or start from [`../config.example.json`](../config.example.json).

The schema rejects unknown fields. Former-product files and removed prompt, provider, memory, automation, agent, transport, or Docker settings are not migrated or rewritten.

## Required settings

| Field | Purpose |
|---|---|
| `provider` | Native harness: `codex` or `claude`. Pass-through is always active. |
| `telegram_token` | Telegram bot token. |
| `allowed_user_ids` | Numeric users allowed to invoke the harness. |
| `project_root` | Existing default harness working directory. |

Telegram policy fields are `allowed_group_ids`, `allowed_channel_ids`, `group_mention_only`, `file_access`, and optional topic `project_roots` mappings. `timeouts.normal` is the fixed gateway deadline; it does not change a native harness limit. `scene.status_reaction` controls only the reaction on the triggering Telegram message.

Set `transcription.automatic_audio` to `true` to transcribe Telegram voice/audio. Its model defaults to `gpt-4o-transcribe`. A key stored in telegram-to-agents' private `.env` is read directly by transcription and is never merged into harness subprocesses. Environment already configured on the service remains part of the native harness configuration.

Configuration is loaded at process start. After editing `config.json`, run:

```bash
telegram-to-agents restart
```

`/new` resets only the current Telegram native-session mapping; it does not reload configuration.
