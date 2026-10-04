# Feature proof integrity

Correct the completion flaws identified in the harness review without adding workflow stages.

## Acceptance criteria

- Shared proof captures automatically bind the referring feature contracts and coverage mappings. New or changed promises cannot be completed using a run that predates them.
- Completing one mapped feature checks its required packages and shared supporting regressions, without requiring unrelated features in the same round to remain current. Whole-round checks still validate all covered features.
- Successful completion automatically stores a compact portable history record. History remains readable without raw local evidence; new completion still requires current raw evidence. Altered or mismatched history records are rejected.
- Fixture helpers are reusable without inheriting their tests; each regression suite runs once in the combined proof.
- Evaluation guidance permits the same agent to author and implement. Criterion IDs identify assertions in normal test output, without another mapping file or mandatory agent.

These changes are explicitly authorized even where they change older behavior. Existing evidence is retained, not relabeled or fabricated.
