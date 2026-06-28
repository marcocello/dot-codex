# Proof Lifecycle

This document holds the detailed proof policy. `AGENTS.md` keeps only the hard operating
contract.

## Contract Split

- `FEATURE.md` describes the product behavior.
- `PROOF.md` describes how completion is proven.
- Proof commands, fixtures, environment notes, and evidence stay out of `FEATURE.md`.
- Non-trivial features need one primary proof command plus at least one executable proof
  artifact.

## Primary Proof

The primary proof should exercise the public boundary that matters:

- API proof calls the route or app client and checks response, state, and side effects.
- UI proof renders or drives the UI and checks visible state or interaction.
- Provider proof uses realistic payloads and prefers safe live read-back when credentials and
  targets exist.
- Bug-fix proof starts as the smallest regression that fails before the fix.

Static source checks, string searches, lint, typecheck, and unit tests can support proof, but
they do not replace the primary proof for user-visible behavior.

## Evidence Bundle

For serious feature, issue, UI, API, provider, or workflow proof runs, proof artifacts should
write a run evidence bundle when practical:

```text
FEATURE_DIR/proof/runs/<timestamp>/
  command.txt
  stdout.txt
  stderr.txt
  result.json
  screenshots/
  logs/
  provider-readback.json
  notes.md
```

Only create files that have real evidence. Do not fabricate empty screenshots, logs, or
provider read-back.

Minimum useful bundle:

- `command.txt`: exact primary proof command.
- `stdout.txt` and `stderr.txt`: bounded command output.
- `result.json`: machine-readable status, timestamps, and important evidence paths.
- `notes.md`: short human summary of what was proven and what remained unavailable.

For browser proof, include screenshots or video paths when the browser tool can capture them.
For provider proof, include read-back output or a clear manual gap when live state is unavailable.
For local app proof, include relevant recent logs, not full noisy logs.

When the proof can be executed as a local command, wrap it with:

```bash
scripts/proof_run_capture --feature-dir FEATURE_DIR -- <primary proof command>
```

The helper writes the evidence bundle and exits with the wrapped command's exit code. Proof
runners may still write richer browser, provider, or app-specific files into the same bundle
when the helper is too small for the whole scenario.

## Anti-Gaming Review

`PROOF.md` must name fake or incomplete implementations that could otherwise pass. Each fake
pass risk should map to a concrete proof step. If the proof cannot catch a plausible fake,
strengthen the proof before implementation starts.

## Proof Change Guard

After implementation code changes begin, do not edit `FEATURE.md`, `PROOF.md`, or proof
artifacts in the same pass. If the proof is wrong:

1. Stop implementation.
2. Return to contract repair.
3. Record why the old proof was wrong.
4. Add the new failing proof or evidence requirement.
5. Restart implementation only after the strengthened proof fails for the right reason.
