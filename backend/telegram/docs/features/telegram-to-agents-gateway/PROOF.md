# Proof

## Done

- Real authorized Telegram updates reach both native harness serialization boundaries with unchanged ordinary text, the selected project `cwd`, no gateway agent-policy overrides, and provider-correct resumable session state.
- Codex automatically uses the managed proxy when its control socket exists and an embedded stdio App Server when it does not, without exposing a gateway transport setting or replaying a turn.
- `/new` creates a new native session, and changing provider cannot resume a session owned by the other harness.
- Telegram audio is transcribed through the real media path while images and files remain byte-for-byte unchanged.
- Progress preserves useful native commentary and compact semantic activity while remaining temporary; repeated activity is grouped, and exactly one clean final answer is delivered. A failed accepted turn is never replayed.
- Onboarding, configuration, source, wheel, service implementation, documentation, and tests expose only Telegram plus Codex/Claude native pass-through on Linux while retaining audio transcription.
- A real Telegram forum-topic name selects one project consistently for harness `cwd`, `/where`, media guidance, and workspace-scoped file delivery.
- The product is consistently distributed and executed as `telegram-to-agents`, imports as `telegram_to_agents`, stores state under `~/.telegram-to-agents`, installs only `telegram-to-agents.service`, and contains no former-product runtime compatibility or migration behavior.
- The source checkout, Hatch discovery/inclusion configuration, type-check commands, and developer guidance use a standard `src/telegram_to_agents/` package layout without a duplicate importable package at repository root. Independently installed wheel and sdist artifacts retain the same public import, CLI, and runtime-start behavior.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/telegram-to-agents-gateway --timeout-seconds 180 --note "final telegram-to-agents native-harness gateway candidate"
```

## Scenario: Telegram text reaches Codex and Claude unchanged

- Producer/activation: feed realistic authorized private-chat Telegram updates through the aiogram dispatcher twice, once with `provider=codex` and once with `provider=claude`, using a temporary gateway home and an existing project directory.
- Consumer: Telegram handler, session manager, orchestrator, CLI service, and real provider command/RPC serializers.
- Read-back: fake outer provider daemons record exact user text, selected `cwd`, native session creation/resume IDs, and serialized requests. Codex uses the App Server bridge; Claude uses its native streaming command. Neither boundary contains model, effort, prompt, tool, sandbox, approval, permission, repository-bypass, or injected gateway/provider-environment overrides.
- Fake: Telegram Bot API and external provider processes only.
- Catches: modifying text, retaining a hidden prompt layer, using gateway state as `cwd`, losing session continuity, selecting the wrong provider, or overriding native harness configuration.

## Scenario: Codex automatically supports managed and embedded App Server

- Producer/activation: feed authorized Telegram turns through the real Codex path with an actual Unix socket at the inherited `CODEX_HOME` canonical control path, with that path absent, and with a non-socket file at that path; create a native session under one transport, change socket availability, and submit the next turn. Separately make the managed fake receive `turn/start` and close before acknowledging it.
- Consumer: Codex transport resolver, bridge command construction, managed WebSocket proxy framing, embedded stdio JSONL framing, native App Server thread/turn RPC, and session persistence.
- Read-back: the fake outer Codex boundary records `app-server proxy` only for an actual socket resolved from inherited `CODEX_HOME` and `app-server --listen stdio://` for a missing path or ordinary file; both paths receive the same unchanged user input, project `cwd`, images, and native JSON-RPC without model or policy overrides. A Codex transport change starts a fresh thread instead of resuming the other transport's ID. The lost-ack turn is observed exactly once by the managed fake, no embedded process starts, and the Telegram update surfaces one failure without replay.
- Fake: Telegram Bot API and the outer Codex executable/App Server only.
- Catches: hardcoding the wrong Codex home, treating an ordinary file as a socket, requiring Remote Control for local foreground use, treating the Mac GUI as a separate protocol, using WebSocket framing against stdio, cross-transport session reuse, configuration surface growth, or retrying after a lost `turn/start` acknowledgement.

## Scenario: Sessions are provider-safe and `/new` is real

- Producer/activation: create and resume a session, submit two rapid same-topic turns while the first remains active, feed `/new`, send another turn, then load the same Telegram session under the other configured provider.
- Consumer: command handler and persisted session manager.
- Read-back: same-topic turns execute serially and the second resumes the native ID persisted by the first; `/new` causes a new native ID; provider and Codex transport switches start fresh provider-native sessions and persist their ownership instead of sending incompatible IDs.
- Fake: Telegram Bot API and external provider processes only.
- Catches: parallel same-topic session forks, last-writer session loss, cosmetic resets, cross-provider session reuse, stale IDs, or native configuration mutation.

