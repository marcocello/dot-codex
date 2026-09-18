# Blind execution protocol

Read current on-disk AGENTS.md, docs/harness/workflow.md, docs/harness/coding/rules.md and the actual skills relevant to each assigned case. Do not read this feature's FEATURE.md, PROOF.md, oracle.json, other executor outputs, or expected judgments. The coordinator supplies case IDs; read their request and repository/runtime context from cases.json. Treat context as investigated facts for this bounded isolated exercise.

For each case, produce the next user-visible response and an ordered external decision/action trace of what you would actually do next under these instructions. Include exact skill announcements, questions (if any), Goal tool actions/objective (if any), work you proceed with, verification and stopping condition. This is an isolated decision exercise: do not modify another project, create real exercise Goals, or perform external mutations. Do not include hidden chain-of-thought. A short concrete list of externally observable actions is sufficient.

Save a JSON object with executor identity, the candidate SHA256 map supplied by coordinator, and `cases`: list of objects containing `id`, `response` (string), `actions` (list of strings), `stop_condition` (string). Do not self-grade or attempt to infer a preferred answer. Work only on assigned cases. Save to the coordinator's requested evidence path.
