---
name: code-explore
description: Investigate unfamiliar code, issues, or architectural choices and return a focused map or implementation proposal. Use for discovery and planning; exploration alone stays read-only.
---

# Explore

Find the smallest part of the system that explains the user's question. Start with repository instructions, the relevant entry point, and existing checks; trace the actual producer, state changes, and consumer. Distinguish the reported symptom from a proposed cause. For issues, inspect available discussion and linked changes without assigning, labeling, or commenting.

Return the useful context: concrete paths and symbols, how the path works, the evidence behind the finding, and the next useful change or unanswered decision. Read enough surrounding code to test your interpretation; avoid a repository tour or large code dumps. Label hypotheses and access gaps.

When asked for a plan, recommend a small usable outcome and explain how to demonstrate it. Separate consequential product choices from routine engineering decisions. A plan is a proposal, not new authority to implement. If implementation is already requested, continue once its material choices are settled.

For a large investigation, use available native delegation only when an independent question benefits from it and session instructions allow it. Give each investigator a bounded question; return findings to one accountable owner. This skill does not require a scout/planner/worker chain or a new document.
