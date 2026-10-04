# Reusable proof inputs

Keep feature-linked acceptance and shared journeys while avoiding reruns caused by unrelated changes. A shared check may declare its inputs once; round completion checks the recorded inputs and feature contracts without imposing another whole-repository snapshot.

## Acceptance criteria

- A check may store repository-relative `scope` and optional `include` paths in `proof/inputs.json`. Captures reuse them automatically; CLI paths extend them. Checks without declared scopes retain whole-repository capture.
- Relevant source, shared dependencies, acceptance inputs, configuration edits, additions and deletions invalidate evidence. Invalid scope configuration fails clearly before running the check.
- New round receipts stay current after unrelated changes when all selected evidence is scoped, but reject changed feature contracts/mappings, relevant inputs, failed/newer attempts, missing coverage, mismatched targets and altered evidence. Any broad selected check remains broad.
- Existing version-1 rounds retain their original whole-repository validation. Retained history is not rewritten.
- Instructions place the promise in FEATURE, criterion links in COVERAGE, and execution/boundary details in shared PROOF, without requiring repeated prose or new workflow stages.
