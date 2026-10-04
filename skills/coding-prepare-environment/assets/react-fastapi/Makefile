export UV_PROJECT_ENVIRONMENT := $(CURDIR)/.venv
PYTHON := $(CURDIR)/.venv/bin/python
DEV_COMPOSE := docker compose -f compose.yaml -f compose.dev.yaml

.PHONY: setup db migrate backend frontend check up down smoke logs status dev-ready

setup:
	python3 scripts/setup.py
	uv sync --project backend --frozen
	npm --prefix frontend/app ci

db:
	$(DEV_COMPOSE) up -d --wait db

migrate:
	cd backend && "$(PYTHON)" -m alembic upgrade head

backend:
	cd backend && "$(PYTHON)" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	npm --prefix frontend/app run dev

check:
	cd backend && "$(PYTHON)" -m ruff check .
	cd backend && "$(PYTHON)" -m pytest
	npm --prefix frontend/app run check
	npm --prefix frontend/app run build

up:
	python3 scripts/setup.py
	docker compose up --build -d --wait

down:
	docker compose down

smoke:
	python3 scripts/smoke.py http://127.0.0.1:$(or $(WEB_PORT),8080)

# Idempotent prerequisite for host development and VS Code.
dev-ready: setup
	$(MAKE) db
	$(MAKE) migrate

logs:
	docker compose logs --follow --tail=100

status:
	docker compose ps