## Scenario: Audio is normalized and images pass through

- Producer/activation: feed an authorized Telegram voice update with a caption, a static image, and another file through normal media download handling.
- Consumer: Telegram media handler, OpenAI transcription adapter, and the same harness boundary used by text.
- Read-back: the fake transcription API receives downloaded audio; the harness receives exactly transcript plus caption; forced transcription failure invokes no harness; image and file bytes, suffixes, and paths remain unchanged after download. Codex's real RPC serializer emits the exact original static-image path as a `localImage` item. Claude stdin and non-image Codex input contain the unchanged caption followed only by the defined deterministic attachment line referencing the same absolute path and MIME type.
- Fake: Telegram download/delivery, an outer local OpenAI-compatible endpoint, and external provider process.
- Catches: losing transcription, adding hidden instructions, invoking a harness after transcription failure, WebP conversion, resizing, metadata-destroying rewrites, or original-file deletion.

## Scenario: Progress is useful, temporary, and execution is at-most-once

- Producer/activation: run a delayed native stream that emits a long commentary message, a Codex command with structured read action metadata, an unknown command whose opaque shell text looks like a read, three web searches with two distinct queries, status, and assistant answer data. Also run streams that fail after accepting a turn or end without a terminal result; force one transient network failure during progress deletion and separately force persistent deletion failure.
- Consumer: Codex App Server event bridge, normalized CLI streaming service, and the real Telegram progress/final delivery path.
- Read-back: every temporary Telegram send/edit payload is inspected. The evolving message retains a useful commentary preview beyond the former 50-character collapse; renders the structured command as `Read files`; labels the adversarial unknown shell action only as `Ran command`; groups all three web searches into one `Searched the web` activity with a count; includes concise unique filename/query details; contains no raw reasoning, full shell command, arbitrary arguments, or `[TOOL: ...]` marker; and never publishes answer deltas as repeated edits. A transient deletion failure is retried and then temporary progress deletion succeeds before exactly one clean final answer is sent, and each Telegram update produces exactly one provider turn request even on error. Persistent progress-deletion failure withholds the final answer and records a transport-delivery error rather than posting a second message.
- Fake: Telegram Bot API and external provider processes only.
- Catches: generic or duplicated activity markers, discarded structured native metadata, unusably short commentary, sensitive argument leakage, vestigial pseudo-streaming, progress leaking into final output, skipped cleanup retry, duplicate final messages, and silent fallback replay.

## Scenario: Product identity is self-contained and remains lean

- Producer/activation: start with a current-schema configuration under the default and an explicit `TELEGRAM_TO_AGENTS_HOME` root while unrelated state directories, service units, and environment variables exist as decoys. Exercise runtime lock acquisition plus status and stop against the selected root, and inspect the outer harness environment. Install the Linux service and record every systemctl effect, then launch its real generated command under only the generated systemd environment and exercise configuration, PID, status, and stop. Submit a configuration containing a neutral arbitrary unknown field and require a clear validation failure without rewriting its bytes. Run onboarding/config validation, build both wheel and sdist, install each artifact independently in an isolated target, and start each real entrypoint in a clean temporary environment.
- Consumer: state-root resolver, strict configuration loader, generated config, runtime entrypoint, command registry, Linux service installer, package metadata, dependency graph, source tree, docs, GitHub templates/workflows, license, and wheel/sdist contents.
- Read-back: the default and explicit state roots are resolved while unrelated decoy state remains byte-for-byte untouched; runtime lock acquisition, status, stop, and the installed systemd unit consume the selected root rather than the decoy. The child harness preserves unrelated inherited environment variables while excluding only `TELEGRAM_TO_AGENTS_*`. The neutral arbitrary unknown field produces a validation error and the exact configuration bytes remain unchanged. Every systemctl effect targets only `telegram-to-agents.service`, leaving the unrelated unit untouched. The checkout has one importable source package at `src/telegram_to_agents/` and none at repository root; Hatch wheel/sdist configuration, mypy commands, and repository guidance reference that source location. The wheel and sdist have the exact `telegram_to_agents-0.1.0` names, contain the current import package and metadata, expose the sole `telegram-to-agents` console entrypoint, and each artifact is independently installed in a clean target where its CLI and runtime-start smoke pass; no assertions target former package artifacts. Onboarding asks only for provider, Telegram authorization, project, and optional transcription; configuration accepts exactly Codex/Claude and has no prompt-mode or Codex-transport choice; only retained commands remain; Linux service support is present while macOS/Windows service backends and automatic image conversion are absent. Active docs and package metadata use `https://github.com/marcocello/telegram-to-agents`; LICENSE preserves upstream MIT attribution and explicitly states that telegram-to-agents is a derived version of Ductor by PleasePrompto. README and installation docs state the automatic managed/embedded split, foreground macOS support, and Linux-only service deployment without claiming a GUI protocol.
- Fake: terminal input, native harness auth probes, and Telegram's external API.
- Catches: broken imports or console scripts, interference with unrelated state/services/environment, special-cased rather than schema-wide unknown-field rejection, inconsistent state roots, incorrect package/repository/service identity, missing MIT attribution, making pass-through configurable, hiding dead code behind packaging exclusions, retaining alternate providers/transports/platform services or obsolete contradictory feature packages, losing transcription, or leaving unused dependencies behind.

