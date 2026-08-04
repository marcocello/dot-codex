# Completion

Current passing proof: `proof/runs/20260803T154753414862Z` (`PASS`, 4 focused tests plus both native skill validators).

User corrections: `skills.toml` no longer records Git `revision` or plugin `version`, and it no longer declares Codex system skills or plugins from `openai-primary-runtime`. Git dependencies follow current provider `HEAD`; URL SHA-256 verification remains. Runtime-owned categories are supplied by Codex outside this inventory, and the manager rejects attempts to add them.

Live migration: `doctor` reports 52 healthy dependencies: 43 owned skills, 2 Git skills, and 7 user-managed plugins. The manifest contains no revision/version fields, no `system` kind, and no `@openai-primary-runtime` selector. Bento and Impeccable follow current upstream `HEAD`; Remotion remains native-plugin managed. The eleven prior raw Remotion directories remain recoverable at `.tmp/legacy-skill-backups/20260803-remotion/`.

Earlier immutable-pin and runtime-inventory behavior, proof strengthening, and symlink-containment repairs remain retained in prior proof attempts and evaluator history; both superseded behaviors are explicitly rejected by the current proof.

Repository gate: applicable Python, common, Git diff, and authored-skill checks passed. The overall gate remains nonzero only for four current provider-owned Bento/Impeccable metadata findings; rewriting downloaded content would break source fidelity, so the gate is skipped for those findings.

Managed evaluator: `PASS` for the corrected source-following and runtime-ownership boundaries; no blocking gaps remain.
