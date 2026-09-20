# ClickUp API source boundary

Official documentation fetched 2026-09-19 for this implementation:

- [Authentication](https://developer.clickup.com/docs/authentication): personal token as Authorization value; existing OAuth access token as Bearer value. This client consumes existing credentials and does not implement OAuth enrollment.
- [Authorized user](https://developer.clickup.com/reference/getauthorizeduser) and [authorized workspaces](https://developer.clickup.com/reference/getauthorizedteams): authenticate identity and workspace access before content operations.
- [Spaces](https://developer.clickup.com/reference/getspaces) and [list](https://developer.clickup.com/reference/getlist): verify configured destination membership using the workspace's spaces and list metadata.
- [Task pagination](https://developer.clickup.com/reference/gettasks): page starts at zero; explicit include_closed, subtasks and include_timl are needed for broader candidate coverage. Only accessible records are visible; complete pagination cannot establish absence of inaccessible tasks.
- [Create task](https://developer.clickup.com/reference/createtask): enforce required custom fields; create supports name, description, status, priority and date inputs. Custom-field creation requirements can still block a core-only create; report that limitation.
- [Update task](https://developer.clickup.com/reference/updatetask) and [get task](https://developer.clickup.com/reference/gettask): updates are partial; GET supports Markdown descriptions. Custom fields need a separate endpoint.
- [Custom fields](https://developer.clickup.com/docs/customfields) and [set value](https://developer.clickup.com/reference/setcustomfieldvalue): validate types and dropdown option IDs and check applicability. Plan and access limits still apply.

No live account or content was accessed during research. HTTP fakes in acceptance replace only the external service; live provider behavior and actual credentials remain unverified.
