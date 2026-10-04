# Flexible discovery acceptance

## Done and command

Run `proof/run.sh` from any directory. The runner validates retained fresh-agent trials and their independent adjudication. It does not launch models or grade prose. A PASS means the required sampled observations and final review passed on the recorded instruction snapshot, not that behavior is reliable across future runs.

Use `python3 proof/prepare.py --case CASE --destination EMPTY_DIRECTORY` to produce a raw repository and request. Give a fresh worker that request, the chosen instruction snapshot, and access to the isolated repository. Keep `proof/rubric.md` and other workers' outcomes out of its context. Baseline and candidate workers use the same model/effort and fixture for the motivating comparison. Record unavoidable differences in `proof/trials.json`.

## Boundary and scenarios

The producer is a realistic user request plus repository files; activation is a fresh worker receiving that request; the consumer is the user and repository artifacts. Read-back consists of actual native worker turns, tool activity, and resulting artifacts. Only the repository and unavailable user are simulated. No model response is supplied as a fixture. Trial workers cannot change the harness, invoke native Goals, use external systems, or implement beyond the request.

| Case | Activation and observation | Plausible incomplete behavior caught |
| --- | --- | --- |
| `studio` | Inspect the raw scheduling repository and shape a broad self-service request; observe questions, recommendations, and any artifacts. Run baseline and candidate separately. | Starts a large accepted specification without investigating facts or exposing consequential decisions; splits work into frontend/backend/database instead of useful outcomes. |
| `export` | Prepare one specification from a settled, precise CSV export request. Read its artifact and actions. | Repeats settled questions, requires APP/ARCHITECTURE scaffolding, or expands scope before producing the requested narrow spec. |
| `repair` | Repair a reproducible capacity-counting bug through the actual Python test command. Inspect the diff and test result. | Adds a feature ceremony or leaves a clear authorized repair unimplemented; counts cancelled reservations. |
| `portal` | Shape a deliverable after an answer to one earlier workspace question; inspect existing integration and observe how other decisions are treated. Candidate-only held-out case. | Converts agreement about workspace scope into acceptance of a particular customer interface, or freezes an ambiguous integration as an accepted contract. |

The withheld rubric defines outcome criteria, tolerates different good approaches, and requires evidence references. Domain guidance, independent proof/review ownership, preserved contracts, and routing coherence additionally require a final separate reviewer to inspect the actual changed instructions. Runtime trials alone do not cover every supporting skill.

## Evidence and pass criteria

`proof/trials.json` records each attempt, including failures, instruction hashes, model/effort, fixture digest, native worker identity, native transcript excerpt, artifacts, and limitations. Transcript excerpts contain visible user/assistant/tool events, never hidden reasoning. Preserve enough real events to assess actions; a worker-written summary is supplemental only. Each required candidate case must satisfy the independently applied rubric; at least the baseline `studio` comparison must be retained whether it passes or fails. An unresolved material gap fails acceptance. No requirement to manufacture a baseline failure or a numerical improvement.

The evidence runner checks file integrity, required trial coverage, observation kind, matching comparison conditions, independent reviewer attribution, and a PASS final review. Semantic adjudication remains an identified independent review of the traces and artifacts. It must not be authored by the candidate implementer or this proof's author. The reviewer may reject superficially compliant text if actual actions contradict it.

One sample per case is a modest forward check, selected to cover exploratory work, settled work, bounded repair, and a withheld decision boundary with low execution cost. It cannot estimate success frequency or establish a statistically meaningful improvement. Repeat a case only for a documented change or failed/ambiguous trial; keep earlier attempts. Do not pool unlike trials into a reliability claim.

## Proves and does not prove

Proves sampled observable behavior for recorded instructions under the declared worker conditions and the actual repaired fixture test. Does not prove full production delivery, external services, real user satisfaction, model-version independence, continuous enforcement, or the quality of every future specification. Fixture isolation and supplied skill paths differ from ordinary automatic routing; record that limitation. No tests match instruction headings or demand exact wording.

Acceptance inputs are FEATURE, PROOF, `prepare.py`, `rubric.md`, `run.sh`, and `check.py`. Evidence files are outputs and are not acceptance inputs. Final review must identify the instruction snapshot it inspected; final proof evidence must match that snapshot.
