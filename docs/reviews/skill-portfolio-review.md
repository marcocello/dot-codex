# Skill Portfolio Review

Date: 2026-09-15. Status: recommendations only. The earlier removal of `html-presentations` is already complete; no additional inventory changes are part of this review.

## Scope and evidence

Reviewed the 51 declared dependencies in `skills.toml`: 42 owned skills and 9 external dependencies. Owned entrypoints were inspected across this task, alongside selected references, the inventory ownership contract, and the Second Brain contract. Bento, ReUI, and Impeccable entrypoints were inspected for replacement boundaries; selected cached plugin manifests were inspected for capability distinctions. This is an instruction and portfolio review, not a behavioral test of every skill, script, or integration. No usage-frequency analysis or live provider validation was performed.

## Recommended reduction

1. Replace `coding-ui-improvement` as a separate entrypoint with Impeccable critique/audit, retaining local annotation and implementation-brief guidance in an owned reference. Verify the read-only review path before retirement.
2. Fold `coding-research` into a research reference used by `coding-workflow` Shape/Analyze.
3. Merge `codex-session-showcase` into technical writing as a recap mode, retaining its evidence checklist.
4. Merge Second Brain activity brief and weekly review into `second-brain-review`, with brief and weekly modes.
5. Merge skill management and synchronization into `codex-manage-skills`, keeping membership changes and additive reconciliation distinct.

These changes reduce 51 declared dependencies to 46 if no other dependencies are added or removed. Conditional removals such as ClickUp and first-principles reasoning are separate decisions. Fewer entrypoints improve selection only if the remaining descriptions and references are precise; file count alone is not a quality metric.

## Naming

Use recognizable domain prefixes for owned skills: `coding-`, `codex-`, `writing-`, `career-`, `marketing-`, `sales-`, `knowledge-`, `second-brain-`, `decision-`, `diagram-`, and `event-`. Prefer short action/object names within each family without forcing awkward grammatical uniformity. Keep provider names for external skills and plugins. Do not rename runtime-owned skills or edit downloaded content for local preferences.

## Complete inventory decisions

