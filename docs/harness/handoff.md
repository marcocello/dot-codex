# Handoff

Default to a short human receipt, not an execution transcript.

## Feature Or Issue Work

Use this order:

```text
Done: <issue>
Outcome: <one to three lines>
Changed: <grouped bullets, capped at five>
Verification:
- Primary proof: <command> -> PASS|FAIL|NOT RUN
- Gate: PASS|FAIL|NOT RUN
- Evaluator: PASS|FAIL|NEED_INPUT
Blockers: none | <exact user-owned input/action>
```

Use `Goal complete: <feature-id>` when a Goal was active. Use `Needs input: <reason>` when the
remaining requirement is user-owned or external after recovery.

Do not include run IDs, prompt text, token counts, tool metadata, internal thread IDs,
exhaustive file lists, or exhaustive skill lists unless the user asks for an audit appendix.

## Artifact Work

Use this order:

```text
Done: <artifact>
Outcome: <one to three lines>
Created/changed: <grouped bullets, capped at five>
Checks: <parser, syntax, contract, fixture, or narrow structural checks>
Live validation: PASS|NOT RUN|NEED_INPUT
Blockers: none | <exact user-owned input/action>
```

Do not imply an artifact is incomplete only because live validation was unavailable.
