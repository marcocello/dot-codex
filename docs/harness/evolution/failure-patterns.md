# Harness Failure Patterns

Optional maintenance file. Use only when repeated harness failures or rollout evidence show that the harness itself should change. Do not use it for every feature, proof, or repair run.

## Pattern Template

```md
## <short pattern name>

- Evidence: <links, run bundle, failing command, or repeated transcript behavior>
- Root cause: <why the harness allowed it>
- Candidate fix: <skill, script, doc, test, or config change>
- Regression risk: <what could get worse>
- Status: open | fixed | rejected
```

Use `scripts/harness_review` to summarize current proof bundles and pending harness change manifests before deciding which pattern deserves a harness change.
