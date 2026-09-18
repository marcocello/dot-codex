# Independent proof: skill portfolio consolidation

## Done

The agreed 47-entry inventory and four new owned entrypoints are discoverable from the local checkout; retired folders and live callers are gone, unrelated declarations and selected protected content remain intact, and an independent scenario-based read-through confirms the content contracts in FEATURE.md.

## Command

Run `"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture.py" --feature-dir docs/features/skill-portfolio-consolidation --timeout-seconds 120 --note "skill discovery and document contract proof"`. The dedicated runner is `proof/run.sh`; it invokes only `proof/acceptance.py`. Gate and affected regressions are separate supporting checks.

## Environment and target

Producer: the approved portfolio changes recorded in FEATURE.md and the user conversation, including retention of first-principles-clarity and provider installations. Authority: skills.toml for membership, owned SKILL.md files for routing, and existing shared engine for commands. Primary consumer: a fresh local Codex skill discovery read; affected consumers: harness links, other owned skills, and UI metadata. Target: this dot-codex checkout, using Python 3.11+ tomllib. No plugins are installed, refreshed, or invoked by this proof. External services, credentials, and UI mutation are outside the activated boundary. No fake services are used.

## Scenarios and dedicated checks

1. **Membership and preservation:** `acceptance.py` reads the preimplementation `baseline-skills.toml`, current skills.toml, and protected hashes. It requires exactly the accepted set transition from 51 to 47, unchanged unrelated declarations, retained inventory engine, Bento, ReUI and first-principles content, and an unchanged relocated anti-rhetoric reference. This catches accidental removal, extra rename, provider change, and lost retained guidance.
2. **Fresh discovery and current callers:** `acceptance.py` reads real owned skill directories, frontmatter, UI metadata, and current harness/owned skill Markdown references. It requires the four new entries and absent eight retired folders, no retired current references, and resolvable relative Markdown links. Historical feature evidence and dated reviews are excluded. This catches ghost discovery, malformed names, dangling links and stale routing.
3. **Research and writing journeys:** fixed `scenarios.json` specifies analysis/Shape research, technical prose and a recap with local validation but no screenshot or deployment. The independent proof author reads the actual routed text and records grounded scenario judgments in `evidence/semantic-review.json`.
4. **Inventory and Second Brain modes:** the same rubric requires read-only audit versus explicit additive bootstrap, source ownership, brief default versus weekly depth, unchanged schema, proposals versus confirmed state, no review-implied writes, and missing-access honesty.
5. **UI meta routing:** the same rubric evaluates critique with annotations, authorized implementation, and unavailable specialists. It requires deliberate Impeccable/ReUI selection, curated source metadata, clear lifecycle and implementation ownership, preserved read-only critique, optional catalog exploration, and component-specific handoff.

The semantic review records a PASS/FAIL, specific citations, and reasoning for every rubric group. `acceptance.py` requires all five groups and binds the evidence to SHA-256 hashes of current discovery/routing documents. The independent author must perform or repeat that review after candidate changes. The implementation agent cannot author its own semantic PASS.

## Proves

Deterministic membership, local discovery structure, live link preservation, and independently inspected instruction-level outcomes for the named scenarios. The evidence is written only after reading the complete candidate entrypoints and their relevant references; it is not inferred from keyword presence. A removed or wrongly routed central entrypoint fails the executable checks, and missing/contradictory required semantic guidance fails the read-through.

## Does not prove

The running Codex app has reloaded its cached skill catalog; an agent will reliably obey these instructions in every paraphrase; Notion or remote UI providers are available; or external actions succeed. The named acceptance boundary is documents and inventory, not a live model evaluation. Existing frozen task metadata may remain stale until fresh discovery.

## False-green risks and known gaps

Human-like semantic judgment can miss ambiguity. Hash binding guards staleness but does not establish a trusted write boundary. The independent final reviewer provides a second read-only check; it remains distinct from proof authorship. Metadata parsing is intentionally focused and is supplemented by repository gate validation. Audit-versus-sync behavior here refers to explicit instruction routing; the unchanged engine's implementation is checked separately through affected regressions. No hidden claim of semantic behavior from substring checks is made.

## Evidence method and fixed inputs

Author: `/root/proof_author`, independently delegated before implementation. Inputs: FEATURE.md and the original conversation approvals/corrections. Frozen acceptance inputs: this document, FEATURE.md, `proof/run.sh`, `proof/acceptance.py`, `proof/scenarios.json`, `proof/baseline-skills.toml`, and `proof/baseline-hashes.json`. Their initial digests are retained in `evidence/proof-inputs.json`. Semantic evidence is an output, outside frozen acceptance. Keep initial red and final captured attempts. Do not change acceptance to match implementation.
