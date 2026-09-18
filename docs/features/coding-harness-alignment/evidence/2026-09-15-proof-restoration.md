# Proof restoration — 2026-09-15

## Authority, author and history

Independent proof author: `/root/current_proof_author`, spawned by `/root` in native task `01a0a570-1b40-7a61-bc79-4c8e8bd7fd6d`. The actual collaboration task transcript retains the assignment, source reads, authored changes and diagnostic command results. This author did not modify FEATURE.md, implementation, shared commands or inventory. Full automatic dialogue extraction is partial; no unavailable history is invented.

The user explicitly approved the current workflow and inventory as intended behavior. FEATURE.md records that accepted verification revision. Prior fixed inputs are retained at `2026-09-15-prior-acceptance/`; the parent recorded the original inventory failure (removed skills), missing semantic evidence and obsolete historical test paths in `2026-09-15-verification-context.md`. These are superseded acceptance expectations, not evidence that current runtime commands were defective.

## Exact old-to-new mapping

| Original input or scenario | Current mapping and reason |
|---|---|
| `proof/acceptance.py:REQUIRED_CAPABILITIES`, fourteen historical skills | The ten named coding skills accepted in the revised FEATURE; compare the coding subset only. Current non-coding inventory remains checked through the real inventory CLI without hardcoding its count. |
| `discovery`, `references` | Same real inventory CLI, owned skill doctor, installed frontmatter identity, retired entrypoint and local-link boundaries; every fixed acceptance input must be Git-deliverable. |
| `supporting_journey` | Preserved real claim, rejected foreign takeover, rejected no-proof completion, captured marker proof, successful completion/read-back, reopen, captured failure, older-PASS rejection and PROOF mutation guarding. Added no-state-mutation read-back after older-PASS rejection. |
| Existing ownership/completion scenario plus accepted core extension | Dedicated `ownership_concurrency`: four real simultaneous independent CLI claims, read-back without lost updates, rejected stale state, and rejected duplicate task ownership. Dedicated `unfinished_attempt`: a real second capture reaches its runner and creates a STARTED record without a final result; the old PASS cannot complete while it runs. Capture is then interrupted and cleaned up. |
| Accepted regression/proof separation extension | Dedicated `regression_separation`: real passing captures in both modes; regression path rejection, independent official proof remains valid after regression, and captured regression output remains invalid when moved into a proof-shaped path. The authority under test is the real feature-status completion validator. |
| `assessed_behavior` report validation | Extracted validation into `validate_assessment`; retained required current candidate, distinct actual role/history identifiers, transcript digest, six reasoned PASS results and limitations. Added `assessment_rejection` with explicit synthetic positive/negative validator inputs. These inputs are never semantic evidence and cannot satisfy the separate `assessed_behavior` group. |
| `cases.json` six prompts and rubrics | Unchanged byte-for-byte. They already cover Shape, Ship, Fix, Analyze and Operate, explicit Goal authority, regression repair, fixed acceptance, runtime closure and evidence limitations. |
| `assessment-schema.json`, `run.sh` | Unchanged byte-for-byte. Runner still executes this feature's dedicated standard-library program only. No removed root unit file, another feature's whole proof, generic suite or fabricated assessment was substituted. |
| `snapshot()` | Preserved candidate binding and added `scripts/gate`, which the real feature_status command loads to decide completion. |
| Setup maintenance | Separate supporting regression scope, owned and captured by root; not folded into dedicated acceptance. |

## Feasibility diagnostics

Command: `python3 docs/features/coding-harness-alignment/proof/acceptance.py run` from the installed checkout, Python 3.13.3. Two diagnostic attempts after the accepted revisions returned exit 1 with seven groups PASS: discovery, references, supporting_journey, ownership_concurrency, unfinished_attempt, regression_separation, assessment_rejection. `assessed_behavior` correctly failed because HARNESS_ALIGNMENT_ASSESSMENT was absent. No independent behavioral PASS is claimed by these diagnostics. Every fixed acceptance input returned exit 1 (not ignored) from `git check-ignore -- <path>`.

The capture command fixtures use isolated temporary repositories and real subprocesses. No external account or production API is invoked. Synthetic report records test parser/validation structure only and are explicitly labeled as such. Self-reported identities are not cryptographic identity verification; root and the final reviewer must compare actual collaboration history.

## Frozen acceptance inputs

The following hashes freeze the accepted revision after diagnostics. Later official proof must use a fresh real exercise, separate assessment and unchanged inputs. Evidence outputs do not alter the snapshot.

- `docs/features/coding-harness-alignment/FEATURE.md`: `4a37359914def739103f369d1a6b74b966b940e223f1548e8753c032732e3db9`
- `docs/features/coding-harness-alignment/PROOF.md`: `2b1738f09e42f754f5ffef0b7078d6573696afc0eca2e30fce33f159a0d7513a`
- `docs/features/coding-harness-alignment/proof/acceptance.py`: `58a1742d0a77518b02eff3a5eea262de5ab6dc2fc22320c22d826c6a091e22d6`
- `docs/features/coding-harness-alignment/proof/assessment-schema.json`: `7060fce480404500019f0a88ddcc6871b0d68f2feeed4a25ccbcab13a7d27a6c`
- `docs/features/coding-harness-alignment/proof/cases.json`: `4cfda640eecd02b68513bb058698275f27b88a98a9822445af9a3661c03cae66`
- `docs/features/coding-harness-alignment/proof/run.sh`: `4110946abc9f6d391ad1c7715e321f6c52e06af7dcc299805934fcb0a1086436`

## Exercise and official capture protocol

Generate the complete candidate with `python3 docs/features/coding-harness-alignment/proof/acceptance.py snapshot`. Give a fresh exercise agent only the six prompts and current instruction access; preserve its exact request, responses, actual identity/history and instruction input versions. A different assessor compares the responses against unchanged rubrics and candidate and writes the schema-shaped report plus transcript digest. This independent proof author may assess; it cannot be the final reviewer.

Run official acceptance with `HARNESS_ALIGNMENT_ASSESSMENT=/absolute/path/to/report.json` and the shared `proof_run_capture --feature-dir docs/features/coding-harness-alignment --timeout-seconds 120 --note "current harness verification"`. The complete proof requires all eight groups PASS. Root separately retains regression results and obtains a fresh read-only final reviewer on the unchanged candidate. Old semantic reports cannot validate this revision.
