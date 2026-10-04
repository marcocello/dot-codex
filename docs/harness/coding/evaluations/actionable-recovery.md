# Actionable recovery guidance review

## Motivating evidence and scope

On 2026-10-01 the user supplied a partial prior exchange: a datastore export failed because configuration was missing; after correcting configuration, the agent encountered a missing quiesce phase record and ended with a warning and a statement that scripts needed repair. The user explicitly requested fixing the lack of proactivity, solution, and clear ownership. The full migration conversation, local source, and runtime were not inspected here; historical runtime claims remain unverified.

This change updates Runtime Ops and Repair guidance only. A technical prerequisite must remain agent-owned within authorized work; a necessary stop must identify the remaining action, owner, stopping reason, and recovery verification. Adoption of manual workflow state must validate invariants rather than bypass guards. Read-only requests and external mutation permissions remain bounded.

## Validation and limits

Both skills passed the skill-creator metadata validator. The repository gate passed. These checks establish structural validity only.

An independent fresh worker read both candidate skills and evaluated two raw scenarios without receiving an intended answer: an authorized local datastore workflow repair encountering a missing phase record, and a production duplicate-notification investigation explicitly limited to read-only work. The worker continued local investigation and repair in the first case while withholding cluster/export execution; in the second, it continued read-only correlation and assigned proposed operational recovery to the operator. It correctly refused to invent a runnable migration command without source investigation.

The worker identified ambiguous existing wording about live read-back and routing to Repair. The final revision explicitly distinguishes diagnosis completion from remediation completion and restricts repair routing to authorized repair. That final clarification passed structural validation; the scenario trial was not repeated.

This was a scenario decision check, not an executable migration trial or a baseline/candidate behavioral comparison. It does not establish improved reliability, prove implementation persistence, or resolve the actual datastore incident. The review used only the supplied partial conversation and retained this concise assessment rather than copying private migration dialogue.