| Current dependency | Decision | Proposed name or destination | Rationale and changes |
|---|---|---|---|
| capture-note | Keep, narrow | knowledge-capture-markdown | Preserves Markdown collection conventions. Remove generic Second Brain routing from its scope. |
| casual-message-rewriter | Keep, simplify | writing-rewrite-message | Useful personal voice. Preserve material meaning; summarization and lowercase should follow the request. |
| codex-session-showcase | Merge | writing-technical-content | Move evidence collection and recap shapes into the technical-writing skill; remove the mandatory screenshot attempt. |
| coding-antipattern-review | Keep | coding-review-code | Own code-quality findings and false-positive checks. Load architecture-specific detail only when needed. |
| coding-app-improvement-review | Keep, rename | coding-review-workflow | Reviews delivery runs and corrections, not product UI. Distinct from source-code review. |
| coding-architecture-deep-dive | Keep | coding-review-architecture | Own design decisions, reference comparisons, migration tradeoffs, and workload analysis. |
| coding-commit | Keep, shorten | coding-commit | Stage-selection and commit behavior are useful. Consolidate repeated scope and ignore-policy instructions. |
| coding-workflow | Keep, narrow routing | coding-workflow | Central engineering lifecycle. It should not impose engineering ceremonies on ordinary writing or personal operations. |
| coding-frontend | Keep, change defaults | coding-frontend | Own React/Next.js implementation. Limit the compulsory admin starter to suitable admin products; narrow language-agnostic UI triggers. |
| coding-laravel-feature-builder | Keep, rename | coding-laravel | Framework conventions and lifecycle boundaries justify a separate skill. |
| coding-php-legacy-maintainer | Keep, rename | coding-php-legacy | Useful for include chains, globals, runtime compatibility, and containment outside Laravel/WordPress. |
| coding-prepare-environment | Keep, simplify | coding-prepare-environment | Shared executable setup support. Preserve repo conventions and avoid unnecessary task-file or ignore-policy changes. |
| coding-python-backend | Keep, narrow trigger | coding-python-backend | Python API technique is distinct. Generic mentions of backend or endpoints should not select Python by themselves. |
| coding-research | Merge | coding-workflow reference | Short source-verification workflow adds little as a separate entrypoint. Retain as a Shape/Analyze research reference. |
| coding-secret-audit | Keep, rename | coding-audit-secrets | Executable GitGuardian and personal-information workflow is distinct. Clarify checkout-only coverage and scanner exclusions in the receipt. |
| coding-ui-improvement | Replace entrypoint | impeccable | Impeccable already owns critique, audit, accessibility, responsive design, and refinement. Preserve local read-only annotation handling and component-level handoff guidance in an owned reference. |
| coding-wordpress | Keep | coding-wordpress | Hooks, nonces, capabilities, plugin/theme layouts, and WP verification are distinct. Reconsider forced greenfield layout for standalone plugin deliverables. |
| customer-tech-requirements | Keep, refine | sales-draft-technical-requirements | Customer/vendor ownership and internal risk separation add value. Sizing examples must remain assumptions, not universal requirements. |
| create-cli-toolkit-kit | Keep, reclassify | coding-build-cli-toolkit-kit | Specialized TWYD runtime adapters and package proof are coding. Consider project-local ownership if no other repository consumes it. |
| drawio-diagram-design | Keep | diagram-build-drawio | Native editable Draw.io output and deterministic validation are not replaced by general visualizations. Preserve styling for ordinary edits. |
| first-principles-clarity | Conditional keep | decision-test-assumptions | Keep if explicitly used for structured reasoning. Otherwise it is a reasonable deletion candidate; much guidance repeats baseline reasoning behavior. |
| launch-photo-drop | Keep | event-photo-drop | A bundled working utility with a lifecycle, rather than generic advice. Broader name covers start, status, and stop. |
| manage-codex-skills | Keep, absorb sync | codex-manage-skills | Single inventory entrypoint with inspect, add/remove/update, and reconcile modes. |
| no-bullshit-technical-writing | Keep, absorb showcase | writing-technical-content | Own evidence-led articles, case studies, technical copy, and work recaps. Keep product social posts separate. |
| prospecting-linkedin-content-manager | Keep, refocus | marketing-manage-linkedin | Own strategy, campaigns, analytics, and learning. Avoid making a campaign knowledge base mandatory for a single post. |
| prospecting-signal-context-builder | Keep | sales-build-signal-context | Reusable qualification and search criteria are an independently useful artifact. |
| prospecting-signal-detector | Keep, simplify | sales-find-buying-signals | Own signal discovery, records, reports, and engagement history. Deduplicate approvals while retaining authorization for external actions. |
| pull-codex-config | Keep | codex-pull-config | Repository clone/fast-forward is distinct from dependency reconciliation; useful executable support. |
| second-brain-activity-brief | Merge | second-brain-review | Brief mode of the shared Notion review workflow. |
| second-brain-capture-interactions | Keep, rename, fix default | codex-export-interactions | Exports project-owned Codex dialogue, not Notion state. Resolve description/body disagreement on current-task versus whole-project default. |
| second-brain-capture-raw-input | Keep | second-brain-capture | Classifies supplied material into the specific Notion task/deal/idea schema. |
| second-brain-external-sweep | Keep | second-brain-sweep-sources | Reads scoped external sources and derives Notion updates; distinct from supplied-input capture. |
| second-brain-notion-api | Keep as adapter | second-brain-notion-api | Retains executable support for the custom schema. Use absolute installed script paths and align select values with the shared contract. |
| second-brain-weekly-review | Merge | second-brain-review | Weekly mode adds depth, not a separate destination or fundamental workflow. |
| sync-codex-skills | Merge | codex-manage-skills | Same inventory engine. Preserve additive reconciliation semantics in its own mode. |
| write-product-posts | Keep | writing-product-posts | Concrete Italian/English voice examples and adaptation rules differentiate it from general technical writing. |
| zotero-capture-source | Keep | knowledge-capture-zotero-source | Source acquisition, note structure, and verified import are a workflow layered on the Zotero integration. |
| zotero | Keep | zotero | Integration required by source capture; retain provider name. |
| clickup | Conditional remove | clickup | The personal operating contract uses Notion. Remove if no separate team/customer ClickUp workflow remains; that usage is not established by this review. |
| sites | Conditional keep | sites | Keep for requested Sites publishing or existing Sites projects. Local frontend skills do not replace its hosting capability. |
| browser | Keep pending tooling review | browser | Cached manifest targets local/in-app browsing. Do not infer redundancy from its name; confirm current CUA/plugin dependencies before removal. |
| chrome | Keep pending tooling review | chrome | Cached manifest targets existing Chrome sessions. Confirm authentication/session coverage and current CUA dependencies before removal. |
| visualize | Keep | visualize | Interactive explanation artifacts are distinct from slide decks, editable Draw.io files, and frontend applications. |
| remotion | Conditional keep | remotion | Keep if video output matters. Bento presentation motion is not a demonstrated substitute for the video workflow. |
| bento-slides | Keep | bento-slides | Preferred browser presentation workflow, replacing the removed HTML presentation skill. Preserve provider-managed content and name. |
| plan-company-visit-itinerary | Keep, simplify intake | sales-plan-company-visits | Address provenance, schedule simulation, coverage, and workbook validation add real value. Allow independent extraction before schedule decisions arrive. |
| answer-job-application | Keep | career-draft-application | Evidence-grounded application writing is distinct from searching and profile building. |
| reui | Keep when used | reui | Specific component APIs, examples, and registry operations complement Impeccable design guidance. Remove only if abandoning ReUI as a component source. |
| run-job-search | Keep | career-search-jobs | Current vacancy verification and cumulative CSV merging are distinct operations with executable support. |
| build-professional-profile | Keep | career-build-profile | Evidence-backed reusable dossier supports applications and search without inventing candidate facts. |
| curate-job-search-directories | Keep | career-curate-job-sources | Source selection is distinct from executing vacancy searches. Keep a separate invocation even though both share career context. |

