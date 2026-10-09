# Writing reference verification

## Done and command

Run `bash docs/features/controlled-coding-writing/proof/run.sh` from the repository root. Pass requires valid coding-skill metadata, readable canonical writing-reference links in every coding skill, and the same link in the proof contract and README.

## Observation

The public artifacts are the installed repository-owned skill files and shared documentation. The CLI reads those files, resolves their Markdown links independently, and validates metadata with the existing skill validator. An absent hook, unreadable guide, or broken link fails. No external service or application behavior is involved and no fake replaces the reference.

Review AC2 and AC3 directly against the source and realistic writing samples. Retain the request, actual output, assessment, and limitations in `evidence/writing-review.md`. The fresh worker receives the reference and writing tasks, without the evaluator's expectations. This is a bounded supplementary observation, not a statistical comparison or runtime loading guarantee.

## Limits

The executable check establishes artifact integration for AC1 and AC4. Semantic review establishes the guide's contents and meaning preservation for AC2 and AC3. A future model can still fail to follow the guidance. Style, sentence length, metadata, and a checker exit code do not establish application acceptance, factual accuracy, or formal ASD-STE100 compliance.

Run the repository gate separately. Retain its baseline failure; do not change unrelated fixtures to obtain a pass.
