---
name: code-release
description: Prepare, publish, and verify a requested software release or deployment using repository conventions. Preparation alone does not authorize commits, pushes, publication, or external messages.
---

# Release

Read the repository's release procedure and scripts before running them; a seemingly local command may commit, tag, push, or publish. Reuse its versioning, package manager, CI, and deployment target. Don't import Pi's lockstep versions, branch rules, or release commands.

Prepare a concrete candidate: relevant checks, user-facing changes since the actual previous release, migration implications, and rollback or recovery path. Build and exercise the distributable outside the source checkout. For the SSH web starter, use the generated project's deployment instructions and verify the served app and database path.

Proceed through every release action already authorized. Keep unrequested actions as prepared local results; ask only for missing consequential authority or target information. A request to commit does not authorize push; a review or implementation request does not imply either. Stage only the intended files and inspect the staged diff without disturbing others' changes. Post no comments or announcements without explicit authorization.

After publication, read back the exact version or deployment from the consumer. A successful build, tag, upload, or CI job alone may not establish availability. On partial failure, inspect what reached the registry or host before retrying; reuse safe recovery for that release instead of bumping another version blindly. Report preparation, publication, and runtime verification separately when their results differ.
