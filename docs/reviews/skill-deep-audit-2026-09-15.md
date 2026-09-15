# Detailed Skill Portfolio Audit

Date: 2026-09-15. Recommendations only. This supersedes the earlier review's recommendations where explicitly stated; it does not undo completed consolidations or authorize more changes.

## Main conclusion

The inventory mixes five different things: reusable domain workflows, personal style profiles, project-specific procedures, integrations, and bundled applications. Treating every difference in output as a reason for a separate skill preserved too many entrypoints in the earlier review. Several capabilities can remain callable as modes while sharing one entrypoint. Conversely, provider modules are often useful subdivisions of one plugin, not independent packages that should be manually consolidated.

The strongest concrete defect is in the local Second Brain API helper. The strongest consolidation candidates are writing modes, the two signal skills, job source selection plus vacancy search, and the four Second Brain workflow/helper entrypoints. The TWYD kit builder belongs with its product. Keep first-principles-clarity and the UI meta toolkit as explicitly requested. Do not uninstall Codex-managed ClickUp or Sites.

## What was inspected and what usage means

- All 47 current declarations: 38 owned skills, 2 externally sourced standalone skills, and 7 plugin declarations.
- Owned SKILL.md content across this task, relevant supporting references and selected executable helpers; current callers and metadata were mapped. File counts below exclude Python bytecode.
- 50 recent app task/chat summaries, including 36 Codex tasks; all 77 archived local task summaries available through the archive pagination. Thus 113 Codex task summaries were sampled, plus 14 ChatGPT conversation summaries. The non-archived list is capped, so this is not a complete lifetime history or an invocation telemetry dataset.
- Selected turns in seven relevant tasks were inspected through the supported task reader. No raw session-directory parsing, private note scraping, live Notion request, credential read, or external mutation was performed.
- Provider-owned entries are reviewed at capability/routing level with selected entrypoint passages, not every helper/reference or live integration. Each exposed provider skill is individually listed in the appendix; no claim of comprehensive runtime testing is made.

Usage labels:

- **V — observed use:** an explicit invocation, skill-file read, or this task's actual use was observed. It does not automatically establish successful completion.
- **L — loaded:** the skill was read, but execution/completion of its integration is not established.
- **S — summary signal:** task summaries indicate relevant demand; exact skill execution is not verified.
- **C — newly consolidated:** created and inspected in this task, with no post-consolidation real-world use observed.
- **P — explicit preference:** the user deliberately asked to retain/select it; no further retention question is needed.
- **N — no use observed in this sample:** unknown lifetime use. Never translate this to 'unused'.

A reference in a SKILL.md is a dependency hint, not evidence of execution. A feature package is evidence that a skill/harness was developed, not that users use it. A healthy doctor result establishes inventory consistency, not operational readiness. Lack of scripts does not imply low value; unique domain judgment and personal examples also matter.

## Verified usage samples

- `run-job-search`: **RESEARCH: Offerte di lavoro e aggiornamento CSV**, task `01a09ee4-405b-71f3-84e8-270f529af603`. Explicit invocation or skill file read observed; final response inspected.
- `second-brain-capture-interactions`: **Capture Codex interactions**, task `01a08b32-6af5-7523-8491-b437b23c19eb`. Explicit invocation or skill file read observed; final response inspected.
- `impeccable`: **RESEARCH: Shape an AI dispute resolution platform (2)**, task `01a0719b-8e20-7702-80d4-d02ec83b0f22`. Explicit user request; completion not established in sampled turns.
- `reui`: **FEAT: build audit log data grid**, task `01a02b2b-33d3-7770-805f-4d6a7b8972ec`. Explicit user request; completion not established in sampled turns.
- `coding-commit`: **CHORE: commit repository changes**, task `01a0a48b-8dbd-7783-abd2-1630a3f66762`. Explicit invocation or skill file read observed; final response inspected.
- `write-product-posts`: **DOCS: Draft Skill Registry launch post**, task `01a05c24-6bb6-7e51-921a-9e348999ca2e`. Explicit invocation or skill file read observed; final response inspected.
- `build-professional-profile`: **REVIEW: LinkedIn builder positioning**, task `01a09034-7bb6-7ba1-ac0d-87bc3d084aa7`. Explicit invocation or skill file read observed; final response inspected.

ReUI and Impeccable requests were explicit in inspected turns. Job search, product-post writing, profile building, commit, and interaction capture also had direct evidence. ClickUp has recent task-backed demand in summaries, so the earlier unused-candidate suggestion is withdrawn. Only selected turn content was inspected; no total invocation counts are claimed.

## Prioritized actions

| Priority | Action | Why |
|---|---|---|
| 1 | Repair or retire the Second Brain API fallback | Placeholder IDs, no CLI update route, and incomplete list pagination undermine the workflows above it. |
| 2 | Merge casual rewriting and customer requirements into writing modes | They add voice/templates to the same evidence-and-writing operation. Preserve mode-specific output and facts. |
| 3 | Merge signal context and detection into sales-signals | One context file, one store, already mutually connected; retain context-only mode. |
| 4 | Merge source curation into career-search-jobs | Same dossier and criteria; retain sources-only and scan modes and existing artifacts. |
| 5 | Consolidate Second Brain capture/sweep/review with the transport helper underneath | One schema and system; clearer read/write modes and fewer drifting copies of rules. |
| 6 | Move TWYD kit-building guidance to its product owner | High value but product-specific paths, protocols, and runtime proof are poor global defaults. |
| 7 | Consider one coding-review with code and architecture lenses | Large overlap in acquisition/evidence/prioritization; preserve specialized references and outputs. |
| 8 | Narrow generic triggers and rigid defaults | Frontend starter, generic Python backend triggers, Markdown 'second brain', fixed writing rhythm, and campaign setup gates can misroute work. |

Illustration, not a target: the writing merges (-2), signals merge (-1), career sources merge (-1), four-to-one Second Brain merge (-3), code-review merge (-1), and moving the TWYD skill out of global inventory (-1) would reduce 47 to 38 global declarations while preserving capabilities. Project relocation must happen before global removal. No provider uninstall is included. Optional PHP-family consolidation is a separate decision, not necessary to reach a quota.

## Concrete defects and conflicts

### Second Brain helper is present but not operationally configured

`skills/second-brain-notion-api/scripts/notion_secondbrain.py:17` defines literal placeholder data-source IDs. List/create operations use those constants; the inspected parser provides no ID override. Merely telling the agent to resolve live IDs cannot configure this helper without changing its source or introducing an override mechanism.

At line 162, `list_rows` requests a single page (default 25). It neither continues pagination nor returns the provider's `has_more` and `next_cursor` in its compact response. A reviewer could mistake a partial set for complete current state. At line 195, `update_page` exists, but the parser at lines 242–266 exposes only list/create-task/create-deal/create-idea.

An offline import and stubbed `api_request` probe confirmed the literal placeholder query path, one request, omission of pagination fields, and the four-command CLI. No network call or token read occurred. This establishes local behavior, not whether a separate Notion connector is currently functional.

### Claims and processes that need narrower scope

