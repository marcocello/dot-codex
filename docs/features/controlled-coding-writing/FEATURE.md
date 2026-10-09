# Controlled coding writing

Use a shared STE-inspired writing reference during coding work. Existing coding skills load the same reference for specifications, acceptance tests, reports, explanations, and human interaction.

## Acceptance

- AC1: Every repository-owned `skills/coding-*/SKILL.md` links to one readable writing reference and instructs the agent to apply it. No new skill or inventory dependency is required.
- AC2: The reference covers specifications, proof plans and reports, and questions and handoffs. Examples preserve requirement strength, uncertainty, actor, conditions, quantities, and observation boundaries. Missing product decisions stay explicit.
- AC3: The reference preserves code, commands, identifiers, paths, quoted errors, and user language/style choices. It identifies the approach as an adaptation and does not claim ASD-STE100 compliance or introduce a mandatory language gate.
- AC4: The proof contract and README expose the same reference. Existing acceptance, authority, lifecycle, and completion rules remain unchanged.

## Decisions and boundary

The user accepted the proposed shared-reference design with “Proceed.” Use an STE-inspired coding adaptation by default. Full STE compliance is a separate explicit request and requires the authoritative standard and suitable review. Do not install or vendor the upstream skill, dictionary, or checker. Its inspected revision is `1e148d670cba46685ad2b4c3f2354a637a7fdbbe`.

Installation can be checked through local CLI reads and existing metadata validation. Review meaning preservation directly and retain a bounded fresh-agent writing exercise. These checks do not establish automatic reference loading in a future task or universal model reliability. The baseline gate has an unrelated tracked-artifact failure in two outcome-continuity vendor fixtures.