## Scenario: Telegram security and topic projects remain gateway-owned

- Producer/activation: write and load a real config containing a topic map, submit unauthorized and authorized updates, learn a forum-topic name, then exercise text, `/where`, media, and in/out-of-project file delivery before and after restart; separately configure that matching topic to a missing directory and submit a turn.
- Consumer: Telegram authorization middleware, topic cache, project resolver, provider start request, and allowed-root sender.
- Read-back: config rewrite preserves the open-ended topic map; unauthorized input never reaches a harness; the mapped absolute project is used consistently and persists; in-project files send while out-of-project files are rejected; a matching invalid mapping returns a clear Telegram error without invoking the provider or falling back to the default project.
- Fake: Telegram Bot API and external provider process only.
- Catches: treating pass-through as bypassing transport security, deleting dynamic mappings during config merge, losing topic names, resolving different roots across gateway paths, or silently running in the wrong project when a configured directory is unavailable.

## Scenario: Timeout and explicit cancellation terminate once

- Producer/activation: submit a deliberately slow turn with a short fixed timeout; separately start live delayed turns and route `/stop` for one topic and `/interrupt` for its chat through normal Telegram handlers.
- Consumer: Telegram commands, CLI service, subprocess executor, process registry, progress cleanup, and session persistence.
- Read-back: the targeted provider processes terminate, any provider session ID emitted before termination remains stored, temporary progress is deleted, timeout produces one clear Telegram error while explicit cancellation relies on its command acknowledgement, the same topic accepts a later successful turn, and native turn-start counts prove no request was replayed.
- Fake: Telegram Bot API and external provider processes only.
- Catches: mocked cancellation, sticky abort state, session loss, orphan progress, raw timeout markers, duplicate turns, and cancellation that affects the wrong topic.

## Scope

Proves:

- Telegram is a thin authenticated transport for native Codex and Claude harnesses with no gateway prompt or agent configuration layer.
- Audio transcription is retained while other attachments remain original.
- Provider sessions, progress/final delivery, at-most-once execution, timeouts, cancellation, and topic project boundaries work through realistic runtime paths.
- The source, installed wheel, and installed sdist are lean; deployable service support remains Linux-only while foreground Codex transport selection also works with a local macOS CLI installation.

Does not prove:

- Live Telegram delivery, paid OpenAI transcription, or paid/live provider output.
- Vendor interpretation of native prompt/configuration files beyond proving the gateway emits no overrides.
- Live attachment to the visible Codex Mac GUI; embedded mode is a separate native App Server process using the same Codex authentication and configuration.
- VM upload, production systemd replacement, or production restart; deployment remains a separate approved action.

False-green risks:

- Calling the orchestrator directly could hide Telegram routing defects, so primary turns enter through aiogram updates.
- Mocking CLI service could hide provider flags or RPC fields, so fakes begin after real serialization.
- Checking text alone could miss environment or native-policy overrides, so command/RPC payloads and process environment are inspected.
- Unit-testing transcription or files alone could miss media routing, so media crosses into the selected harness boundary.
- Positive checkout and package assertions verify the canonical `src/` layout and every source-path consumer; installing and smoking both artifacts catches a source distribution that contains files but cannot produce a working installation.
- A green final output could hide a duplicate provider invocation, so the outer daemons count native turn starts.

Evidence method:

- deterministic

Known gaps:

- provider: external Codex/Claude processes are replaced only at their outer process or network boundary; no credentials or usage are required.
- deployment: live Linux VM installation and service restart require separate approval.

## Environment

- Repository-local Python, pytest, uv build tooling, temporary configuration/session directories, and deterministic fake external boundaries; no credentials or network.
- Runner stdout: Python executable/version, pytest version, uv version, repository root, built wheel and sdist names, retained providers/commands, and exercised project directory.
