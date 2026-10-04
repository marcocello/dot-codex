# Designing and challenging acceptance

Use the relevant example when authoring or checking an unfamiliar proof boundary. These are techniques, not additional lifecycle stages; [proof.md](proof.md) owns the rules.

## Acceptance Author

Start from the accepted outcome and original user context. Identify how a real user or consumer activates it, where its authoritative result lives, and how a separate observation can contradict a false success. Inspect enough implementation to find those boundaries without deriving expected results from the candidate.

Choose the smallest realistic proof that would fail for a plausible incomplete implementation. Explain what it establishes and leaves unknown. Use established test infrastructure; do not build a bespoke framework when a process invocation, browser interaction, and read-back suffice. Exercise uncertain helpers before long runs. Return product ambiguity to Product Partner rather than choosing the easiest oracle.

Keep the contract, runnable command, prerequisites and gaps with the check; hand them over only when work is delegated. The same agent can author and implement. Expected outcomes must come from the spec and external observations, not from copying implementation assumptions. Preserve original failures and reasons for test corrections.

## Final Reviewer

Start with the original request/corrections and form an expectation of the ordinary user outcome before reading completion summaries and PASS results. Then inspect the accepted feature, changed surface, proof boundary, results, and repairs. Follow the highest-consequence shared assumption to independent source or consumer evidence; agreement between specification, fixture, and implementation is not corroboration. Challenge the completion claim against the tested candidate and target:

- Which ordinary promised action could still fail while every assertion passes?
- Did proof activate the real path and observe the authoritative result? Could a fake, prefilled state, stale build, or shared implementation assumption hide the defect?
- Did implementation or proof repair change the accepted meaning? Does a separate product choice remain unsupported?
- Does every accepted feature criterion map to appropriate evidence, including failure/permission checks a happy journey would miss? Are scoped inputs complete enough to justify reusing unchanged checks, and were shared integration risks exercised on the combined candidate?
- Are relevant regressions and the reviewed files current? Does the evidence establish local behavior, a live target, or only a narrower prerequisite?

State evidence-backed blockers and demonstrated limits, keeping stylistic preferences optional. A delegated reviewer stays read-only; the implementing agent handles repairs and records the result. Passing output is evidence to assess, not a verdict to echo.

## Boundary Examples

| Promised outcome | Useful activation and independent read-back | False confidence to challenge |
| --- | --- | --- |
| Save a customer | Normal authenticated API or UI; reload and read the authoritative store | Handler returns success but transaction never commits |
| Provider delivery | Normal producer; authorized sandbox provider read-back and consumer result | Adapter returns an invented ID; local queue acceptance mistaken for delivery |
| Worker processing | Start the actual worker, submit input, observe durable result and relevant retry behavior | Calling an internal function bypasses scheduling, configuration, or persistence |
| Local startup | Run the documented default command in its actual terminal/process mode; check readiness and shutdown | Detached-only smoke test misses an attached-terminal failure |
| UI feature | Real browser actions, persisted result after reload, appropriate permissions and failure state | Screenshot or direct handler invocation skips actual interaction |
| Generated report/export | Invoke normal generation/download and inspect meaningful content and format | File existence or HTTP 200 accepts empty or incorrect output |
| First-use automation | Begin without saved preferences and observe a useful permitted result | Prefilled fixtures hide the missing selection or fallback policy |
| Refactor | Exercise the preserved public contract or invariant through affected consumers | Snapshot of private structure rewards the rewrite without checking equivalence |
| Harness instruction change | Fresh task execution with raw context and withheld expectations | Retained text judgments or heading checks presented as actual agent behavior |

Select relevant error/recovery cases from the promise. These examples are neither a quota nor a reason to expand a narrow feature. For provider variability or sampled model behavior, explain the sampling limit rather than turning one pass into a reliability claim.
