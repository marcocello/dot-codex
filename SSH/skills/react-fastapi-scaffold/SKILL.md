---
name: react-fastapi-scaffold
description: Bootstrap new web apps using SSH's React, FastAPI, PostgreSQL, and Docker starter. Use for greenfield scaffolding; preserve established projects and explicit stack choices.
---

# React + FastAPI scaffold

Use this starter by default for a new web application. Stack selection is already settled: React/TypeScript/Vite, Tailwind with shadcn-style owned components, FastAPI, SQLAlchemy/Alembic, PostgreSQL, and Docker Compose with Caddy. npm and uv own dependencies. Single-host deployment is the baseline.

Create the project with `python3 <this-skill>/scripts/scaffold.py /path/to/new-project`. The target must be absent or empty; the script refuses to merge into existing work. Read the generated [README](assets/template/README.md) for runnable commands and deployment details. Dependencies and private environment files are created in the generated project, never in the template.

Build the requested product on the included notes slice, replacing its demo vocabulary and behavior. Use `backend/app` for API and persistence, `frontend/app/src` for UI, and Alembic for schema changes. Add service modules when business logic warrants them. Keep requests on the same `/api` origin. Preserve lockfiles and migrations.

Don't ask which framework, package manager, folder layout, database, or deployment format to use. Explicit user choices and existing project conventions override these defaults. Ask only for missing product intent or consequential decisions that the scaffold cannot supply, such as who may access real data. The demonstration has no application accounts or authorization; production includes a shared access gate. Resolve product access control before exposing private data or public writes.

Run the generated checks and exercise a save followed by a reload against real PostgreSQL. The smoke script writes a note: use a disposable local instance or an explicitly authorized test environment. Prepare deployment files by default; publishing requires an authorized target and credentials. Add capabilities when the product needs them, without importing the parent harness's lifecycle machinery.
