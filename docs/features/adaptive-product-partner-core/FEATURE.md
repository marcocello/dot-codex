# Adaptive Product Partner Core

## Goal

Establish one active adaptive shaping authority for all product input, with explicit handoffs to separate delivery skills and no global technology defaults.

## Behavior

- `coding-product-partner` is the single shaping entry for rough or detailed input, one outcome, several possible outcomes, and app-level decisions.
- The partner inspects current repository and authoritative external context before asking, then actively dissects and expands the problem, users, benefit, evidence, assumptions, constraints, material unknowns, implications, and recommended direction.
- Discovery examines three connected lenses by default: the underlying unknowns; the affected user's context, journey, expectations, friction, trust, and observable outcome; and the technical architecture, ownership, data, integrations, implementation risks, compatibility, operations, and likely change surface.
- It asks focused grouped questions whenever answers can materially clarify or expand those lenses. Discovery may continue across multiple turns when each answer reveals a new consequential unknown or implication; after every round it resynthesizes what changed and stops when the outcome is decision-ready, not after a fixed number of rounds.
- Each material decision has meaningful alternatives, consequences, and a recommended default; reversible implementation details are inferred and disclosed. Clear requests still proceed without artificial questioning.
- The partner performs deep analysis but responds as a concise practical working brief: what it understands, the direction it recommends, what remains missing or undecided, and the focused questions. It omits empty sections, raw reasoning, generic commentary, and repeated context.
- The default discovery response fits on one screen: one recommended direction, only the highest-value implications or gaps, and a short grouped question list. It expands only when the user asks or consequence and risk require more detail.
- When the request is already clear, the partner states material assumptions and the recommended next action, then proceeds within the existing authorization instead of forcing a discovery template.
- It classifies material discoveries as current behavior, prerequisite, follow-up, alternative, or unrelated. Only accepted outcomes and required prerequisites expand durable artifacts or implementation scope.
- Architecture is selected from repository context, accepted constraints, current authoritative evidence, and stack/domain skills. The global partner does not prescribe React, OpenAI, or another technology solely because a project is greenfield.
- `APP.md`, `ARCHITECTURE.md`, feature packages, proof packages, and queues are created only when they own durable accepted decisions. A material feature still receives realistic proof through `coding-proof-author`; a clear isolated repair remains local.
- A planning or specification-only request stops after the requested contracts. A clear isolated defect routes to `coding-repair`. One implementation-authorized material feature routes through `coding-proof-author` and then `coding-feature-execute`. Several accepted features receive separate proof packages and use `coding-autonomous-execute` only when serial keep-going execution is authorized; `coding-feature-queue` remains optional durable coordination.
- Preflight and final review remain owned by the decomposed delivery lifecycle. The partner does not bypass delivery review or completion requirements.

## Constraints

- Preserve explicit implementation authorization, safety approvals, dirty-tree protection, one accountable parent, serial feature execution, realistic proof, and truthful completion.
- Preserve separate proof authoring, implementation, review, repair, and optional autonomous delivery skills.
- Do not convert adjacent exploration into a speculative backlog or mandatory artifact set.
- Do not impose a one-round or two-round question cap, ask isolated low-value questions, repeat resolved questions, or use open-ended conversation as a substitute for investigation and recommendations.
- Do not expose chain-of-thought, produce long analysis dumps, restate the entire request, or bury decisions and questions under explanatory prose.
- Keep the active repository gate green by migrating tests that consume the retired shaping skills; do not preserve obsolete exact-phrase contracts merely to keep their filenames.

## Non-Goals

- Consolidating delivery into one skill.
- Changing preflight, final review, proof capture, repair, or queue semantics; those belong to the decomposed delivery lifecycle feature.
- Proving comparative model behavior; representative semantic replay is owned by `product-partner-behavioral-evals`.
- Rewriting historical feature evidence solely to use the new partner name.
