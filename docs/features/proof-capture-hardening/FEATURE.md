# Proof Capture Hardening

## Goal
Make official feature-proof attempts mechanically trustworthy by exercising the real capture supervisor and rejecting proof runners that mutate their own accepted proof inputs.

## Behavior
- A successful proof runner produces a retained `PASS` with its output and pre-run contract copies.
- A non-zero proof runner produces `FAIL` and preserves the runner return code.
- A timed-out or interrupted runner produces the corresponding retained terminal status and cleans up its process group.
- Invalid or escaping feature paths, accepted-input targets, and attempt directories plus missing or non-executable runners fail clearly without a misleading passing attempt or outside-repository write.
- At runner exit, independently baselined content, mode, inode, and change time for `FEATURE.md`, `PROOF.md`, `proof/run.sh`, and their retained pre-run copies must still match. Ordinary writes, replacements, or direct overwrite-and-restore attempts that change this state make a would-be pass `FAIL` and name the surface.

## Constraints
- Tests exercise the real `scripts/proof_run_capture` executable in temporary repositories with real subprocesses and signals.
- Mutation detection uses supervisor-memory state independent of repository-writable retained files and observes content, mode, filesystem identity, and change metadata without adding persisted hashes or receipts.
- Accepted proof inputs and the attempt base must use ordinary repository-contained paths without symlink components.
- This is accidental and ordinary runner-mutation containment, not an operating-system event monitor or protected filesystem trust root. Deliberate transient pathname or parent-directory substitution that restores the untouched original entry or tree is outside the accepted threat model.
- No hashes, receipts, implementation manifests, or target-project workflow stages are added.
- Existing exit semantics remain stable: runner status, `2` invalid input, `124` timeout, `125` cleanup failure, and `128+signal` interruption; proof-input mutation uses capture failure code `126` only when the runner would otherwise pass.

## Non-Goals
- Judging whether a feature proof scenario is semantically realistic.
- Binding a completed feature to a Git commit or implementation snapshot.
- Detecting a malicious same-user runner that temporarily substitutes a pathname or parent tree and perfectly restores the untouched original entry, or otherwise rewrites both implementation and proof adversarially.
- Generic secret redaction or retained-output size limits.
