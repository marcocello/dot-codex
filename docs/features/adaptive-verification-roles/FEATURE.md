# Simple specification-driven delivery

User correction: remove the risk levels and role policies added in the previous implementation. Route the request to the appropriate skill. Feature delivery rests on narrow vertical specs, executable acceptance tests, and a few shared journey/behavior proofs. Known fixes remain lightweight.

## Acceptance criteria

- No risk classification, mode selection, rationale, or separate agent is required for acceptance authoring, implementation, or checking completion.
- Receipt commands require only the actual implementer; optional author/reviewer attribution records delegated work. New receipts contain no risk policy fields.
- Standalone and shared-round completion still reject stale, failed, incomplete, tampered, or mismatched evidence and wrong ownership. Existing receipt history remains readable.
- Specs define one small demonstrable outcome and its acceptance tests before implementation; shared journeys cover several features without duplicated full suites. Questions and fixes do not automatically become feature workflows.

This replaces the previously accepted risk-policy design at the user's explicit request. Prior captures preserve that historical contract and its results.
