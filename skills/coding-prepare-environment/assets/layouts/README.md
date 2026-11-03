# Repository layout examples

Choose the smallest structure that makes component ownership, runtime wiring, and verification clear. These examples describe placement; they are not runnable applications or a requirement to create every listed file. Preserve an established repository layout unless a concrete restructuring is authorized.

| Situation | Example | Placement decision |
| --- | --- | --- |
| One API, bot, or background application | [Single service](single-service.md) | Keep one named component without inventing a frontend. |
| A browser app and an API | [Web and API](web-api.md) | Frontend/backend can name the actual applications; the existing React/FastAPI scaffold remains valid. |
| A supplied full-stack website, an integration, APIs, and automation workflows | [Mixed components](mixed-components.md) | Use named components; keep feature-specific source and utilities together even when they execute in another component. |

Each component owns its source, dependencies, build, tests, and component-specific setup or utilities. `deployments/` selects and connects components for each environment; genuinely shared deployment helpers can remain there. Docker services and source components need not map one-to-one: a component may run setup jobs, and an assembly may use standard database images.

The examples use `local` and `prod` as environment names. Preserve an existing `dev` environment or another accepted name, including the bundled scaffold's `dev`. Optional README files, containers, VS Code tasks, Python environments, and deployment files are created only when needed by authorized work. Keep credentials, supplied private data, dependencies, and generated artifacts out of Git according to the owning skill's policy.
