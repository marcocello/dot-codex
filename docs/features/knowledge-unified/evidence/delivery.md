# Unified skill delivery

Task 01a0b606-aaba-72b2-8b87-e012fffbe543. Matching native Goal consolidates connection/setup and supports user-chosen chat-token intake. Implementer /root, independent proof/semantic author /root/unified_proof, fresh final reviewer /root/unified_review. Dialogue stays in native history; evidence capture is partial.

## Delivered surface

knowledge-connect owns canonical profile resolver, setup reference, shared/local references and provider clients. knowledge-config is removed from skills.toml and its SKILL/UI entrypoints retired; legacy resolver/ClickUp CLI launchers remain. Current consumers and setup-required referral point to knowledge-connect.

Token guidance uses user-provided ClickUp Settings → ClickUp API → API tokens. Chat paste is a supported voluntary input, with conversation-retention explanation, no echo, no shell arguments/repository storage, permission-aware private storage and honest fallback when no suitable tool exists. No actual token provided or stored in this change.

During inspection the checkout already contained new ClickUp Docs/page implementation from another completed task. This was preserved; current capability documentation is used instead of stale unsupported-Docs statements. Notion body/block, unsupported ClickUp comments/attachments/deletion and OAuth enrollment limitations remain explicit.

## Verification

- Frozen initial red: proof/runs/20260919T191522109737Z.
- Official final PASS: proof/runs/20260919T191537126899Z.
- Routing compatibility PASS: tests/runs/20260919T191537134973Z.
- Notion API PASS: tests/runs/20260919T191537122735Z.
- Existing ClickUp Docs supporting suite PASS: tests/runs/20260919T191537142536Z.
- Legacy profile compatibility PASS: tests/runs/20260919T191554257986Z.
- Public API setup referral and relocated instruction links PASS: tests/runs/20260919T191637380144Z.
- Historical ClickUp suite retained at tests/runs/20260919T191550855351Z: all provider-operation cases pass, sole failure is frozen assertion requiring error.skill=knowledge-config. This expected identity was deliberately superseded by this feature. Historical proof is not edited; new independent proof and API referral check verify knowledge-connect instead.
- Independent semantic acceptance PASS: semantic-review.md; frozen hashes unchanged.
- Skill validation and repository gate PASS; status-only completion gate in native history.
- Inventory doctor still reports existing sites@openai-bundled absent; unrelated to this removal, no installation attempted.

No live plugin installation, real credential input/storage, external writes or SaaS verification. Tests validate synthetic/local CLI behavior and written guidance, not future model compliance. No commit/push. Unrelated dirty work preserved.

## Used skill versions

- skills/coding-shape/SKILL.md: 92ba8e97a2de90163091d94b7bdf7d3cf8e817f97fb81634038edbaca0ed029d
- skills/coding-ship/SKILL.md: 6d9b4a62415c69804a78816f118cfdbe9f87876999747a4405fa0925cd960c8c
- skills/.system/skill-creator/SKILL.md: 6656e54755638e8efcf275a472b9672eaa8a9a1b9e59dc210e275b03b59e1e66
- skills/harness-manage-skills/SKILL.md: 926270cd55ad8440b2d36a425e68618702799b131867514413794757ac999463
