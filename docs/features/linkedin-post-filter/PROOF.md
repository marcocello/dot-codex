# Keep or Cringe Proof

## Done

- The active skill package is structurally valid and exposes the expected binary attention-filter contract.
- Six retained item-only regressions preserve the previously verified attention filter, and four fresh current-version invocations must exercise source-agnostic item plus profile behavior without receiving expected verdicts.
- The package validator, inventory doctor, and manifest regression prove the instruction package is discoverable as `$keep-or-cringe`.
- All retained outputs use the active `KEEP|CRINGE` contract: verdict alone on the first line, explanation below it, and no em dash.
- Representative retained cases distinguish substance from tone, apply personal relevance without laundering weak evidence, and keep item and profile verdicts independent.
- Deterministic checks validate invocation provenance and case/sample/judgment integrity; a separate semantic evaluator read cases before outputs and judged whether every verdict and reason was supported.
- A fresh current-identity invocation must prove the corrected brutal voice on the exact agent-stack pressure, and a separate evaluator must reject padding, forced salvage, and personal attacks.
- A read-only browser trace and current-skill invocation must prove that an inaccessible LinkedIn URL produces a factual paste-text fallback without inventing a verdict or changing LinkedIn state.
- A current-skill invocation must discover a dummy local `SOUL.md`, use its relevant learning constraint, and omit an irrelevant private canary from the response.
- LinkedIn, X/Twitter, and blog-style profile corpora must activate the same decision policy, provide concrete examples and coverage, and avoid character judgment.
- A weak item from a useful profile and a strong item from a low-value profile must receive opposing item/profile verdicts.
- A partial two-item profile history must remain unrated.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture.py" --feature-dir docs/features/linkedin-post-filter --timeout-seconds 60 --note "verify source-agnostic content and profile filtering"
```

## Scenario: Source type does not change the attention standard

- Producer/activation: four fresh isolated agents load the current `$keep-or-cringe` skill and receive realistic LinkedIn, X/Twitter, and blog-style item plus profile corpora without expected verdicts.
- Consumer: the user deciding whether to keep the cited item and whether the broader author or publication deserves future attention.
- Read-back: retained exact responses use separate `POST` and `PROFILE` blocks, explain personal usefulness, cite two to four observed examples for rated profiles, and report corpus size plus complete, partial, or sampled coverage.
- Fake: provider pages and feed pagination are represented as bounded visible-item fixtures because social feeds are volatile and login-bound. The model decision and output are real; provider retrieval is not.
- Catches: a LinkedIn-only prompt, one generic response reused across source types, missing coverage, invented links, or profile judgment without evidence.

## Scenario: One item does not determine the profile

- Producer/activation: one LinkedIn-style case supplies an empty promotional post within an otherwise useful technical history; one X-style case supplies a strong benchmark thread within an otherwise low-value commentary history.
- Consumer: the user deciding independently whether to save the item and whether to follow the profile.
- Read-back: the first case returns `POST CRINGE` and `PROFILE KEEP`; the second returns `POST KEEP` and `PROFILE CRINGE`, each supported by corpus examples rather than tone or identity.
- Fake: profile items are explicit fixtures with dates, titles, and summaries.
- Catches: creator blacklisting from one weak post, profile halo from one excellent post, or silently forcing both verdicts to match.

## Scenario: Too little profile evidence stays unrated

- Producer/activation: a fresh current-skill invocation receives a weak blog article and only two accessible profile items with coverage explicitly marked partial.
- Consumer: the user who needs a trustworthy profile recommendation rather than false certainty.
- Read-back: the post receives `CRINGE`; the profile section states that evidence is insufficient, contains no profile `KEEP` or `CRINGE`, and reports two partial items.
- Fake: the inaccessible remainder is represented by the fixture's partial coverage marker.
- Catches: issuing a profile verdict from an undersized sample or pretending partial history is complete.

## Scenario: User examples are rejected for their actual evidence gaps

- Producer/activation: separate isolated Codex agents loaded the current `$keep-or-cringe` skill and evaluated paraphrased versions of the supplied agent-orchestration funnel and solo-revenue anecdote without seeing expected verdicts.
- Consumer: the user deciding whether either post deserves more attention.
- Read-back: retained exact consumer-visible responses contain `CRINGE` verdicts with distinct blunt reasons and no character judgment; each records the invoking agent and current skill path.
- Fake: none for pasted-text skill invocation. Live LinkedIn is not simulated.
- Catches: a generic anti-brag classifier, one canned rejection rationale, or a filter that treats a headline metric as transferable evidence.

## Scenario: The verdict is brutal without becoming personal

- Producer/activation: a fresh isolated Codex agent loads the current `$keep-or-cringe` skill and evaluates the agent-stack/course-funnel post without receiving the desired wording or verdict.
- Consumer: the user who explicitly rejected a padded four-section answer and wants super-honest, no-fluff filtering.
- Read-back: the retained exact response puts `CRINGE` alone on the first line, directly identifies the flex/withheld-value/funnel mechanism and personal attention value below it, contains no em dash, and contains no ritual `Useful kernel`, `For you`, or `Confidence` sections. A separate evaluator judges directness, accuracy, and the absence of personal attack.
- Fake: none; the pasted post and optional local context are bounded fixtures.
- Catches: consultancy-style padding, forced balance, soft euphemisms, flattering the user, or confusing brutality with insulting the author.

## Scenario: Substance survives unpleasant tone

- Producer/activation: a fresh isolated Codex agent loads the current skill and evaluates a boastful engineering post containing measurements, method, failures, and reproducible artifacts.
- Consumer: a technical builder looking for reusable implementation knowledge.
- Read-back: the retained sample keeps the post because of the evidence and method, not because of tone.
- Fake: none at the semantic boundary; the pasted post is a bounded fixture.
- Catches: dropping every confident or self-promotional post.

## Scenario: Personal attention cost changes a close decision

- Producer/activation: a fresh isolated Codex agent loads the active skill and evaluates a detailed infrastructure deep dive with explicit personal context that the topic is outside current learning priorities.
- Consumer: the user protecting a deliberately narrow learning queue.
- Read-back: the retained sample returns `CRINGE` for the high-quality but currently irrelevant post and names opportunity cost rather than low quality.
- Fake: the personal context is a minimal fixture, not the user's real private file.
- Catches: evaluating abstract post quality while ignoring the requested `soul.md` alignment.

## Scenario: Local personal context is discovered selectively

- Producer/activation: a fresh isolated Codex agent loads the active skill, treats the proof fixture directory as its workspace, discovers `SOUL.md` without receiving its contents in the prompt, and evaluates a substantive Kubernetes autoscaling post.
- Consumer: the user relying on automatic personal relevance without exposing unrelated private context.
- Read-back: the retained response returns `CRINGE` because Kubernetes is explicitly deferred this quarter; an unrelated canary present in the fixture is absent from the response. A separate evaluator checks discovery provenance, relevant use, and non-disclosure.
- Fake: the local `SOUL.md` is an explicit non-secret proof fixture, never the user's real file.
- Catches: ignoring local context, requiring the user to paste it, quoting the whole file, or leaking unrelated content.

## Scenario: Inaccessible LinkedIn links fail honestly and read-only

- Producer/activation: the in-app browser navigates directly to a deliberately nonexistent LinkedIn post URL and reads its visible removed-post status; a separate fresh agent loads the current skill and evaluates that URL with browser controls under the skill's no-mutation rule.
- Consumer: the user who supplied a URL but no post text.
- Read-back: the retained browser trace records only navigation and visible-status reading, with an empty mutation-action list; the skill response reports the inaccessible page and asks for pasted text instead of inventing a `KEEP|CRINGE` verdict.
- Fake: the URL is intentionally nonexistent so the fallback is stable; LinkedIn's real rendered error state is used rather than a mocked page.
- Catches: hallucinating post content, forcing a verdict without evidence, entering credentials, or mutating account state.

## Scenario: Author history is bounded and content-based

- Producer/activation: a retained item-only regression supplies an ambiguous teaser with a short recent-post history showing repeated pitches without disclosed methods.
- Consumer: the user deciding whether to open more posts from that author.
- Read-back: the current sample uses the observed pattern to support `CRINGE` without inferring motive, personality, or permanent author quality.
- Fake: recent-post text is a fixture because live LinkedIn is variable and login-bound.
- Catches: unbounded profile research, creator blacklisting, or psychological diagnosis.

## Scope

Proves:
- The active checkout contains the validated decision policy under the valid, discoverable `$keep-or-cringe` identity.
- The active skill instructions and UI prompt consistently expose only `KEEP|CRINGE` as verdict labels.
- The current skill is invoked independently for four source/profile pressures spanning LinkedIn, X/Twitter, and blogs; the six immediately preceding post-only outputs remain regression evidence.
- Retained samples stay joined to every case and include exact consumer-visible output, verdict, and invocation provenance.
- A separate semantic evaluator confirms each verdict, decisive pressure, direct no-fluff voice, compact output, absence of ritual sections or forced salvage, and absence of prohibited character reasoning with case-specific evidence.
- A current-identity sample and independent judgment confirm the corrected brutal voice against the user-reported miss.
- A real LinkedIn removed-post page, retained read-only action trace, and current-skill response confirm the inaccessible-link fallback without account mutation.
- A dummy local `SOUL.md`, current-skill discovery invocation, and independent judgment confirm selective relevance use without disclosure of unrelated context.
- Item and profile verdicts can disagree in both directions without cross-contamination.
- Rated profiles include two to four corpus examples and truthful coverage; an undersized partial profile remains unrated.

Does not prove:
- Authenticated rendering or exhaustive scrolling of accessible LinkedIn and X profiles, factual accuracy of arbitrary posts, or deterministic output from every future model.
- Provider-specific retrieval of complete live archives. The cross-source profile corpus is a controlled semantic fixture.
- That the user's real `soul.md` exists, is complete, or should override an explicit prompt.

False-green risks:
- Retained outputs and evaluator judgments can still be semantically generous. Fresh final review must read the cases, exact outputs, and judgments before the policy and challenge unsupported verdicts.
- LinkedIn, X, and blogs can hide, reorder, paginate, or block history; the retained browser proof covers read-only inaccessible-link behavior, while cross-source corpus retrieval remains provider-dependent.
- A package regression could leave the folder, frontmatter, UI prompt, or desired-state registry inconsistent; the current package validator, inventory regression, and doctor target those boundaries.
- A structurally short answer could still be vague or cruel. The fresh semantic evaluator must confirm it names the content failure directly while avoiding personal judgment.

Evidence method:
- deterministic current-package and inventory validation, six retained item-only regressions, four fresh current-version source/profile invocations, a real read-only inaccessible-link browser trace, dummy local-context discovery, separate evidence-first semantic evaluations, and the repository gate

Known gaps:
- authenticated full-profile retrieval, provider pagination variability, archive completeness beyond the 100-item bound, and model-output variability

## Environment

- Active dot-codex checkout using repository-local Python and the bundled skill validator.
- No credentials, network request, paid model endpoint, deployment, or external mutation.
- Runner stdout identifies the Python version and active skill path.