## Highest-value instruction repairs

### Route personal work by its actual destination

`docs/harness/secondbrain.md` currently describes broad personal operations. Narrow it to organizing tasks, deals, and ideas in the specific Notion system. Markdown notes, career dossiers, writing, and research artifacts should retain their own destinations. Apply coding lifecycle rules to engineering work rather than every task in dot-codex.

### Assign frontend responsibilities

Use `coding-workflow` for delivery lifecycle, `coding-frontend` for implementation conventions, Impeccable for design/critique, and ReUI for selected registry components. Avoid loading every design reference or installing components for an ordinary review. Local contracts should preserve review-only scope and fixed acceptance regardless of provider playbook defaults.

The frontend skill requires cloning an admin template for almost any greenfield frontend. Scope that preference to admin/dashboard applications or an explicit user choice. The Python skill's generic backend triggers should require Python context or an accepted Python choice. The WordPress greenfield tree should accommodate a standalone distributable plugin. These are proposed policy changes, not instructions applied in this review.

### Remove unsupported LinkedIn precision

`skills/prospecting-linkedin-content-manager/references/linkedin-algorithm.md` contains precise reach penalties, comment weights, distribution windows, and format prescriptions without supporting citations in that file. Remove them as standing facts or replace them with dated sourced claims and audience-specific experiments. This review identifies missing grounding; it does not establish the current LinkedIn algorithm. Let the writing skill own prose and the marketing skill own strategy and results.

### Resolve contradictory and restrictive defaults

- Interaction capture: description says current-task default; body says project-wide default. A choice is needed before changing behavior.
- Second Brain: use the contract's `Review`, not unsupported `Needs Review` values.
- Showcase: screenshots described as optional must not be a prerequisite for drafting.
- Message rewriting: preserve commitments and qualifications unless summarization is requested.
- Customer requirements: avoid promoting an example capacity into a universal requirement.
- Company visits: source extraction can proceed independently of missing start/end times.
- Signal engagement: retain external-action authorization but avoid repeatedly requesting equivalent approval.
- Draw.io: preserve user styling and coordinates for ordinary edits rather than always applying import redesign.
- Decision analysis: remove celebrity framing and use introspective/ego analysis only when relevant.

## Skills supplied outside the declared inventory

The session exposes additional provider/runtime skills. Their presence is not evidence that they should all be copied into `skills.toml`. The following is capability-level routing based on the exposed catalog, not a full audit of each implementation:

| Family | Recommendation |
|---|---|
| System skill creation, plugin creation, installation, OpenAI documentation | Retain runtime ownership; do not rename or declare system skills. Local inventory management has a different responsibility. |
| Documents, PDF, spreadsheets, PowerPoint presentations | Keep native-format capabilities. Bento does not replace workbook formulas, Word redlining, PDF forms, or PPTX editing. |
| Google Drive with Docs/Sheets/Slides/comment subskills | Keep when connected work matters. These coordinate remote files and native edits; local artifact skills are complementary. |
| Notion knowledge capture, meeting intelligence, research, spec implementation | Use for general Notion documents and projects. Route the custom Tasks/Deals/Ideas schema through Second Brain skills. Do not merge provider code into owned skills. |
| Impeccable | Keep as the primary UI design and critique capability; source inspected for the UI-review replacement recommendation. |
| Image generation | Keep for raster images; distinguish from editable diagrams and data visualizations. |
| Template creator | Keep for reusable artifact templates; it is not another ordinary drafting skill. |
| Plugin management | Keep for native connection/discovery management; the inventory manager owns repository desired state. |
| Remotion subskills | Treat as one video capability with specialized references/operations, not many independently redundant skills. |

## Migration boundaries

For an approved cleanup, change owned names, folders, metadata, inventory entries, current cross-references, and script callers together. Use `skill_inventory.py` for desired-state mutations. Preserve historical feature and interaction evidence as history. Do not silently change output schemas, state directories, scope defaults, approval semantics, or frozen proof inputs as part of renaming. Test affected executable callers and replacement workflows before removing their entrypoints.

The most useful first batch is the five specified consolidations/replacements. Keep conditional removals separate until the intended workflows are known. No additional removal is authorized by this analysis deliverable.