- `casual-message-rewriter/SKILL.md:32` says to summarize long source material despite promising unchanged meaning. Preserve material commitments and qualifiers unless asked to summarize.
- `customer-tech-requirements/SKILL.md:40` offers 50 GB as a baseline without workload evidence; its reference also supplies CPU/RAM figures. Examples must not silently become customer requirements.
- `create-cli-toolkit-kit/SKILL.md:15` still uses 'standard or sensitive' feature terminology and a specific product/runtime layout. The validator command at line 86 assumes the skill's scripts directory is available relative to cwd.
- `second-brain-capture-interactions/SKILL.md:3` says current-task default; the body chooses project-wide synchronization without an argument. This is a real scope conflict needing a deliberate behavior decision.
- `prospecting-linkedin-content-manager/references/linkedin-algorithm.md:16` and `:101` assert comment multipliers and link reach penalties without supporting citations in that file. This audit identifies missing grounding; it does not verify the current algorithm.
- The campaign manager's Topics mode requires a strategy file, and its post mode defaults to a large content package. Those dependencies are disproportionate for one topic or one post.
- `writing-technical-content/references/anti-ai-rhetoric.md` prescribes numeric sentence-length proportions. That preserved reference is not a good universal rule for short messages, requirements, or natural prose.
- `coding-frontend` mandates an admin starter for broad greenfield UI requests; `coding-python-backend` includes language-agnostic backend triggers. These can choose a solution before the stack/product need is established.
- Generic Notion capture/spec skills can create additional pages/task structures, while Second Brain and coding-workflow have their own schema/status authority. Define the destination and authoritative contract before selecting a workflow.
- The Google Drive router's blanket DOCX-first instruction and Google Docs' native-template-aware route are not identical. Use the specialized current file-route contract; do not flatten native multi-tab/template semantics for consistency with a generic router.

## Every declared dependency

### 1. capture-note

**Decision:** Conditional keep as knowledge-capture-markdown. **Usage:** N.

**What it adds:** Captures Markdown notes while preserving collection filenames, frontmatter, and append/create conventions. Its useful invariant is preservation of the destination collection, not generic summarization.

**Overlap:** Overlaps with Second Brain capture and Notion knowledge capture at the input stage, but writes to a different system. A destination distinction is real; it does not necessarily require a 79-line standalone workflow.

**Recommended change:** Keep only if Markdown is an intentional destination. Remove the generic 'second brain' trigger and reduce the entrypoint to destination discovery, preservation, and a receipt. If all organized capture now goes to Notion, retire this skill rather than add another knowledge router.

**Evidence and limits:** No scripts or supporting references; no explicit usage found in the sampled tasks. That is a deletion candidate to discuss, not proof of non-use.

**Local footprint:** 79 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/capture-note/SKILL.md).

### 2. casual-message-rewriter

**Decision:** Merge into writing-technical-content as message mode. **Usage:** N.

**What it adds:** Rewrites DMs, chat, email snippets, and spoken notes in your conversational voice. It has style examples and three degrees of casualness, but no distinct data source, state, or tool contract.

**Overlap:** The general writing skill already handles intent, audience, evidence, language, and revision. This skill's incremental content is a voice profile; preserving that as a reference retains the capability without another top-level entry.

**Recommended change:** Add a clearly described message-rewrite mode and move casualness examples into a reference. Preserve one-version/no-explanation output. Do not apply technical-essay structure or the anti-rhetoric sentence-length quotas to short messages.

**Evidence and limits:** Line 32 tells the agent to summarize long input while the description promises unchanged meaning. Explicitly preserve commitments, qualifiers, names, and dates unless summarization is requested. Earlier advice to keep it separate was more conservative than the actual boundary requires.

**Local footprint:** 68 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/casual-message-rewriter/SKILL.md).

### 3. coding-antipattern-review

**Decision:** Merge with architecture review into coding-review. **Usage:** N.

**What it adds:** Reviews recurring code, runtime, architecture, and proof weaknesses; its strongest differentiator is actively checking counter-evidence and rejecting harmless pattern matches.

**Overlap:** Its scope overlaps heavily with coding-architecture-deep-dive: both map boundaries, trace behavior, identify consequences, rank evidence, and recommend the smallest correction. Distinct lenses can live behind one read-only review entrypoint.

**Recommended change:** Use code-quality and architecture modes with separate references. Preserve the anti-pattern catalogs, confirmed/suspected/rejected distinctions, and function-maintainability lens. Keep workflow retrospectives separate because their evidence is historical runs rather than just current source.

**Evidence and limits:** No direct invocation verified in the sample. No inbound mention from another owned SKILL.md is not a defect: direct discovery may be intentional. Merge for duplicated selection/analysis, not for a fabricated usage claim.

**Local footprint:** 108 entrypoint lines, 5 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/coding-antipattern-review/SKILL.md).

### 4. coding-app-improvement-review

**Decision:** Keep as coding-review-workflow. **Usage:** S.

**What it adds:** Reviews actual coding runs, proof attempts, user corrections, and harness friction. It distinguishes project defects from proof, harness, preference, and one-off lessons.

**Overlap:** Shares evidence language with code review, but answers a different question: why the delivery process succeeded or failed. It should consume existing captured dialogue rather than create another store or reissue completion.

**Recommended change:** Keep the retrospective capability, shorten repeated lifecycle prose, and improve the name. Route only deliberate retrospectives or concrete recurring friction here; an ordinary code review should not load it.

**Evidence and limits:** Archived task 'REVIEW: Find harness interaction gaps' explicitly names this skill in its summary. This is a usage signal, not a verified successful invocation. Evidence availability determines whether the retrospective is useful.

**Local footprint:** 104 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/coding-app-improvement-review/SKILL.md).

### 5. coding-architecture-deep-dive

**Decision:** Merge with anti-pattern review into coding-review. **Usage:** N.

**What it adds:** Assesses components, contracts, data flow, state, workload limits, migration, and current-versus-reference choices. KEEP/PARTIAL ADOPT/REPLACE is its distinctive decision output.

**Overlap:** The review acquisition, evidence, counterexample, prioritization, and minimal-correction steps duplicate the anti-pattern reviewer. The architecture mode adds workload and migration analysis rather than a new integration.

**Recommended change:** Retain architecture/reference-comparison as a mode with its own guide. Generic 'review this module' can then route inside one skill, avoiding competing discovery descriptions.

**Evidence and limits:** Related architecture tasks appear in history, but the inspected turns do not establish use of this exact skill. Do not infer invocation merely from a task title containing architecture.

**Local footprint:** 106 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/coding-architecture-deep-dive/SKILL.md).

### 6. coding-commit

**Decision:** Keep; shorten repetitive instructions. **Usage:** V.

**What it adds:** Owns stage selection, coherent local commits, Conventional Commit messages, ignored paths, and explicit versus unscoped commit requests. These are consequential personal workflow preferences.

**Overlap:** Overlaps with general Git abilities and developer instructions, but actual stage-selection rules are nontrivial and repeatedly exercised. It should stay independent of feature completion and deployment.

**Recommended change:** Keep one compact authoritative scope algorithm, one commit procedure, and concise examples. Remove repeated restatements of 'never push', staged-set preservation, and grouping rules where they add no new condition.

**Evidence and limits:** Verified explicit invocation and skill-file read in 'CHORE: commit repository changes'; the task reported local commits. A skill-file read for secret audit was also observed there, but that alone does not establish successful scanning.

**Local footprint:** 126 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/coding-commit/SKILL.md).

### 7. coding-workflow

**Decision:** Keep as the engineering lifecycle owner. **Usage:** V.

**What it adds:** Owns Shape/Ship/Fix/Analyze/Operate, feature contracts, independent proof, status, capture, and final review. Twelve other owned entrypoints explicitly reference it.

**Overlap:** Some lifecycle prose is repeated in domain skills, and Notion spec-to-implementation offers a competing plan/task lifecycle. The current root instructions also risk applying coding workflow to non-engineering tasks.

**Recommended change:** Centralize lifecycle rules here and leave only domain-specific proof boundaries in stack skills. Define one authority when a source spec comes from Notion. Review the Goal permission requirement separately; it caused an additional approval during this consolidation.

