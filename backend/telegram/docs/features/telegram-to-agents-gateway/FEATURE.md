# telegram-to-agents native-harness gateway

## Goal

An operator can use `telegram-to-agents` as a thin, authenticated Telegram interface to either the native Codex or Claude harness without the gateway acting as an agent framework.

## Behavior

- Telegram is the only messaging transport. `provider` is the only agent-facing choice and has the closed values `codex` and `claude`.
- Pass-through is the only prompt policy. There is no prompt-mode setting or augmented mode in onboarding, configuration, runtime, or documentation.
- Ordinary Telegram text is sent to the selected harness unchanged. `telegram-to-agents` does not add a system prompt, developer instructions, appended prompt files, `MAINMEMORY.md`, an agent roster, background-worker instructions, delegation guidance, repository guidance, memory reminders, or reflection hooks.
- Codex always runs through its native App Server protocol. Before a turn, `telegram-to-agents` resolves the native control socket as `<CODEX_HOME>/app-server-control/app-server-control.sock` when the inherited non-empty `CODEX_HOME` exists, otherwise `~/.codex/app-server-control/app-server-control.sock`. It selects the Remote Control-managed transport via `codex app-server proxy` only when that resolved path is an actual Unix socket; otherwise it starts an embedded local App Server via `codex app-server --listen stdio://`. This is an internal transport decision, not an onboarding or configuration option. Claude runs through its native CLI streaming interface. Each harness's native configuration controls its model, reasoning effort, tools, skills or agents, provider options, sandbox, approval or permission policy, repository instructions, and environment.
- `telegram-to-agents` supplies only transport coordinates required for the turn: the selected project `cwd`, the exact user payload, an optional native session/thread ID, and the gateway timeout. It does not emit model, effort, tool, prompt, permission, sandbox, approval, repository-bypass, or provider-environment overrides.
- A selected existing project directory is the default `cwd`. A valid per-topic project mapping may override it by topic name, `chat:topic`, or topic ID. Invalid or missing directories fail clearly instead of falling back to gateway state.
- The gateway serializes turns per Telegram chat/topic. The first turn creates a provider-native session and each later turn resumes the ID persisted by its predecessor. The persisted record includes its provider and Codex transport so a provider or managed/embedded transport change starts a fresh native session instead of sending an incompatible ID. `/new` clears the current chat/topic session; `/stop` and `/interrupt` cancel active work without altering native harness configuration.
- Telegram shows bounded temporary progress while work is active. Native commentary remains visibly distinct from activity and is truncated only to a useful multi-line preview. Tool activity uses semantic summaries from native tool names and structured Codex metadata, groups repeated activity by kind with counts, and retains up to three concise unique details such as filenames or web-search queries. It never exposes raw reasoning, arbitrary tool arguments, full shell commands, or generic `[TOOL: ...]` markers. Unknown shell activity is truthfully labeled as a command rather than inferred from command text. The temporary state is confirmed removed before one clean final answer is sent; assistant answer deltas are not repeatedly edited into Telegram messages.
- Telegram voice notes and audio files are automatically transcribed when enabled. The transcript plus an optional caption becomes the user payload. Transcription failure returns a clear Telegram error and does not invoke either harness.
- Images and other attachments are downloaded without transcoding, resizing, metadata removal, or deletion of the received file. Internally, a user turn keeps user text and attachment metadata separate until the provider boundary. Codex receives static images as native `localImage` input items alongside unchanged caption text. Claude, and non-image Codex attachments, receive the unchanged caption plus exactly one deterministic transport line per file: `[Telegram attachment: <absolute-path>; type=<mime>]`. That line references the unchanged downloaded file and contains no instruction or inferred description.
- Telegram authorization, mention policy, file access, topic isolation, reply/media normalization, fixed per-turn timeout, cancellation, service lifecycle, and logging remain gateway responsibilities.
- The deployable background service targets Linux VMs only. Foreground source execution may use a local Codex installation on macOS through the same automatic transport selection, but `telegram-to-agents` has no macOS or Windows service backend.
- Configuration accepts only the current telegram-to-agents schema. Unknown former-product or removed agent-framework fields are rejected rather than migrated or silently rewritten.
- The public identity is consistent across the distribution (`telegram-to-agents`), Python package (`telegram_to_agents`), CLI (`telegram-to-agents`), Linux unit (`telegram-to-agents.service`), log/help text, documentation, repository metadata, and default state directory (`~/.telegram-to-agents`). The authoritative public repository URL is `https://github.com/marcocello/telegram-to-agents`, and the new distribution starts at `0.1.0`.
- `TELEGRAM_TO_AGENTS_HOME` is the only product-specific state-root environment variable. It is authoritative for configuration, runtime state, status, stop, and restart; otherwise the state root is `~/.telegram-to-agents`. No former-product state directories, configuration keys, environment variables, or services are detected, copied, converted, filtered, stopped, disabled, or removed.
- Installing the Linux service writes and manages only `telegram-to-agents.service`. The unit safely pins the resolved active state root so a clean systemd environment uses the same configuration, sessions, secrets, files, PID, status, and stop boundary selected during installation.

