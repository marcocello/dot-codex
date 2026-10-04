# Completion supported by current evidence

## Outcome

A new feature completion cannot use proof from an earlier application state or omit the independent final review. Historical acceptance remains historical rather than becoming an assertion that every old feature still passes today.

## Accepted behavior

- Capture retains a deterministic fingerprint of the current repository candidate, including tracked and non-ignored untracked files and deletions, plus the owning acceptance inputs. It records scope and target. Generated evidence directories and lifecycle status are excluded so capture and status writes do not invalidate themselves. Ignored runtime/configuration, external services, and arbitrary transient edits remain explicit observation limits. No raw source or secret values are added to capture output.
- Proof and regression capture preserve existing CLI, timeout, interruption, output separation, process cleanup, selected snapshot protection, and retained failures. A nominally passing command that changes the observed candidate during execution becomes FAIL. Missing or invalid fingerprints cannot qualify as current evidence.
- A small receipt command records the actual final review verdict, distinct implementer/acceptance-author/reviewer identifiers, concise rationale, named proof and selected regression runs, their digests, and the tested target. It rejects nonpassing/stale/mismatched evidence when recording PASS. Recording identifiers is attribution, not authentication or a substitute for review.
- `feature_status.py` rejects a new transition to done unless the newest owning official proof passed, has a valid unchanged candidate fingerprint, and has a matching PASS review receipt with passing current supporting runs. Source/test/fixture edits, additions/deletions, a newer failed or unfinished proof, regression substitution, or altered bound evidence prevent completion. Rejected transitions leave status unchanged.
- Existing done entries remain interpretable under their historical format; reading the status inventory must not require rerunning all history against today's checkout. Every new done transition, including a reopened historical feature, must satisfy the new contract. Historical evidence is not current regression assurance.
- Draft registration permits a nonempty FEATURE without placeholder PROOF/runner files. Ready/active require nonempty FEATURE and PROOF plus an executable runner. These checks establish structural readiness only; semantic discovery and independent authorship remain accountable judgments.
- Document exact commands and limits. Do not introduce a rigid project configuration, a service, compulsory source commits, automatic terminal surveillance, or falsely claim sandbox-enforced acceptance isolation.

## Verification and boundaries

Use real installed capture, receipt, and status CLI subprocesses in disposable repositories. Prove successful completion, stale-after-edit rejection, edits during passing proof, acceptance/helper changes, altered evidence/receipt, regression handling, historical inventory compatibility, draft-to-ready structure, ownership preservation, and failure retention. Keep tests under this feature and never replace production consumers with mocks. Review code and instructions independently before final completion.