**Evidence and limits:** Used in this task. The independently verified prior consolidation proves a local document/inventory contract, not universal agent adherence. More files or mandatory stages do not by themselves establish stronger behavior.

**Local footprint:** 51 entrypoint lines, 10 reference files, 1 script files; 12 other owned entrypoints mention this name. [Source](../../skills/coding-workflow/SKILL.md).

### 8. coding-frontend

**Decision:** Keep with narrower defaults. **Usage:** V.

**What it adds:** Owns React/Next.js source organization, UI implementation, design-system reuse, and greenfield structure. Historical task inspection shows the skill was read during a ReUI request.

**Overlap:** Impeccable, ReUI, Sites, and the UI toolkit also attract frontend requests. Their responsibilities must remain design technique, components, platform, and selection respectively; none should compete to own every frontend task.

**Recommended change:** Use the toolkit only for unresolved UI approach selection. Restrict the compulsory shadcn-admin clone to suitable admin/dashboard work. Preserve explicit Next.js or existing architecture rather than letting generic UI wording choose a starter.

**Evidence and limits:** The skill combines React/Next.js scope with a compulsory admin starter and broad 'feature affects UI' triggers. That can choose an unsuitable stack/product shape. This is a concrete routing risk, not evidence that frontend skills should be deleted.

**Local footprint:** 66 entrypoint lines, 0 reference files, 0 script files; 2 other owned entrypoints mention this name. [Source](../../skills/coding-frontend/SKILL.md).

### 9. coding-laravel-feature-builder

**Decision:** Keep for Laravel; optional later PHP-family consolidation. **Usage:** N.

**What it adds:** Provides Laravel request validation, policies, model events, jobs, cache, migration, and PHPUnit/Pest conventions. It is short and framework-specific.

**Overlap:** Shares setup and generic safe-change guidance with plain PHP and WordPress. Most overlap is reusable PHP hygiene, while framework execution boundaries differ.

**Recommended change:** If PHP work is occasional, use coding-php with Laravel/plain-PHP/WordPress mode references. Otherwise keep coding-laravel as a precise trigger and remove duplicated lifecycle text. Do not merge it into Python or a generic backend skill.

**Evidence and limits:** No exact use established in the sampled tasks. Absence from recent activity can indicate a seasonal stack rather than useless content. The choice is convenience versus discovery count, not lost framework capability.

**Local footprint:** 52 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/coding-laravel-feature-builder/SKILL.md).

### 10. coding-php-legacy-maintainer

**Decision:** Keep conditionally; candidate mode of coding-php. **Usage:** N.

**What it adds:** Focuses on plain PHP, include chains, globals, extensions, compatibility, and containment without framework rewrites.

**Overlap:** Much of its 56 lines is generic inspect/minimal-fix/test guidance. Its unique part is upgrade and bootstrap risk in framework-light applications; Laravel/WordPress skills already cover their own versions of this.

**Recommended change:** If you still maintain plain PHP, preserve the compatibility and include-chain lens. It can be a mode/reference of one PHP-family skill when reducing top-level choices is valuable.

**Evidence and limits:** No exact use established. A WordPress entrypoint references it, so removal requires updating that route even if no user invocation appears. Static references show dependency intent, not runtime usage.

**Local footprint:** 56 entrypoint lines, 0 reference files, 0 script files; 1 other owned entrypoints mention this name. [Source](../../skills/coding-php-legacy-maintainer/SKILL.md).

### 11. coding-prepare-environment

**Decision:** Keep as shared setup support. **Usage:** V.

**What it adds:** Owns environment detection, project-native setup, command prefixes, ignore rules, and a VS Code tasks generator. Five stack entrypoints refer to it.

**Overlap:** Stack skills correctly delegate readiness here. Overlap becomes harmful when setup rewrites repository conventions or imposes generated tasks on a task that only needs an existing command.

**Recommended change:** Keep scripts and minimal readiness checks. Separate your new-project defaults from repairs in existing projects. Reconsider mandatory whitelist-style gitignore for every new repository and default ngrok run tasks if those are not universal preferences.

**Evidence and limits:** Its SKILL.md was read in the inspected ReUI coding task. Related setup tasks also exist. Generator support makes this more than generic advice, but the presence of a generator does not prove every generated task is appropriate.

**Local footprint:** 103 entrypoint lines, 1 reference files, 1 script files; 5 other owned entrypoints mention this name. [Source](../../skills/coding-prepare-environment/SKILL.md).

### 12. coding-python-backend

**Decision:** Keep; narrow language selection. **Usage:** N.

**What it adds:** Provides Python API/service/domain/persistence boundaries, pytest expectations, and a backend/app default.

**Overlap:** Generic backend and endpoint triggers overlap with Laravel, WordPress REST, and other stacks. The actual Python-specific implementation boundary is useful once the stack is established.

**Recommended change:** Require a detected or explicitly selected Python context. Keep existing repository structure primary, and express layered architecture proportionally rather than forcing extra layers around trivial endpoints.

**Evidence and limits:** No exact invocation verified in sampled turns. Backend-related tasks are not enough to prove this skill ran. Its operational relevance is plausible but distinct from observed usage.

**Local footprint:** 52 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/coding-python-backend/SKILL.md).

### 13. coding-secret-audit

**Decision:** Keep as specialized audit, with scope clarity. **Usage:** L.

**What it adds:** Has a deterministic GitGuardian runner plus personal-information scanning, repository visibility policy, and credential handling. It adds executable behavior beyond a writing checklist.

**Overlap:** Touches commit and publish flows but is explicitly a supporting audit, not a mandatory coding stage. General code review cannot substitute for provider-backed secret detection.

**Recommended change:** Keep the callable audit. Make receipts explicit about skipped binary/oversized files, checkout-only coverage, and unavailable provider checks. Show exact personal values only as needed and within the user's requested audit context.

**Evidence and limits:** A read of this skill was observed in a commit task; successful scanner execution was not established. Inventory health cannot prove authentication, provider reachability, or comprehensive historical secret coverage.

**Local footprint:** 94 entrypoint lines, 0 reference files, 2 script files; 0 other owned entrypoints mention this name. [Source](../../skills/coding-secret-audit/SKILL.md).

### 14. coding-wordpress

**Decision:** Keep for WordPress; optional PHP-family mode. **Usage:** N.

**What it adds:** Preserves WordPress hooks, nonces, capabilities, plugin/theme separation, Bedrock variants, WooCommerce, and ecosystem-specific validation.

**Overlap:** Shares generic PHP setup and testing with the other PHP skills, but its runtime security and layout conventions are distinct. It should not select generic React frontend patterns for Gutenberg/theme work automatically.

**Recommended change:** Keep or place its detailed rules in a coding-php WordPress mode. Reconsider forcing wordpress/app in every greenfield plugin-only repository; a distributable plugin may need a package-root layout.

**Evidence and limits:** No exact recent use verified. Retaining the capability is justified if WordPress remains in your work mix, but global discoverability is a preference rather than evidence of present use.

**Local footprint:** 56 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/coding-wordpress/SKILL.md).

### 15. customer-tech-requirements

**Decision:** Merge into writing-technical-content as requirements mode. **Usage:** N.

**What it adds:** Turns source material and repository context into customer prerequisites, customer/vendor responsibilities, and separate internal delivery gaps. The ownership split is useful and should survive.

**Overlap:** It overlaps with technical writing in audience, evidence, concise prose, factual grounding, and delivery. Its specific contribution is an output template and inspection checklist, not a separate tool integration.

**Recommended change:** Move its customer-facing/internal-risk patterns into a requirements reference, with a clear mode trigger. Let Documents/Google Docs own the file mechanics when requested. Avoid importing article-style narrative or fixed prose rhythm into requirements.