## Commands

- Retained commands: `/start`, `/help`, `/info`, `/status`, `/new`, `/reset`, `/stop`, `/stop_all`, `/interrupt`, `/restart`, `/where`, `/leave`, and `/showfiles`.
- Removed commands: `/model`, `/effort`, `/memory`, `/cron`, `/tasks`, `/session`, `/sessions`, `/agents`, `/agent_start`, `/agent_stop`, `/agent_restart`, `/agent_commands`, `/diagnose`, and `/upgrade`.

## Constraints

- Audio transcription is the only supported OpenAI API call outside a selected native harness and remains optional.
- Telegram authentication and file restrictions are never delegated to Codex or Claude.
- `telegram-to-agents` must not inject product-specific or provider override variables into harness processes. Service and transcription environment remains allowed at those boundaries.
- The installed package contains no Gemini, Grok, Antigravity, Matrix, Slack, multi-agent supervision, background workers, cron, delegated tasks, webhooks, heartbeat, direct API, prompt enrichment, memory injection, or automatic image-conversion runtime.
- The source checkout contains only runtime, tests, root tooling, assets, and active documentation needed by this product. It contains no former-product compatibility or migration code.
- The canonical Python project layout keeps importable application code only under `src/telegram_to_agents/`, tests under `tests/`, and packaging, documentation, and developer tooling at the repository root. Hatch wheel discovery and sdist inclusion, type-check commands, and repository path guidance all use the `src/telegram_to_agents/` source location. There is no duplicate importable `telegram_to_agents/` package at the repository root.
- A harness failure after accepting a turn is surfaced once. `telegram-to-agents` never replays the same user turn automatically as a fallback.
- Ductor is referenced only in the original MIT copyright/attribution and the explicit derived-work notices in LICENSE and README. Runtime, configuration, services, tests, packaging assertions, and other documentation contain no Ductor compatibility or migration behavior.
- Automatic Codex transport selection occurs before the App Server turn is submitted and is fixed for that Telegram update. Once the bridge writes the `turn/start` request, it never invokes the other transport—even if the selected server received the request but its acknowledgement is lost.
- Temporary progress must be confirmed deleted before the final answer is delivered. If deletion still fails after the bounded retry, the gateway withholds the final answer and surfaces a transport-delivery error rather than leaving progress beside a second final message.
- Timeout, `/stop`, and `/interrupt` terminate the active provider process, clear temporary progress, preserve any provider session ID already observed, and never replay the turn.

## Non-Goals

- Replacing or editing native system prompts, developer instructions, `AGENTS.md`, `CLAUDE.md`, skills, tools, agents, or native configuration.
- Supporting providers other than Codex and Claude.
- Supporting transports other than Telegram.
- Providing gateway model, reasoning, tool, sandbox, approval, or permission selectors.
- Live token-by-token assistant-answer editing in Telegram.
- Supporting macOS or Windows service installation or treating the Codex GUI as a separate public protocol.
- Changing the transcription provider or transcription model beyond retaining the existing OpenAI transcription integration.
