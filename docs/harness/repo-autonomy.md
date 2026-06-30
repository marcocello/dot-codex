# Target Repo Autonomy

This harness is meant to operate on other software repos. Autofixing, autosuggestions, and auto-improving are target-repo capabilities first. Harness self-improvement is a separate outer loop.

## Autofix

Autofix means Codex repairs a concrete target-repo failure until the proof lifecycle is satisfied.

Use autofix for:

- failing primary proof;
- failing gate, lint, typecheck, build, migration, or runtime check;
- evaluator `FAIL`;
- observed green-but-broken behavior after proof passes.

Autofix changes target-repo code, tests, fixtures, setup, diagnostics, or proof artifacts as the failure owner requires. It should not change harness policy unless repeated evidence shows the harness itself caused the failure.

## Autosuggestions

Autosuggestions are repo-facing improvement proposals generated from evidence. They are not automatic code edits.

Useful inputs:

- failed proof bundles;
- repeated repair attempts;
- evaluator failures;
- weak proof-scope or proxy-validation classifications;
- missing readiness checks;
- user corrections after a claimed pass.

Use `$coding-project-improvement-review` from a target repo to produce suggestions. `scripts/harness_review` can summarize proof bundles and missing run evidence before the review, but it does not decide improvements.

Autosuggestions should route to one of these owners:

- feature/spec repair when behavior is underspecified;
- proof repair when evidence is weak;
- implementation repair when a concrete failure is reproduced;
- setup/readiness repair when local tools or services are missing;
- queue addition when the suggestion is a new product improvement;
- harness evolution only when repeated evidence shows the harness allowed the failure.

## Auto-Improve

Auto-improve means accepted suggestions become normal target-repo work: a feature, proof repair, code repair, readiness check, diagnostic, or queue item. The improvement still needs proof, gate, and evaluator before it is done.

Do not treat a suggestion as permission to silently broaden scope. If the proposal changes product behavior, create or update the relevant `FEATURE.md` and `PROOF.md`. If it only fixes a reproduced defect, use the smallest local regression proof.

Accepted learning needs a durable owner:

- project-specific behavior, architecture, or style rule -> target repo `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, or `docs/TESTING.md`;
- proof or evidence pattern -> target repo `docs/TESTING.md`, a feature proof template, or the owning `FEATURE_DIR/PROOF.md`;
- new product capability -> feature queue item or new `FEATURE.md`/`PROOF.md` pair after user acceptance;
- repeated cross-project harness lesson -> dot-codex skill, harness doc, evaluator fixture, or narrow script/test;
- stable personal preference -> memory only when explicitly requested.

## Boundary With Harness Evolution

Target-repo auto-improve asks: "What should this software repo fix or strengthen next?"

Harness evolution asks: "What should the Codex harness change so future repos do not repeat this failure?"

Most failures should stay in target-repo autofix or autosuggestion. Promote a failure to harness evolution only when the same pattern appears across runs, repos, or feature types, and when a small harness component can prevent it without weakening safety or proof quality.
