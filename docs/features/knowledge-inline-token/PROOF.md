# Inline token acceptance

## Done and command

`bash docs/features/knowledge-inline-token/proof/run.sh` must pass from the checkout. This independently authored proof uses Python 3.11+ on POSIX and synthetic credentials only. Frozen before implementation; implementation must not modify acceptance inputs.

## Boundary and scenarios

Producer: stdin token text or an explicitly selected existing credential reference. Activation: canonical profile CLI in separate processes. Owner: real profile validation, mutation, serialization and read logic. Consumers: fresh profile CLI processes, legacy launchers and real provider API command entrypoints. Durable read-back: TOML parsed independently and file permission bits checked. Unsafe edge: network only, replaced through urllib opener responses; no real provider access.

- `test_inline_persistence_redaction_and_restart`: stores stdin token after whitespace trimming, reads actual token from TOML, verifies owner-only mode, preserves default and second profile, reopens through list/resolve/default/transport and legacy launchers with redaction, updates unrelated profile without destroying secret. Catches cosmetic acceptance with absent persistence, raw output leaks and redacted-value rewrites.
- `test_import_reference_and_preserve_other_profile`: imports environment then private file credentials, preserves auth type, transport/default/unselected profile, retains source file and permits idempotent inline import. Catches global credential scanning or destructive migration.
- `test_invalid_input_and_conflicts_are_atomic`: invalid/oversized stdin, mutually exclusive options, absent binding and nonremote target fail without configuration mutation. No raw token argv interface is accepted.
- `test_reference_replaces_inline_and_unsafe_config_rejected`: reference can replace inline binding; owner-unsafe inline files, symlink and FIFO rejected promptly. Catches stale dual credentials and blocking special-file reads.
- `test_inline_used_by_public_api_clients`: independently spawned HTTP-edge harness executes complete ClickUp and Notion `check` commands with saved inline profiles. Edge verifies exact synthetic Authorization headers; real parsing, resolving, transport and identity verification execute unchanged; output remains secret-free. Catches a store-only implementation that clients cannot consume.

## Proves / does not prove

Proves the public CLI storage/reuse/redaction contract locally, real serialization and safe permission handling, compatibility activation and authenticated consumption at the provider edge. Does not prove live SaaS identity, encryption, chat/history erasure, malicious concurrent filesystem races, or actual migration where this harness has no configuration. Instructional setup wording, ignored config policy and avoiding secret literals in tool arguments receive independent semantic review, not exact-phrase assertions.

## Evidence and false-green risks

Retain captured red and green proof runs separately. Freeze FEATURE.md, this document, runner, test_acceptance.py and api_edge.py hashes before implementation. The HTTP fake can establish headers and response consumption only; it cannot establish live provider access. Synthetic token never appears in successful tool output; failing assertions may reveal only synthetic fixture values. Future review must verify documentation and implementation do not log actual values outside these paths. No proof imports another feature's suite or edits implementation.