**Evidence and limits:** The 50 GB/4 vCPU/16 GB examples can become unsupported promises if treated as defaults. Label sizing assumptions and tie them to workload evidence. Earlier recommendation to keep a separate entrypoint overstated the need for separation.

**Local footprint:** 58 entrypoint lines, 1 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/customer-tech-requirements/SKILL.md).

### 16. create-cli-toolkit-kit

**Decision:** Move to TWYD project ownership. **Usage:** N.

**What it adds:** Builds deterministic tool archives for a specific Portal/Admin/Team/Coworker/MCP runtime. The adapter, archive, data-isolation, and provenance rules are substantial.

**Overlap:** The overlap with generic Python coding is appropriate composition; the real issue is that the supposed global skill hardcodes one product's runtime layout and integration sequence.

**Recommended change:** Keep the capability in the repository or provider kit that owns that runtime. Use coding-build-cli-toolkit-kit if it must remain global, but make product scope conspicuous. Preserve validator and proof rules with their owner.

**Evidence and limits:** The entrypoint names backend/cli_toolkit_runtime/runtime.py, business_logic_modules, and the older 'standard or sensitive' lifecycle terminology. Its relative validator command also assumes the skill directory is cwd. No exact skill invocation was verified; current TWYD work alone does not prove this kit workflow remains active.

**Local footprint:** 119 entrypoint lines, 2 reference files, 1 script files; 0 other owned entrypoints mention this name. [Source](../../skills/create-cli-toolkit-kit/SKILL.md).

### 17. drawio-diagram-design

**Decision:** Keep if editable diagrams are a deliverable. **Usage:** N.

**What it adds:** Produces native editable mxGraphModel cells with a deterministic builder and geometry validator. Its file format and editability contract distinguish it from raster generation and generic explanation diagrams.

**Overlap:** Visualize can explain structures; Mermaid can express simple static graphs; Impeccable can advise appearance. None automatically preserves Draw.io editing semantics.

**Recommended change:** Keep as diagram-build-drawio when .drawio delivery matters. Use a simpler diagram path when no editable source is needed. Make source-style preservation the default for ordinary edits and reserve the imposed visual grammar for requested redesign.

**Evidence and limits:** No exact invocation found in the sample. Its builder/validator are substantive assets; assess artifact demand before removing them. Its hard node budget and style gate can overconstrain diagrams with legitimate complexity.

**Local footprint:** 85 entrypoint lines, 4 reference files, 2 script files; 0 other owned entrypoints mention this name. [Source](../../skills/drawio-diagram-design/SKILL.md).

### 18. first-principles-clarity

**Decision:** Keep as requested. **Usage:** P.

**What it adds:** Provides a deliberate assumption-testing and decision format, including competing explanations, evidence confidence, disconfirmation, and reversible tests.

**Overlap:** Large portions overlap with ordinary good reasoning and code/architecture review. The justified distinct role is an explicitly desired thinking framework, not a superior source of facts.

**Recommended change:** Keep membership and the recognizable invocation. Simplify celebrity framing, fixed explanation counts, and ego-audit requirements when unrelated to the decision. Prefer proportionate depth.

**Evidence and limits:** The user explicitly asked to keep it in this task. That preference outranks speculative usage-based deletion; no further retention question is needed.

**Local footprint:** 136 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/first-principles-clarity/SKILL.md).

### 19. launch-photo-drop

**Decision:** Keep as a utility; consider separate package ownership. **Usage:** N.

**What it adds:** Runs a bundled upload/gallery application, manages authentication discovery, local storage, a temporary public tunnel, status, and shutdown. Seven scripts support this lifecycle.

**Overlap:** Sites could build a portal, but that would replace a working application with a new build. A generic file-sharing instruction is not an equivalent runtime.

**Recommended change:** Keep as event-photo-drop if this is a desired event utility. A personal plugin/package could own the app and runtime while exposing one short skill. Separate app maintenance from launching an event.

**Evidence and limits:** No event launch verified in the sampled history. This is an occasional-use executable asset, so infrequency alone is a poor deletion criterion. Remove only if you no longer want the utility and have preserved any desired source/runtime assets.

**Local footprint:** 110 entrypoint lines, 0 reference files, 7 script files; 0 other owned entrypoints mention this name. [Source](../../skills/launch-photo-drop/SKILL.md).

### 20. prospecting-linkedin-content-manager

**Decision:** Keep only for persistent campaign work; refocus. **Usage:** N.

**What it adds:** Owns a LinkedIn knowledge base, strategy, topics, post packages, campaign calendars, metrics, and learning.

**Overlap:** Its Create Posts mode competes with product-post and technical-writing skills, and profile work overlaps with the professional dossier. Single-post drafting does not need a campaign database.

**Recommended change:** Keep as marketing-manage-linkedin if you actually run campaigns. Route prose to the relevant writing mode and candidate facts to the profile dossier. For occasional posts only, retain a compact strategy reference and drop the standalone manager.

**Evidence and limits:** No exact invocation verified, although writing and profile tasks exist. The algorithm reference has unsourced precise weights/penalties, and Topics requires an existing strategy file. This is a strong simplification candidate, not proof of current campaign usage.

**Local footprint:** 133 entrypoint lines, 6 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/prospecting-linkedin-content-manager/SKILL.md).

### 21. prospecting-signal-context-builder

**Decision:** Merge into sales-signals as setup/context mode. **Usage:** N.

**What it adds:** Normalizes product, ICP, disqualifiers, triggers, queries, and engagement constraints into signal-context.md.

**Overlap:** It exists specifically to feed prospecting-signal-detector; both already reference each other and share the same product context. A useful standalone output can still be produced by a mode.

**Recommended change:** Use sales-signals context to create/update the file without scanning. Preserve Unknown/Needs input, facts versus inference, source conflicts, and engagement constraints. Scan mode consumes the same artifact.

**Evidence and limits:** No explicit use established. This is a stronger merge than merely renaming: one entrypoint can own the signal workflow from context through reports while exposing distinct actions.

**Local footprint:** 64 entrypoint lines, 1 reference files, 0 script files; 1 other owned entrypoints mention this name. [Source](../../skills/prospecting-signal-context-builder/SKILL.md).

### 22. prospecting-signal-detector

**Decision:** Merge with context builder into sales-signals. **Usage:** N.

**What it adds:** Scans, classifies, stores, reports, and supports engagement on buying signals. Maintains signals-database.json and engagement history.

**Overlap:** Its own mode system already includes Scan/Report/Engage, making Context a natural addition. It also overlaps with LinkedIn marketing for converting trends into posts.

**Recommended change:** Preserve the signal store and history; route content creation to writing/marketing rather than expanding the detector. Distinguish one source post from repeated same-person/week activity, and avoid excessive repeated approvals for the same authorized action.

**Evidence and limits:** No exact use verified. No bundled store/merge validator exists, so JSON schema, deduplication, and mutation bookkeeping depend on instruction compliance. Test these before trusting repeated unattended scans.

**Local footprint:** 162 entrypoint lines, 3 reference files, 0 script files; 1 other owned entrypoints mention this name. [Source](../../skills/prospecting-signal-detector/SKILL.md).

### 23. pull-codex-config

**Decision:** Keep as codex-pull-config. **Usage:** N.

**What it adds:** Uses a helper for safe clone/fast-forward of the configuration repository, preserving dirty work and avoiding forced Git operations.

**Overlap:** Touches the same environment as codex-manage-skills but operates on a different state boundary: Git checkout versus declared installations. Merging is possible, but not a high-value first target.

