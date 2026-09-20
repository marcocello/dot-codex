# Delivery evidence

Task: 01a0b606-aaba-72b2-8b87-e012fffbe543. Native scoped Goal: separate configuration from provider operations and verify profile-isolated Notion API access. Implementer: /root. Independent proof/semantic author: /root/connect_proof. Fresh final reviewer: /root/connect_final_review. Original dialogue remains in native task history; lifecycle capture is partial, with no copied private conversation.

## Result and boundary

knowledge-config owns setup questions, persistent profiles/defaults and resolution. knowledge-connect owns provider references, ClickUp and Notion MCP instructions, direct API clients and shared private credential loading. Capture/review delegate resolved remote profiles. Missing setup retains pending intent and asks; explicit none and Markdown do not connect remotely. The old ClickUp CLI delegates to the new canonical client. The retired fixed-token Notion CLI remains disabled with updated migration guidance.

Target is checkout CLI/instruction behavior with synthetic HTTP boundaries. No real credentials, live MCP session, SaaS state, mutations or deployment verified. API helpers expose documented bounded capabilities, not arbitrary provider endpoints.

## Captured verification

- Initial official red: proof/runs/20260919T090826802293Z (missing new client).
- Final official PASS: proof/runs/20260919T091422243937Z.
- Existing ClickUp public CLI regression PASS: tests/runs/20260919T091241295951Z.
- Existing profiles and retired-entrypoint regression PASS: tests/runs/20260919T091405738679Z.
- Canonical clients, malformed read-back/cursor/identity cases, redirect refusal, profile edges and skill validation PASS: tests/runs/20260919T091422509118Z.
- Independent semantic assessment: ../SEMANTIC-ASSESSMENT.md, PASS; frozen hashes unchanged, no fixture repairs.
- Repository gate PASS before completion; completion metadata gate recorded in native tool history.
- Inventory add synchronized knowledge-connect. Doctor reports only existing absent sites@openai-bundled; unrelated to this feature and no installation attempted.

Read-only review identified malformed read-back risks: null text object losing known page ID, boolean equal to numeric value, and missing option name mistaken for null. Guards now reject these; known page ID is retained. Supporting regressions are distinct from frozen acceptance.

## Used skill versions

- skills/.system/skill-creator/SKILL.md: `6656e54755638e8efcf275a472b9672eaa8a9a1b9e59dc210e275b03b59e1e66`
- skills/coding-shape/SKILL.md: `92ba8e97a2de90163091d94b7bdf7d3cf8e817f97fb81634038edbaca0ed029d`
- skills/coding-ship/SKILL.md: `6d9b4a62415c69804a78816f118cfdbe9f87876999747a4405fa0925cd960c8c`
- skills/coding-fix/SKILL.md: `7d1d8e041496c8ea07924c154fa36051eac14a62f9ebd698c85047847533cf35`
- skills/harness-manage-skills/SKILL.md: `926270cd55ad8440b2d36a425e68618702799b131867514413794757ac999463`
