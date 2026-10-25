# Architecture

## Responsibility boundary

```text
Telegram                  Gateway                       Native harness
updates/files  ->  auth, topics, sessions  ->  Codex App Server or Claude CLI
                   progress and delivery       native configuration
```

The gateway owns Telegram authorization, topic/project routing, unchanged attachment storage, file-delivery policy, temporary progress, timeouts, cancellation, optional audio transcription, and Telegram-to-native-session mappings.

Codex or Claude owns all agent behavior. There is no gateway system prompt, memory injector, roster, background-worker layer, model/tool selector, provider registry, transport supervisor, task scheduler, webhook server, or gateway-managed agent system.

## Runtime path

1. `telegram_to_agents.__main__` loads the strict focused configuration and starts one Telegram runtime.
2. `AuthMiddleware` rejects unauthorized input before the harness path.
3. Telegram creates a structured `UserTurn`: unchanged text plus original attachment paths. Enabled audio transcription replaces audio with transcript text.
4. `Orchestrator` resolves the chat/topic project and provider- and backend-safe native session ID.
5. `CLIService` executes the turn once through `CodexCLI` or `ClaudeCLI` and never retries an accepted turn.
6. Codex checks the canonical native control path before the turn. An actual Unix socket selects `codex app-server proxy`; an absent path or ordinary file selects `codex app-server --listen stdio://`. The selection is fixed for that turn and is never retried on the other transport. Static images are native `localImage` items. Claude uses `claude --verbose -p --output-format stream-json`. No agent-policy overrides are supplied.
7. Telegram displays bounded temporary status/tool/commentary, confirms its deletion, then delivers the final answer once.

Sessions contain the selected provider, Codex transport backend when applicable, and native ID. Changing provider or Codex backend starts a fresh session instead of cross-resuming an incompatible ID. Topic mappings control the same project boundary for execution, `/where`, media, and workspace-scoped file delivery.

Remote Control is optional. Both Codex paths are native App Server transports and inherit Codex configuration; the Codex GUI is not a separate gateway protocol. The product targets Linux systemd user services only, while foreground source execution may run on macOS.