**Recommended change:** Keep a short explicit command skill or make it a repository-maintenance command. Resolve the helper path from the installed skill rather than assuming the current repository contains skills/pull-codex-config.

**Evidence and limits:** No exact use verified. The script is useful operational behavior; a short entrypoint has low maintenance cost. Never conflate pulling the repo with plugin refresh or dependency sync.

**Local footprint:** 29 entrypoint lines, 0 reference files, 1 script files; 0 other owned entrypoints mention this name. [Source](../../skills/pull-codex-config/SKILL.md).

### 24. second-brain-capture-interactions

**Decision:** Keep; rename codex-export-interactions. **Usage:** V.

**What it adds:** Synchronizes app-visible completed Codex dialogue into project-owned interaction records, with preservation and completeness boundaries.

**Overlap:** The Second Brain name is misleading: it does not write Notion tasks/deals/ideas. It supports historical evidence, while workflow review consumes relevant history.

**Recommended change:** Rename by destination and operation. Fix the current-task versus project-wide default discrepancy through an explicit behavior decision, not a rename side effect. Keep the script with native app/session discovery boundaries.

**Evidence and limits:** Verified explicit invocation and a reported successful repaired capture in 'Capture Codex interactions'. The initial failure was followed by a fix; do not present that historical failure as a current defect. This is an actually used specialized capability.

**Local footprint:** 58 entrypoint lines, 0 reference files, 1 script files; 0 other owned entrypoints mention this name. [Source](../../skills/second-brain-capture-interactions/SKILL.md).

### 25. second-brain-capture-raw-input

**Decision:** Merge into second-brain as capture mode. **Usage:** N.

**What it adds:** Classifies supplied notes into Tasks, Deals, or Ideas using the custom shared schema.

**Overlap:** The 42-line entrypoint mostly repeats the shared Second Brain contract. External sweep performs the same classification after retrieving sources, and the API skill is a helper rather than another user goal.

**Recommended change:** Use one second-brain router with capture/sweep/review and helper references. Preserve supplied-input capture without requiring source discovery or a review. Add deliberate read-before-create matching when requested capture may repeat an existing item.

**Evidence and limits:** No explicit invocation verified. Current instructions do not establish a robust deduplication path; creating narrow rows alone can still duplicate a task or deal on repeated captures.

**Local footprint:** 42 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/second-brain-capture-raw-input/SKILL.md).

### 26. second-brain-external-sweep

**Decision:** Merge into second-brain as sweep mode. **Usage:** N.

**What it adds:** Reads scoped native sources and derives concise task, deal, or idea updates without importing entire source bodies.

**Overlap:** Its main difference from capture is source acquisition. The same schema, classification, confidence, and mutation safeguards can be shared behind one entrypoint.

**Recommended change:** Keep explicit source/time-window selection, partial-access reporting, source links, and no outbound messaging without authorization. Reuse the capture logic after acquisition. Do not make sweep the default for an ordinary note.

**Evidence and limits:** No exact use verified. Current helper limitations can affect downstream writes, and Needs Review differs from the shared contract's Review. A schema-aware common path would reduce this drift.

**Local footprint:** 44 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/second-brain-external-sweep/SKILL.md).

### 27. second-brain-notion-api

**Decision:** Repair or retire helper; remove standalone entrypoint on merge. **Usage:** N.

**What it adds:** Implements the custom Notion schema with a local token-file integration. In principle this is transport for Second Brain operations, not a user-facing goal.

**Overlap:** Overlaps with the Notion connector in transport and with the other Second Brain skills in schema. It only earns maintenance if the connector cannot provide necessary operations.

**Recommended change:** First decide whether the direct API fallback is needed. If yes, make IDs externally configurable, implement pagination/completeness, expose supported update operations, and keep it beneath the second-brain router. If not, retire it in favor of the connected Notion path.

**Evidence and limits:** Confirmed offline: query uses literal <tasks-data-source-id>; CLI has only list/create-task/create-deal/create-idea; list performs one request and drops has_more/next_cursor. No remote calls or secrets were used. Fresh rows beyond the first page can be omitted from reviews.

**Local footprint:** 67 entrypoint lines, 0 reference files, 1 script files; 1 other owned entrypoints mention this name. [Source](../../skills/second-brain-notion-api/SKILL.md).

### 28. write-product-posts

**Decision:** Keep as writing-product-posts. **Usage:** V.

**What it adds:** Contains specific Italian and English voice examples, adaptation rather than translation, sparse micro-post handling, claim preservation, and concrete product-story rules.

**Overlap:** Overlaps with technical writing and LinkedIn post creation, but this is a personal voice with an independently useful bilingual deliverable. The campaign manager should call it instead of maintaining another competing style.

**Recommended change:** Keep the voice examples as the primary differentiation. Allow explicit user requests for one language or a particular format; don't force two versions against the request. Trim repeated anti-rhetoric rules that already have one owner.

**Evidence and limits:** Verified SKILL.md read and a bilingual draft in 'DOCS: Draft Skill Registry launch post'. This is stronger evidence than a source-code reference or a generic writing task title.

**Local footprint:** 117 entrypoint lines, 1 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/write-product-posts/SKILL.md).

### 29. zotero-capture-source

**Decision:** Keep above Zotero integration. **Usage:** N.

**What it adds:** Acquires article/video evidence, separates source notes from analysis, creates paired notes, deduplicates sources, imports, and verifies the result.

**Overlap:** Zotero plugin owns the library/API mechanics. This skill owns editorial evidence processing and a specific persistent note contract. Those layers are complementary.

**Recommended change:** Keep capture workflow and RIS/session helpers; avoid hardcoded session mechanics if the provider changes. Make limitations clear for incomplete transcripts and expired connector sessions. Do not merge it into general note capture unless those guarantees survive.

**Evidence and limits:** No exact use verified. The imported source plus read-back contract is substantive, but provider session availability is not established by static inspection. A separate usage check would be needed before removing an archival workflow.

**Local footprint:** 115 entrypoint lines, 1 reference files, 2 script files; 0 other owned entrypoints mention this name. [Source](../../skills/zotero-capture-source/SKILL.md).

### 30. zotero

**Decision:** Retain provider-managed integration. **Usage:** N.

**What it adds:** Operates Zotero Desktop readiness, library search, collections, exports, and connector imports.

**Overlap:** Supports zotero-capture-source but also independent BibTeX and citation tasks. Removing it can strand a retained owned workflow.

**Recommended change:** Keep provider name and lifecycle. Choose removal at plugin level only if Zotero is no longer part of your research workflow, not because two skills contain the word Zotero.

**Evidence and limits:** No verified invocation in the task sample. Installed/readable plugin content proves availability on disk, not live Zotero readiness.

### 31. clickup

**Decision:** Keep; no uninstall recommendation. **Usage:** S.

**What it adds:** Provides the ClickUp connection used for task-backed work.

**Overlap:** Notion is the declared personal system, but team/customer project systems can remain ClickUp. One personal system does not make other project connectors redundant.

**Recommended change:** Leave its Codex-managed installation unchanged. If skills.toml ownership is revisited, distinguish declaration cleanup from uninstalling the plugin.

**Evidence and limits:** Recent task summaries include 'FEAT: implement ClickUp 86cbb8wh9' and 'FEAT: implement ClickUp task 123nktjr441'. They demonstrate requested ClickUp workflows, not a completed connector audit. My earlier unused-candidate suggestion is withdrawn.

### 32. sites

**Decision:** Keep managed platform; route explicitly. **Usage:** N.

**What it adds:** Supplies site construction and a hosting lifecycle, including existing Site manifests and deployment state.

