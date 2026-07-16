# Test and Proof Lenses

Distinguish test-code maintainability from false confidence. Prioritize smells that weaken the ability to detect real regressions.

## Oracle quality

### Weak or missing oracle

- Signal: a test executes code but makes no meaningful assertion at the behavior boundary.
- Confirm with: assertions on existence, status-only checks, snapshots with uncontrolled noise, or no check of the requested effect.
- Reject when: the command itself is a strict parser, compiler, typechecker, or invariant checker whose exit status is the intended oracle.

### Mock tautology

- Signal: the test configures a mock and then verifies only that the code returned the configured value or called the same mock.
- Confirm with: domain behavior never executes, incorrect wiring could still pass, or assertions mirror implementation steps.
- Reject when: interaction ordering or collaborator invocation is itself the explicit contract.

### Source-shape proof

- Signal: static text, file existence, or call recording stands in for observable behavior that could be exercised.
- Confirm with: the proof passes while integration, runtime, or user-facing behavior can remain broken.
- Reject when: the artifact is itself the product contract, such as a schema, manifest, generated file, or policy document.

### Happy-path monopoly

- Signal: behavior-critical branches, failure modes, boundaries, or state transitions lack pressure.
- Confirm with: incident history, uncovered contract branches, mutation survivors, or untested invalid inputs.
- Reject when: the missing paths are impossible by construction and that constraint is itself tested.

## Isolation and determinism

### Shared mutable fixture

- Signal: tests depend on state modified by other tests or reuse mutable global setup.
- Confirm with: order dependence, parallel failures, leaked database rows, or cleanup sensitivity.
- Reject when: state is immutable, transactionally isolated, or recreated deterministically.

### Timing-dependent test

- Signal: sleeps, wall-clock assumptions, race windows, or eventual behavior without bounded polling control the result.
- Confirm with: intermittent failures, environment sensitivity, or arbitrary timing margins.
- Reject when: a controlled fake clock, explicit deadline, or deterministic scheduler owns time.

### Environment-coupled test

- Signal: undeclared local services, machine state, network availability, timezone, locale, or credentials determine results.
- Confirm with: local/CI divergence or missing setup ownership.
- Reject when: the test is explicitly an integration check with declared prerequisites and isolated resources.

## Maintainability and diagnostic value

### Over-integrated test

- Signal: a broad end-to-end test is the only protection for behavior that could be localized more precisely.
- Confirm with: slow feedback, ambiguous failures, costly setup, or inability to isolate regressions.
- Reject when: the risk exists only at the real integration boundary and lower-level tests already cover local rules.

### Implementation-coupled test

- Signal: refactors that preserve behavior require widespread test rewrites because tests assert private structure or call sequence.
- Confirm with: private-method testing, excessive mocking, or assertions on incidental representation.
- Reject when: the asserted structure is a compatibility, performance, security, or interaction contract.

### Green-by-weakening

- Signal: failing tests, fixtures, or gates are deleted, skipped, broadened, or made less specific to obtain a pass.
- Confirm with: reduced contract coverage or unchanged product behavior after the test change.
- Reject when: the old assertion was demonstrably incorrect and the corrected contract is independently proved.
