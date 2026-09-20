# Delivery evidence

Owner/native task: `01a0b606-aaba-72b2-8b87-e012fffbe543`. Matching native Goal covers rename and scoped ClickUp deletion. Implementer `/root`; independent acceptance/semantic author `/root/tool_delete_proof`; fresh final reviewer `/root/tool_delete_review`. Original dialogue remains native; partial capture here.

Canonical integration is `knowledge-tool-connect`; active instructions, inventory and setup errors use the new name. Existing knowledge-connect script paths use a Git-visible compatibility symlink. Profile data/location and credentials unchanged. New `delete DESTINATION TASK_ID` verifies scope before one DELETE and requires subsequent HTTP404 to report success.

Official RED before implementation: `../proof/runs/20260920T125543271712Z`. Latest official PASS: `../proof/runs/20260920T125646515420Z`. Frozen acceptance unchanged.

Affected regressions PASS: `../tests/runs/20260920T125708063511Z` (inline credentials, routing, Notion, ClickUp Docs), `../tests/runs/20260920T125747792494Z` (existing ClickUp provider task behavior). Historical exact setup-owner assertions in older unified/ClickUp contracts intentionally superseded by new first-use rename acceptance; those history files are unchanged.

Skill validator and repository gate PASS. Inventory doctor reports pre-existing unrelated `sites@openai-bundled` not installed; no unrelated plugin installation attempted. No stale old-name references in active routing surfaces.

Boundary: synthetic credentials/temp profiles and a controlled outer HTTP edge, real parser/client/transport. No live SaaS deletion or credential validation. Public Docs/page deletion lacks a documented endpoint; no container, bulk or Notion deletion added. New skill discovery may require a fresh task if current host cached its catalog.

## Frozen input and selected skill hashes

- `docs/features/knowledge-tool-delete/FEATURE.md`: `87f1ac62d1802c611dedb9b9605de9314b6545e53beceb834c3f0526c99d9e39`
- `docs/features/knowledge-tool-delete/PROOF.md`: `2f472ec96ed618b4a525d10c8dae5a6bdb5b8259e64cb904ee85b59a72d2cc34`
- `docs/features/knowledge-tool-delete/proof/api_edge.py`: `76a441e35f17d1c81dbbe27324b78d369a668277147504390416780c9d07eac6`
- `docs/features/knowledge-tool-delete/proof/test_acceptance.py`: `0cb4409ed481e54a93e00656c53fad0ae24a33beeeb9c323a1695acd97541ed1`
- `docs/features/knowledge-tool-delete/proof/run.sh`: `baf2fb0eb6a6d11315bab72b9314f432b8755180f89c92c080222d7601846655`
- `skills/coding-shape/SKILL.md`: `92ba8e97a2de90163091d94b7bdf7d3cf8e817f97fb81634038edbaca0ed029d`
- `skills/coding-ship/SKILL.md`: `6d9b4a62415c69804a78816f118cfdbe9f87876999747a4405fa0925cd960c8c`
- `skills/.system/skill-creator/SKILL.md`: `6656e54755638e8efcf275a472b9672eaa8a9a1b9e59dc210e275b03b59e1e66`
- `skills/harness-manage-skills/SKILL.md`: `926270cd55ad8440b2d36a425e68618702799b131867514413794757ac999463`
