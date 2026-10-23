# How to Build Software When AI Writes the Code

**PhD course syllabus | Winter 2026 / Spring 2027 | 20 contact hours | English**  
**Instructor:** Marco Cello  
**Contact:** marco.cello@followups.run  
**Proposed format:** Five four-hour meetings with short explanations, live demonstrations, guided labs, and group review. The formal exam would be scheduled separately from the 20 contact hours.

## Course purpose

AI coding agents can implement substantial software changes, but people still have to decide what the software should do and whether it works. This course teaches students to turn a research need into a small running application, direct an AI coding agent, and evaluate the result with observable evidence. Students will practice on a prepared application so they can focus on engineering decisions rather than framework setup.

Codex is the main lab tool. The methods apply to other coding agents. Examples from the instructor's engineering harness and remote development environment show how the same methods extend to larger projects. Operating a VM or writing Terraform is not a prerequisite or a lab objective.

## Intended audience and prerequisites

The course is for PhD students who can read and modify simple code but have limited experience with software engineering or AI coding agents. No prior knowledge of React, web APIs, databases, cloud infrastructure, or Terraform is required. Each student needs a laptop and access to an AI coding agent. The instructor provides a working starter repository and synthetic data.

## Learning outcomes

By the end of the course, students should be able to:

1. Describe a research workflow as a user goal, a bounded software change, and observable acceptance criteria.
2. Explain the roles of the interface, API, data store, repository, tests, and runtime in a small application.
3. Give a coding agent useful repository context, constraints, and a task with a clear stopping point.
4. Inspect an agent's changes and judge them with targeted code review, automated checks, and direct use of the running application.
5. Reproduce a failure, guide a repair, and retain evidence of both the failure and the verified result.
6. Identify decisions that require human control, especially those involving research data, credentials, external services, destructive actions, and deployment.
7. Hand over a small application with instructions that let another person run it and verify its main behavior.

## Common practical project

All students start from a small, local **Research Records** application with a browser interface, a Python API, a local database, synthetic records, and one working user flow. The starter runs with documented commands. Students can choose one bounded feature, such as importing records from a CSV file with clear error messages, filtering records by tag, or exporting a selected set. The same application is used across the five meetings. This keeps the lab comparable while leaving room for each student to make product and engineering decisions.

The course uses synthetic data. Students must not put unpublished research data, personal data, passwords, or access tokens into prompts or the shared lab repository.

## Teaching programme

| Meeting | Hours | Main question and topics | Guided lab and saved result |
| --- | ---: | --- | --- |
| **1. See the whole system** | 4 | What changes when an agent writes code? Tour a small application: user action, interface, API, storage, repository, and runtime. Introduce version control, a branch, a diff, and a repeatable local run. | Run the starter app, trace one action through it, and ask the agent for one tiny change. Save the changed repository state and show the behavior in the browser. |
| **2. Define what should happen** | 4 | Turn a research need into a small user journey. State the starting condition, action, expected result, failure behavior, and scope limit. Distinguish a feature request from an implementation instruction. | Write a one-page feature brief and acceptance checklist. Ask the agent to clarify or plan before implementation. Build the first vertical part of the feature and check it against the brief. |
| **3. Direct the agent within boundaries** | 4 | Give the agent repository context without burying it in instructions. Explain a simple architecture map, task boundaries, permissions, tool use, and when a reusable skill helps. Inspect the agent's proposed changes and revise the task when necessary. | Extend the feature across the interface, API, and data store. Save a short task instruction, an architecture sketch, the changed repository state, and a working local demonstration. |
| **4. Find false confidence and repair failures** | 4 | Compare unit, integration, and user-facing checks. Show how a test can pass while the real workflow fails. Cover stale results, wrong environments, data integrity, privacy, dependencies, and targeted review of high-risk code. | Test a seeded defect or incomplete feature. Record the observed failure, ask the agent to repair it, then rerun automated checks and the actual user journey. Save evidence of the failure and the verified repair. |
| **5. Evaluate, operate, and hand over** | 4 | Decide what evidence is enough for a small release. Separate local success from deployment. Explain reproducibility, known limits, and human approval for external actions. Use Codex on VM and Terraform as a short instructor case study. | Exchange applications with a peer for independent acceptance checks. Repair one finding. Present the running app, feature brief, check results, known limits, and steps to reproduce the result from a fresh checkout. |

Across the 20 hours, roughly one quarter is explanation and demonstration, more than half is guided practice, and the remainder is review and discussion. Each meeting adds to the same project rather than starting a new tool or application.

## Assessment

The exam follows the course proposal: multiple-choice questions and a practical assessment. The exam date and venue remain to be set.

| Component | Proposed weight | What it checks |
| --- | ---: | --- |
| Multiple-choice questions | 20% | Core concepts: task scope, application boundaries, evidence, false positives, permissions, data handling, and runtime claims. |
| Practical assessment | 80% | Specify, build, validate, and present one small feature or application using an AI coding agent. Students may use the course starter and receive a feature brief of comparable scope. |

**Practical marking guide (within the practical component):** 20% for a clear user goal and observable acceptance criteria; 30% for working behavior and a reproducible run; 30% for independent checks, failure analysis, and evidence; 20% for safe decisions, targeted review, and a clear handoff. The assessment rewards sound judgment and demonstrated behavior, not prompt length, generated code volume, or an unsupported claim that tests passed. A student should still receive credit for an honestly documented failure and a sound diagnosis, even if the feature is incomplete.

Students submit a repository or archive, a one-page feature brief, run instructions, a concise evidence record, and a short presentation. The evidence record identifies which checks ran, what was observed in the application, and what remains unverified.

## Instructor preparation

- Prepare and test the starter repository on the machines or environment students will use. Include one-command setup, synthetic data, and a known working baseline.
- Confirm agent access and usage limits before the first meeting. Keep a fallback account or paired-lab plan for access failures.
- Prepare three feature briefs of similar size, a seeded defect for Meeting 4, and a simple peer-check sheet for Meeting 5.
- Demonstrate one complete change before asking students to work independently. Keep the VM and Terraform material to a guided case study so the course does not become an infrastructure tutorial.

## Suggested reading and reference material

- [The Carpentries: Version Control with Git](https://www.carpentries.org/lessons/) for students who need a version-control refresher.
- [OpenAI: Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) for an example of repository-level agent context.
- [GitHub: About pull requests](https://docs.github.com/en/pull-requests/get-started/about-pull-requests) for the relationship between changes, review, and automated checks.
- [NIST: Secure Software Development Framework](https://csrc.nist.gov/Projects/ssdf) for a broader view of secure development and verification.

Tool-specific readings should be checked again before the course begins because agent products and their interfaces change quickly.
