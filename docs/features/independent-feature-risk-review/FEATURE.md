# Independent Feature Risk Review

## Goal
Reduce late evaluator, user, and production corrections by making pre-implementation and final review independently discover the relevant current product and system surface instead of inheriting the implementing parent's scope blind spots.

## Behavior
- For tracked and autonomous work, the parent supplies the original user goal and material corrections as verbatim excerpts together with the current feature/proof contracts and relevant current repository context.
- Contract preflight treats parent-supplied paths as discovery entry points, then independently follows current repository authority, state transitions, producers, consumers, schemas, persistence, runtime/provider boundaries, and interaction paths needed to judge the accepted outcome.
- Preflight remains one fresh, separate, bounded, read-only pass before red evidence. It reports every supported material contract/proof finding discovered in that pass; no arbitrary numeric finding cap truncates the review.
- Final evaluation treats the transient active-feature surface as an entry point rather than a scope ceiling. It independently follows current related contracts, affected consumers, authority/state paths, and real call paths needed to judge intent, architecture, behavior, and false-green risk.
- Review breadth is relevance-bounded. Preflight and evaluation do not default to repository history, accumulated dirty diffs, generated output, unrelated modules, or repository-wide sweeps.
- The accountable parent resolves supported preflight findings once, without repeating preflight as an approval gate. Evaluator findings still strengthen proof when practical, drive repair, rerun the complete proof, and require another fresh evaluator.

## Constraints
- Preserve preflight/evaluator read-only roles, one accountable parent, one active feature, serial execution, final-candidate freshness, and realistic executable proof.
- Preserve all material findings from a bounded pass; consolidate related evidence instead of stopping at a quota or the first blocker.
- Do not promote speculative adjacent behavior, style preferences, or unrelated architecture opinions into findings.
- Do not create persistent review receipts, scope manifests, hashes, scores, queue fields, or another lifecycle stage.

## Non-Goals
- A repository-wide audit for every feature.
- Repeating preflight until it returns `CLEAR`.
- Letting preflight issue an implementation or completion verdict.
- Replacing executable proof with reviewer confidence.
- Guaranteeing that probabilistic review finds every defect.
