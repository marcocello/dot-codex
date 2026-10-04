---
name: code-verify
description: Demonstrate coding outcomes at their real consumption boundary, including browser, API, CLI, persistence, and recovery checks. Use when completion needs evidence beyond compilation or unit tests.
---

# Verify

Choose a check that could disprove the promised outcome. Establish the target revision, configuration, runtime, initial state, action, and observable result. Use the project's existing tools and relevant ordinary failure cases; no standard test pyramid or mandatory test count.

Verify through the consumer. A UI claim needs interaction; a saved-state claim needs read-back after reopening or restart; a package claim needs the built artifact outside the source tree. Distinguish simulated dependencies from real integration checks. For browser or terminal work, read [interactive checks](references/interactive.md) when needed.

Use isolated fixtures for destructive or write-producing checks. Preserve existing data and running tasks. Inspection or verification scope does not authorize deployment, paid calls, or writes to a shared environment. Reuse already granted authority and keep doing unaffected work when one check is unavailable.

Keep the evidence proportionate: command or interaction, target, observed result, and limitations. Retain logs or screenshots when they explain a failure or support later diagnosis; don't create a parallel evidence registry. Relevant changes invalidate earlier results. Report a check that could not run as unverified, never as a pass. Fix an authorized defect and rerun the affected checks; otherwise report it.