**Overlap:** Overlaps with generic frontend building in product shape, but has platform-specific publishing capability. It should not be used merely because a task mentions a webpage.

**Recommended change:** Leave Codex-managed installation unchanged. Route explicit Sites requests and established Site projects to it; ordinary repository UI remains under the coding workflow/frontend/toolkit owners.

**Evidence and limits:** No exact use verified in the sample. That is not sufficient to remove a managed platform, particularly given your explicit ownership correction.

### 33. browser

**Decision:** Keep pending actual transport audit. **Usage:** S.

**What it adds:** Cached manifest describes local/in-app browser operations and browser lifecycle hooks.

**Overlap:** Chrome and current CUA tooling overlap at the automation surface, but existing sessions and plugin hooks may differ. Skill names do not establish transport equivalence.

**Recommended change:** Before any removal, verify local app testing, browser tabs, and current CUA dependencies. Do not infer that one browser plugin can be removed because the runtime now exposes a unified tool.

**Evidence and limits:** Browser work was observed in job search, but the inspected CUA call does not prove which legacy plugin package supplied it. Treat usage as surface evidence rather than package attribution.

### 34. chrome

**Decision:** Keep pending actual transport audit. **Usage:** N.

**What it adds:** Cached manifest targets existing Chrome tabs, cookies, authenticated sessions, and extension setup.

**Overlap:** Has apparent overlap with browser/ CUA, but user-session continuity can be a distinct capability.

**Recommended change:** Keep provider ownership. Confirm authenticated external work and actual tool dependencies before deciding whether this declared package is still needed.

**Evidence and limits:** No exact package invocation established. Generic browser activity must not be counted as Chrome use. A session-preservation test is the relevant deletion prerequisite.

### 35. visualize

**Decision:** Keep for in-conversation explanation. **Usage:** N.

**What it adds:** Produces interactive explanations, simulations, and UI previews inside the conversation, with an explicit distinction from standalone application building.

**Overlap:** Touches diagrams, charts, presentations, and UI previews but has a different consumption surface. Its current entrypoint explicitly prefers Markdown tables or Mermaid for simple static cases.

**Recommended change:** Keep. Avoid automatically invoking it for every comparison or any request containing a chart. Use artifact-specific skills when a durable workbook, deck, or publication figure is the required output.

**Evidence and limits:** No exact invocation verified. This is provider functionality; no need to copy or rename its internals in dot-codex.

### 36. remotion

**Decision:** Keep as one video capability if desired. **Usage:** N.

**What it adds:** Provider package exposes separate creation, markup, captions, maps, preview, rendering, and upgrade skills.

**Overlap:** The long list looks redundant, but most entries are stages or technical modules of video work. Bento animations are not demonstrated replacements for rendered videos.

**Recommended change:** Treat plugin membership as one decision. Do not manually merge or remove provider subskills. Use its router and only the needed technique references.

**Evidence and limits:** No verified invocation in sampled history. If video creation is no longer wanted, uninstalling the whole optional plugin could reduce discovery clutter, but it is not part of this analysis's authorization.

### 37. bento-slides

**Decision:** Keep as preferred browser-deck workflow. **Usage:** P.

**What it adds:** Authors editable single-file Bento decks by updating document JSON inside a bundled runtime.

**Overlap:** Overlaps with PowerPoint/Google Slides on presentation intent, but preserves a different file/editor target. It already replaced html-presentations by your explicit choice.

**Recommended change:** Keep provider-managed name and source. Route explicit PPTX or native Google Slides requests to their own skills. Avoid letting Bento's broad 'whenever presentation' description override the requested format.

**Evidence and limits:** Explicitly selected by the user as the preferred replacement. No completed Bento authoring run was verified in the sampled history; preference is sufficient to retain it.

[Installed source](../../skills/bento-slides/SKILL.md).

### 38. plan-company-visit-itinerary

**Decision:** Keep as a specialized planning workflow. **Usage:** N.

**What it adds:** Normalizes company sources, checks addresses, preserves provenance, simulates travel/visits, accounts for unscheduled companies, and produces a validated workbook.

**Overlap:** Spreadsheets and PDF/Docs skills supply artifact handling; they do not supply the route/schedule domain constraints. Maps in Remotion animate geography rather than plan visits.

**Recommended change:** Keep as sales-plan-company-visits. Allow independent extraction and address cleanup before missing scheduling choices are answered. Retain explicit estimated-versus-live travel labels, complete company accounting, and supplied appointment constraints.

**Evidence and limits:** No exact use verified. This has concrete helper scripts and a distinct output contract. It is a much stronger standalone candidate than generic writing-style skills.

**Local footprint:** 103 entrypoint lines, 2 reference files, 2 script files; 0 other owned entrypoints mention this name. [Source](../../skills/plan-company-visit-itinerary/SKILL.md).

### 39. answer-job-application

**Decision:** Keep as career-draft-application. **Usage:** N.

**What it adds:** Drafts application fields using an evidence-backed dossier, role context, word limits, and user-owned employment facts.

**Overlap:** General writing can supply prose, but factual career claims, missing visa/compensation facts, and employer-facing positioning require a stricter domain contract.

**Recommended change:** Keep application writing separate from searching and submission. Reuse the dossier and voice guidance; never manufacture achievements or convert repository activity into business impact.

**Evidence and limits:** No exact invocation established. Its role is independently useful even if applications are occasional; discovery and submission must remain separate authorization boundaries.

**Local footprint:** 91 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/answer-job-application/SKILL.md).

### 40. reui

**Decision:** Keep as specialist component source. **Usage:** V.

**What it adds:** Provides registry search, worked examples, component APIs, installation commands, and adaptation guidance.

**Overlap:** Impeccable guides design; coding-frontend implements in the repo; the toolkit chooses; ReUI supplies component-specific knowledge. The overlap is useful when those owners are explicit.

**Recommended change:** Keep. Stop broad descriptions from making every dashboard an automatic ReUI install. Existing compatible components may already suffice; apply licensing and dependency constraints to actual selection.

**Evidence and limits:** Verified explicit ReUI request in 'FEAT: build audit log data grid', with further ReUI tasks in archived summaries. Sampled turns do not establish final successful rendering, but actual demand is clear.

[Installed source](../../skills/reui/SKILL.md).

### 41. run-job-search

**Decision:** Keep; absorb source curation as mode. **Usage:** V.

**What it adds:** Verifies current listings, applies profile constraints, scores evidence, and merges URL-unique findings into a cumulative CSV using a helper.

**Overlap:** Source curation is an earlier mode of the same search workflow, with shared profile and criteria inputs. Separate source output can be retained without another discovery entrypoint.

**Recommended change:** Use career-search-jobs with sources and scan modes. Preserve the existing cumulative CSV and scoring schema; never start vacancy scanning when only source curation is requested. Add explicit refresh behavior if old URL judgments need rechecking.

**Evidence and limits:** Verified explicit invocation and reported 25 new URLs in 'RESEARCH: Offerte di lavoro e aggiornamento CSV'. Historical scores and URL deduplication require care: an existing row is not proof that the job is still active.

**Local footprint:** 80 entrypoint lines, 0 reference files, 2 script files; 1 other owned entrypoints mention this name. [Source](../../skills/run-job-search/SKILL.md).

### 42. build-professional-profile

**Decision:** Keep as career-build-profile. **Usage:** V.

**What it adds:** Builds a canonical dossier with sources, chronology, conflicts, evidence, positioning, and optional search criteria.

**Overlap:** Supplies facts to job search, applications, and LinkedIn profile writing. It should own candidate truth; marketing should not maintain a conflicting biography.

