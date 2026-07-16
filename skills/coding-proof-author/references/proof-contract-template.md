# Proof Contract Template

Use this template only when creating or materially restructuring `PROOF.md`.

````md
# Proof Plan

## Definition Of Done
- <observable behavior required>

## Primary Proof
Type: <bug-fix | api-provider | browser-ui | worker-scheduler | webhook-messaging | cli-subprocess | migration-internal | static-artifact>

Boundary:
- Producer: <real producer>
- Activation path: <real entrypoint>
- Consumer: <normal application path>
- Durable state: <state or output changed>
- Read-back: <evidence proving the effect>
- Unsafe edge: <live guarded edge or outer fake>

Command:
```bash
scripts/proof_run_capture --serious --feature-dir FEATURE_DIR --source-path <implementation-or-proof-input> --behavior-boundary "<producer -> activation -> consumer -> read-back>" --oracle-scope "$(cat FEATURE_DIR/PROOF.md)" --notes "<summary>" -- <behavioral proof command>
```

Expected evidence:
- <response, visible state, persisted state, provider read-back, or invariant>

## Claimed Behavior Coverage
| FEATURE claim | Real production entrypoint proof drives | Fake boundary used | Read-back |
| --- | --- | --- | --- |
| <claim> | <activation path> | <none or unsafe outer edge> | <durable or visible evidence> |

## Fake Boundary Ledger
- Fake: <outer edge replaced, or none>
- Allowed because: <why it is outside the claim>
- Not faked: <producer, activation, consumer, durable transition, read-back>

## Proof Scope
Proves:
- <specific behavior>

Does not prove:
- <important excluded live, scale, timing, concurrency, provider, or UI condition>

False-green risks:
- <how incomplete behavior could still pass>

Evidence strength:
- deterministic | probabilistic | live gap | manual gap

## Secondary Guards
- <optional lint, typecheck, unit, or static checks>

## Environment And Data
- <fixtures, services, accounts, credentials, safe targets, readiness command>

## Anti-Gaming Review
- Fake pass risk: <incomplete implementation>.
- Proof catch: <observable step that fails>.
- Broken implementation that would still pass: <risk or none after strengthening>.

## Manual Gaps
- None, or <exact user-owned or external gap>
````

Serious evidence belongs under `FEATURE_DIR/proof/runs/<timestamp>/`. Required files are created by `scripts/proof_run_capture`; add screenshots, logs, provider read-back, repair notes, attempts, and agent observations only when they contain real evidence.
