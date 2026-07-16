# Proof Profiles

Read only the sections selected by `SKILL.md`.

## Bug Fix And Internal
- Bug fix profile: start with the smallest regression that fails before the fix.
- Migration/internal profile: prove integrity, equivalence, migration result, or the claimed invariant at its real boundary.
- Static/documentation profile: use only when the feature itself is static analysis, documentation, generated reports, configuration manifests, or source policy. Prefer executing the parser or generator over string searches.

## API And Provider
- API profile: call the real route or app client and verify response, state, and side effects.
- OAuth/API connection: run the API with a test database and fake outer provider endpoints; drive authorize, callback or exchange, status, selection, and disconnect; verify persisted rows and public status.
- Provider/live profile: submit realistic payloads and patch only the outermost external provider/client boundary locally. Prefer safe live read-back when credentials and a safe target exist.
- CRM or mailbox workflow: ingest realistic fixtures through public app/test ingress and read back created, updated, read, or drafted provider objects. Final assistant text and serializer strings are not enough.
- Black-box provider proof should not import app internals or monkeypatch the activation path.

## UI And Artifact
- UI profile: render the component/page or drive the browser; verify visible state, interaction, reload behavior, and screenshots when useful.
- Frontend integration: run the frontend and API stub/server, drive connect, disconnect, toggle, empty, loading, error, and responsive states through the browser.
- PDF/report/artifact: seed source context, call the real endpoint or orchestration path, render or extract the artifact, and verify grounded values, layout-critical state, and missing-fact behavior.

## Reactive And Process Boundaries
- Worker/scheduler profile: seed the same persisted row, status, event, or queue payload the producer writes; run the scheduler/worker pickup path the app uses; verify persisted output, side effects, and idempotent retry.
- Webhook/messaging profile: submit realistic signed payloads to the listener/API boundary and verify state plus outbound provider-client calls and ordering.
- CLI/subprocess profile: cross the real subprocess boundary. A fake executable may replace only the unsafe outer command and must expose argv, environment, cwd, runtime files, durable state, traces, and user-visible output.
- Mocks, fakes, and monkeypatches must not replace the activation path or durable state transition being proven.

## Semantic Pressure
- For semantic behavior, prove the structured outcome rather than an exact response phrase.
- Include paraphrase cases and at least one non-English or wording-shifted case when practical.
- Treat hardcoded natural-language keyword lists, phrase gates, and language-specific routing as fake-pass risks unless the vocabulary is a closed protocol, enum, provider contract, product taxonomy, or explicit specification.
