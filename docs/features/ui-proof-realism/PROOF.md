# UI Proof Realism Proof

## Done
- UI proof distinguishes browser actions from synthetic event dispatch.
- Loaded resources require decoded and visible browser state.
- Domain behavior uses the real application API while presentation fixtures remain allowed.
- Proof authoring routes UI work to this profile, and the oracle rejects a representative source-only weakened policy.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/ui-proof-realism --timeout-seconds 30 --note "verify realistic UI proof boundaries"
```

## Scenario: UI claims use the owning boundary
- Producer/activation: pytest reads the active UI proof profile.
- Consumer: proof authoring for interaction, resource, or domain-behavior claims.
- Read-back: proof authoring routes UI work to this profile; policy requires genuine browser actions, rejects handler calls and synthetic dispatch, requires loaded/decoded/visible resources, and crosses the real protected API plus normal authorization to visible/durable read-back while only unsafe outer providers may be faked.
- Fake: presentation-only state fixtures and unsafe outer-provider fakes.
- Catches: synthetic clicks that miss hangs, valid image URLs that never render, and UI fixtures that advertise unavailable domain behavior.

## Scope
Proves:
- The current UI proof profile rejects the observed false-green patterns.

Does not prove:
- Product-specific browser proof quality.
- Future model compliance.

False-green risks:
- Static policy can be misapplied; feature evaluation must challenge each concrete UI proof.

Evidence method:
- deterministic

Known gaps:
- Live adherence remains probabilistic.

## Environment
- Repository-local Python and pytest; no browser, network, or external mutation is required because the claimed artifact is the proof policy itself.
