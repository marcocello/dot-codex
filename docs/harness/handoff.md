# Handoff

Short. Outcome first. No transcript.

```text
Outcome: <done behavior>
Completion: DONE|IN PROGRESS|BLOCKED
Changed: <max five groups>
Proof: <command> -> PASS|FAIL|NOT RUN
Review: PASS|FINDINGS|NEED_INPUT|NOT APPLICABLE
Runtime: ACTIVE PROVEN|SOURCE PROVEN; ACTIVATION REQUIRED|NOT APPLICABLE
Activation: none|<exact rebuild/restart/deployment step>
Gaps: none|short list
Blocker: none|exact input/action
```

Omit run IDs, prompts, tokens, tool metadata, thread IDs, and exhaustive files unless audit is requested.

When an existing runtime is the named consumption target, source proof is intermediate and cannot be reported as `DONE`. Continue safe local activation or report `BLOCKED` with the exact approval or external dependency.
