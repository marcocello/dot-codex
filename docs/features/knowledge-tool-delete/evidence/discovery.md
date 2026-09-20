# Discovery

User request in native task 01a0b606-aaba-72b2-8b87-e012fffbe543: rename integration skill to knowledge-tool-connect or knowledge-connect-tool; implement ClickUp object deletion. Selected knowledge-tool-connect. Announced task/subtask initial scope after offering optional scope clarification, with public Docs/page deletion unavailable. No request to delete actual remote objects.

Official provider references inspected 2026-09-20:
- https://developer.clickup.com/reference/deletetask : DELETE /api/v2/task/{task_id}, 204 response.
- https://developer.clickup.com/docs/mcp-tools : delete-task handles tasks/subtasks; actual installed capabilities still must be discovered.
- https://developer.clickup.com/llms.txt : Docs endpoints cover search/create/fetch/page listing/page get/create/edit; no documented Doc/page delete endpoint. Do not manufacture API support or clear content as deletion.

Compatibility surfaces: canonical scripts move; old knowledge-connect/scripts remains usable; shared and knowledge-config launchers updated; inline and reference credentials and profile storage untouched. Historical knowledge-unified proof has exact old setup skill assertions superseded by the rename; retain its history, prove new routing independently.

Local development validation uses synthetic credentials and fake outer HTTP edge only, not a live ClickUp account. Original dialogue remains in native history; this is partial evidence capture.