**Recommended change:** Keep lean/full/targeted depths and the source ledger. Separate canonical facts from channel-specific copy. A profile refresh should not automatically become a job search.

**Evidence and limits:** Verified skill-file read during 'REVIEW: LinkedIn builder positioning'. The task reported a read-only profile assessment. This directly supports the skill's value beyond vacancy searching.

**Local footprint:** 64 entrypoint lines, 3 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/build-professional-profile/SKILL.md).

### 43. curate-job-search-directories

**Decision:** Merge into career-search-jobs as sources mode. **Usage:** N.

**What it adds:** Creates a verified, ranked source plan with stable CSV fields and a recommended complementary set.

**Overlap:** Shares dossier, search constraints, geography, and source-selection intent with run-job-search. They already call each other. The boundary is a mode choice, not necessarily a separate skill.

**Recommended change:** Preserve job_directories.csv and source-only invocation. Keep current provider verification, source preservation, and deduplication. Do not fold the profile builder or application writer into this search skill.

**Evidence and limits:** No exact invocation verified, but job search demonstrably consumed a source list. Consumed data proves the artifact's utility, not which skill created it.

**Local footprint:** 73 entrypoint lines, 0 reference files, 0 script files; 1 other owned entrypoints mention this name. [Source](../../skills/curate-job-search-directories/SKILL.md).

### 44. writing-technical-content

**Decision:** Keep; expand carefully as writing modes. **Usage:** C.

**What it adds:** Now owns technical prose and work recaps with an anti-rhetoric reference. It is the natural home for message voice and customer-requirements modes.

**Overlap:** Can reduce separate style/template skills without absorbing marketing campaigns, career truth, or file-format mechanics. Mode-specific output expectations must remain discoverable.

**Recommended change:** Keep a small router with technical prose, recap, message, and requirements modes. Load only the corresponding references. If those non-technical modes are added, writing-content may be a better name than writing-technical-content.

**Evidence and limits:** This task created and independently inspected the consolidation, not a real writing deliverable with the new name. The retained anti-rhetoric reference imposes numeric sentence-length proportions; that conflicts with proportional natural writing and should not spill into short modes.

**Local footprint:** 65 entrypoint lines, 2 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/writing-technical-content/SKILL.md).

### 45. codex-manage-skills

**Decision:** Keep as desired-state owner. **Usage:** V.

**What it adds:** Owns inspect/list/doctor, membership changes, updates, and additive reconciliation through one engine.

**Overlap:** Overlaps with runtime skill-installer and plugin-management at installation intent. The distinction is repository desired state versus generic installation or account connection management.

**Recommended change:** Keep one owner for skills.toml mutations. Use native providers for package lifecycle, but do not let generic installers silently create undeclared repository dependencies. Doctor should be described as inventory health, not runtime usability.

**Evidence and limits:** Used in this task. The Second Brain helper can pass inventory health while being unconfigured, showing exactly why presence and behavior must be reported separately.

**Local footprint:** 29 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/codex-manage-skills/SKILL.md).

### 46. second-brain-review

**Decision:** Merge into second-brain as review mode. **Usage:** C.

**What it adds:** Provides brief/weekly read-only views of the same Tasks/Deals/Ideas schema. The recent consolidation correctly preserved both depths.

**Overlap:** Shares schema, transport, confidence, and state interpretation with capture and sweep. One router with explicit read/write modes can avoid repeated contract drift.

**Recommended change:** Retain brief default and weekly detail inside a consolidated Second Brain skill. Require complete or explicitly partial data before summarizing priorities; don't treat a 25-row first page as the full system.

**Evidence and limits:** The new entrypoint was created and inspected here, not exercised against live Notion. Its document-level acceptance passed; this does not establish that its underlying optional API adapter works.

**Local footprint:** 32 entrypoint lines, 0 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/second-brain-review/SKILL.md).

### 47. coding-ui-toolkit

**Decision:** Keep as the agreed meta skill. **Usage:** P.

**What it adds:** Selects UI approaches and coordinates Impeccable, ReUI, existing components, references, and artifact routes.

**Overlap:** It intentionally overlaps at the selection layer. It should not repeat the specialists' implementation playbooks or become an extra mandatory gate before every UI edit.

**Recommended change:** Keep a selective catalog and direct route for explicit specialists. The retained review-handoff reference still contains a full review procedure; trim it toward your unique component/annotation handoff requirements to avoid slowly recreating a second Impeccable.

**Evidence and limits:** User explicitly requested the meta role; the previous batch verified its instruction-level routing. No claim of live model behavior across all UI prompts. Do not delete it in the name of reducing skill count.

**Local footprint:** 28 entrypoint lines, 4 reference files, 0 script files; 0 other owned entrypoints mention this name. [Source](../../skills/coding-ui-toolkit/SKILL.md).

## Every exposed provider/system skill

These 38 rows expand provider modules and runtime-owned skills, including modules behind plugin declarations already discussed above. They are not 38 additional desired-state dependencies. No use was established for each module individually unless stated. This section assesses routing and duplication, not installed-version correctness or complete implementation behavior.

### imagegen

System raster creation/editing workflow; distinct from diagram XML and data plots.

**Recommendation:** Keep runtime-owned. Route only bitmap tasks here, and use the available image tool's current contract; a generic screenshot is not image generation.

### openai-docs

Official product/self-knowledge research; overlaps broad skill-management questions at the information stage.

**Recommendation:** Keep runtime-owned. It explains current OpenAI behavior; codex-manage-skills owns this repository's mutations. Avoid loading model/API material for local inventory edits.

### plugin-creator

Creates plugin manifests and bundles.

**Recommendation:** Keep runtime-owned. It packages skills/tools; skill-creator writes skill behavior, and inventory management records desired installation. Three stages can compose without being three competing owners.

### skill-creator

Authors skill content, references, scripts and metadata.

**Recommendation:** Keep runtime-owned. Useful authoring guidance is distinct from installation, inventory reconciliation, and retrospective evaluation.

### skill-installer

Generic GitHub/curated skill download and installation.

**Recommendation:** Keep runtime-owned, but use codex-manage-skills for desired-state mutations here. Direct installation can otherwise create undeclared content. Do not edit the runtime skill to enforce a local inventory preference.

### documents:documents

DOCX authoring, edits, comments, redlining and rendered verification; can feed Google Docs.

**Recommendation:** Keep. writing-content supplies substance; this supplies document mechanics. Treat generic writing advice inside the provider as default rather than duplicating local voice everywhere.

### pdf:pdf

PDF reading, generation, rendering and fillable-form handling.

**Recommendation:** Keep. A PDF export from Word is only one use; forms and existing PDFs are separate. A diagram screenshot does not replace PDF semantics.

### presentations:Presentations

PowerPoint/native presentation creation and editing, plus Google Slides routing.

**Recommendation:** Keep alongside Bento for requested native formats. Bento's broad presentation trigger is a routing collision, not a reason to remove PPTX capability.

### spreadsheets:Spreadsheets

Standalone workbook construction, formulas, charts, formatting and recalculation.

**Recommendation:** Keep. Job-search CSV and itinerary domain logic are separate from workbook mechanics. Do not require complex workbook authoring machinery for a plain CSV append unless the applicable skill contract demands it.

### spreadsheets:excel-live-control

Targets an already selected live Excel desktop/add-in session.

**Recommendation:** Keep runtime-owned; activate only for that live target. It is not a duplicate of standalone file generation and must not silently replace the selected workbook with a new artifact.

### template-creator:template-creator

Turns an artifact into a reusable personal template skill.

**Recommendation:** Keep runtime-owned. Distinct from one-off artifact creation; do not invoke for every reference-based document edit. It can replace locally maintained format templates if they become truly reusable.

