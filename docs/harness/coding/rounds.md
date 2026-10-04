# Features, shared checks, and implementation rounds

Every acceptance criterion needs appropriate evidence; every feature does not need a separate proof runner. Prefer a lightweight feature inventory with shared journeys and focused checks. Retain an existing standalone proof when it is useful; do not rebuild working tests merely to adopt this layout.

## Feature coverage

Keep outcomes and identifiable acceptance criteria in `docs/features/<id>/FEATURE.md`, and lifecycle status in the existing index. Complex features may have detailed specifications; a short outcome and criteria are enough for simple ones. In a mapped feature, `COVERAGE.json` replaces the compulsory per-feature PROOF and runner:

```json
{
  "version": 1,
  "criteria": {
    "AC1-save-and-reopen": ["docs/verification/customer-journey"],
    "AC2-other-account-denied": ["docs/verification/customer-permissions"]
  }
}
```

Criterion IDs refer to the feature's prose; there is no mandatory Markdown syntax. The assigned author/reviewer checks that every promised criterion is represented. The validator checks nonempty mappings and runnable referenced packages; it cannot discover an omitted promise. Use criterion IDs in test names or normal assertion output so each promised outcome can be located without another mapping file. Every mapped package is required for completion, not an alternative that can silently be skipped. Preserve provider-dependent criteria while prerequisites are unavailable; report partial progress without marking that feature done.

Shared packages live at `docs/verification/<check-id>/`, each with `PROOF.md` and `proof/run.sh`. They need no FEATURE or lifecycle entry. Existing `docs/features/<id>` proof packages can also be referenced. A package can wrap existing repository test commands rather than copy tests; record determining helpers, fixtures, configuration and code scope. FEATURE owns acceptance criteria, COVERAGE links their IDs to checks, and PROOF records the command, activation/read-back, controlled external edges and limits. Reference criteria rather than copying their prose. Keep focused API/CLI/invariant checks where they observe the promised boundary; use a real browser journey for user interaction and composition. Generic regressions do not become acceptance merely by changing their label.

Use a small number of independently runnable checks organized by behavior and cost. For example, a real-AI quality check, a revocation check, and a visual check may share setup utilities without requiring each other's full suites. Legitimate prerequisite state must still be established; never seed the outcome under test. A successful journey does not replace permission, failure/recovery, or concurrency negatives.

## Deliver a round

A round is a coherent group of authorized features integrated and reviewed against a stable candidate, not a new product feature or a fixed sprint length. Choose its scope from the user's journey and dependencies. Keep one actively edited feature per task. When its implementation and affected focused checks are finished but shared verification is pending, use `active -> implemented`, then continue the next slice. `implemented` releases the claim and is not completion. Do not postpone all testing to the end of the round.

At the round boundary, run relevant composed journeys and outstanding focused acceptance checks. Perform final review of the combined candidate, criteria mapping, current evidence, and material gaps. Features with independent satisfied coverage may complete while another remains blocked. A round review may cover multiple features without repeating the same test or review per feature. Different implementation/acceptance owners can use separate receipts sharing the same evidence; attribute actual roles, never invent a common author.

Record a round receipt using the [capture commands](evidence.md#shared-checks-and-round-reviews). It binds each selected feature's mapping and the selected evidence. A feature marked done means it was verified at that recorded round/candidate; it is not a permanent assertion about today's code. `check-round` validates the whole round. Completing one feature validates its mapped proof packages and the round’s supporting regressions; unrelated feature-only checks do not block it. Completion automatically writes a portable `completion.json` beside FEATURE. Inventory reads use that historical record; new completion still requires raw current evidence.

## Rerun only affected checks

Before an expensive run, check changed login/navigation/setup and capture readiness with a short real probe. Do not run a known-blocked full suite merely to rediscover its prerequisite failure. Isolate expensive checks when the outcome permits; do not remove their accepted obligations.

Declare a check's determining inputs once in its optional `proof/inputs.json`, using repository-relative paths:

```json
{"scope": ["src/customer", "tests/customer", "package.json"], "include": ["local-fixtures/customer.json"]}
```

Capture automatically reuses this declaration; `--scope` and `--include` add paths. `include` is optional. Include shared dependencies, startup/configuration and relevant contracts; owning acceptance files, referring feature contracts/mappings, and the declaration itself are always fingerprinted. Changing the declaration invalidates its prior evidence. Without a declared or CLI scope, capture remains broad. These paths are maintained with the check, not selected anew for each feature or run.

After repair, rerun affected checks and reuse unchanged evidence. New round completion validates the covered feature contracts/mappings and selected check inputs, including shared dependencies and directory additions/deletions, rather than another whole-repository snapshot. Old version-1 rounds keep their original boundary. Scope completeness still requires understanding dependencies; hashes cannot discover omitted inputs. Use broad capture when those dependencies are unknown.

A newer failed or unfinished attempt supersedes an older pass for the same package. A repair inside a monolithic package still requires that package's full rerun; split it independently along legitimate acceptance boundaries before claiming partial reuse. Shared state, dependency changes, or integration uncertainty justify broader verification. Round completion never combines incompatible candidates merely because each was once green.

## Incremental adoption

Preserve existing feature contracts, tests, failures, and receipts. Map one coherent round to existing useful checks, extracting only the expensive or duplicated checks that materially improve execution. Do not migrate the entire backlog, rewrite old completion history, silently waive criteria, or start application runs merely to update harness instructions. Review accepted boundary changes under the normal proof rules.