### google-drive:google-drive

Finds files and owns Drive file lifecycle, routing to format specialists.

**Recommendation:** Keep provider-managed. File discovery is not content editing; avoid loading every sibling. Its broad net-new Docs instructions and newer Google Docs native-template routing can disagree, so inspect the specialized current route.

### google-drive:google-docs

Native document editing, template/tab preservation, and format-aware creation.

**Recommendation:** Keep. Native reference documents are not interchangeable with DOCX reconstruction. Existing-document native fidelity is the distinguishing behavior; use the specialized route over generic router assumptions.

### google-drive:google-sheets

Connected-sheet selection, ranges, state, formulas and batch updates.

**Recommendation:** Keep. Shares spreadsheet technique with the workbook skill but owns the live cloud file. Existing-sheet edits need precise readback and should not become a replacement import by default.

### google-drive:google-slides

Native deck templates and existing-slide edits.

**Recommendation:** Keep. It explicitly routes net-new decks without native references toward Presentations. This is a useful format boundary, not two independent slide systems to merge locally.

### google-drive:google-drive-comments

Creates/replies/resolves comments with quoted text, cell ranges or slide evidence.

**Recommendation:** Keep as provider module. Comments are external collaboration actions, distinct from editing content or returning a private review. Its batch-splitting approval instructions should not imply extra permission when the user's request already authorizes the full batch.

### notion:notion-knowledge-capture

Creates general wiki, decision, how-to and FAQ pages.

**Recommendation:** Keep provider module but distinguish from the specific SB Tasks/Deals/Ideas schema. It proposes hubs, links and task creation that must stay within user scope; do not let it redesign Second Brain automatically.

### notion:notion-meeting-intelligence

Prepares agendas and pre-reads from Notion context.

**Recommendation:** Keep module if Notion meeting preparation is useful. It shares retrieval and writing with research/capture but has attendee/decision/timebox intent; don't replicate it with a new local meeting skill without a concrete gap.

### notion:notion-research-documentation

Synthesizes multiple Notion pages into reports with citations.

**Recommendation:** Keep provider module. A request to answer a question need not imply publishing a new Notion page. Source retrieval and artifact creation should follow the user's requested destination.

### notion:notion-spec-to-implementation

Creates Notion plans, tasks and progress records from specs.

**Recommendation:** Keep provider-managed but avoid competing authority with coding-workflow feature/status/proof. Prefer it as a Notion intake/tracking adapter when requested. It must not silently establish a second acceptance or task system for the same engineering feature.

### impeccable:impeccable

Design direction, critique, audit, visual refinement and many specialist playbooks.

**Recommendation:** Keep; explicit user invocation verified. This is the main UI technique provider. The owned toolkit selects it; frontend owns repository technique; lifecycle stays with coding-workflow. Do not copy these playbooks into the toolkit.

### remotion:remotion-best-practices

Router for video tasks and specific technical modules.

**Recommendation:** Keep with Remotion. Evaluate the package as one optional video capability rather than twelve independent local skills.

### remotion:remotion-captions

Caption transcript timing, import and rendering structures.

**Recommendation:** Keep with Remotion; a specialized timed-data model. Different from summarizing a transcript into Zotero notes.

### remotion:remotion-create

Scaffolds video projects and new compositions.

**Recommendation:** Keep with Remotion. Its setup should not run when modifying an existing video, previewing, or only rendering.

### remotion:remotion-docs

Discovers current Remotion API documentation.

**Recommendation:** Keep provider module. Similar generic research principles can coexist because this contains provider-specific discovery mechanics; unlike the retired local coding-research entrypoint it is bundled with the provider.

### remotion:remotion-interactivity

Structures video markup for interactive playback/editing.

**Recommendation:** Keep module; distinct from exporting a static MP4. Route only when interactivity is relevant rather than reading it for every render.

### remotion:remotion-maps

Selects map rendering/animation techniques.

**Recommendation:** Keep module. It animates geographic scenes; it does not replace the company-visit itinerary's address verification and scheduling constraints.

### remotion:remotion-markup

Frame-based animation, media composition and React markup techniques.

**Recommendation:** Keep as the implementation core of video authoring. Generic frontend animation advice is not a safe substitute for frame-deterministic rendering.

### remotion:remotion-multimedia

Media duration and dimension inspection through Mediabunny.

**Recommendation:** Keep provider helper. Small entrypoints in a package may be routing aids rather than unwanted standalone workflows.

### remotion:remotion-render

Exports completed video or still compositions.

**Recommendation:** Keep; rendering is a distinct executable operation, and shouldn't force project creation or studio startup.

### remotion:remotion-saas

Embeds players and rendering in an application.

**Recommendation:** Keep module only loaded for a video product/app. It composes with frontend and backend skills, not a replacement for their architecture.

### remotion:remotion-studio

Starts/reuses preview studio.

**Recommendation:** Keep helper. It manages a runtime process and preview state, distinct from video file export.

### remotion:remotion-upgrade

Coordinates matching Remotion/media package versions and skills.

**Recommendation:** Keep provider module; only use for an upgrade request. It can alter package and skill state, so local inventory ownership must be respected when a provider update touches globally managed content.

### sites:sites-building

Builds within the Sites platform and owns its checkout/lifecycle.

**Recommendation:** Keep Codex-managed. Use for explicit or established Sites targets, not generic UI work. Its source ownership restrictions mean the toolkit must not delegate Site mutations to a non-owning agent.

### sites:sites-hosting

Registers, versions and deploys Sites builds.

**Recommendation:** Keep Codex-managed. Hosting is not duplicated by frontend implementation. Preserve explicit deployment scope and do not treat a UI critique as publishing authorization.

### plugin-management:plugin-management

Discovers plugins, manages connections/permissions and removal.

**Recommendation:** Keep provider-managed. It owns native capabilities; codex-manage-skills records local desired state. Avoid recommending installations solely because an adjacent service might help.

### visualize:visualize

In-conversation interactive explanations and previews.

**Recommendation:** Keep as the module behind the declared plugin. Different from standalone Sites apps, exported figures and slide decks. No need for a new local wrapper.

### zotero:Zotero

Local library/API readiness, search, export and import.

**Recommendation:** Keep behind source capture and independent citation tasks. Do not merge provider integration code into the owned source-processing skill.

## Decision rules for the next cleanup

1. Keep a top-level skill when it has a distinct integration/state boundary, substantial domain workflow, or deliberately desired invocation.
2. Use a mode/reference when the difference is mainly voice, output template, or a stage in one workflow. A sources-only or requirements-only request remains possible through a mode.
3. Move a skill to its project when its rules depend on that project's private paths, schemas, lifecycle, and runtime.
4. Keep provider packages under their actual owner. Do not rename caches, vendor provider playbooks, or manually delete subskills to reduce a count.
5. Remove a capability only when the user no longer wants it or a verified replacement preserves the necessary behavior. No observed usage is a question mark, not authorization.
6. Preserve first-principles-clarity and coding-ui-toolkit per explicit preference. Keep ClickUp and Sites installation unchanged.

## What remains unknown

No lifetime usage telemetry was available in this pass. Older non-archived tasks, other hosts, implicit skill use, and tasks outside the sampled history may change usage judgments. No live external account readiness was tested. Most scripts were not executed; the exception was the isolated offline Second Brain helper probe. Provider routing passages were inspected selectively, and their full references/helpers are outside this portfolio audit. These limits constrain deletion decisions, not the concrete overlap and local-code findings above.

No skills, inventory entries, plugins, or credentials were changed by this audit. Only this report and its compact evidence file were written. The earlier completed consolidation remains intact.
