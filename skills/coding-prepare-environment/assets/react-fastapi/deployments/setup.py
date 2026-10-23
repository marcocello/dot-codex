"""Create private configuration for the selected deployment environment once."""

import argparse
import os
import re
import secrets
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", choices=("dev", "prod"), default="dev")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    directory = root / "deployments" / args.environment
    destination = directory / ".env"
    content = (directory / ".env.example").read_text()
    password = secrets.token_urlsafe(32)
    slug = re.sub(r"[^a-z0-9_-]+", "-", root.name.lower()).strip("-_")[:30] or "app"
    project_name = f"{slug}-{args.environment}-{secrets.token_hex(3)}"
    content = content.replace(
        "COMPOSE_PROJECT_NAME=\n", f"COMPOSE_PROJECT_NAME={project_name}\n"
    )
    content = content.replace("POSTGRES_PASSWORD=\n", f"POSTGRES_PASSWORD={password}\n")
    if args.environment == "dev":
        port = int(os.environ.get("DB_PORT", "5432"))
        if not 1 <= port <= 65535:
            raise SystemExit("DB_PORT must be between 1 and 65535")
        content = content.replace("DB_PORT=5432", f"DB_PORT={port}")
        content = content.replace(
            "DATABASE_URL=\n",
            f"DATABASE_URL=postgresql+psycopg://app:{password}@127.0.0.1:{port}/app?connect_timeout=5\n",
        )
    try:
        fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        print(f"Existing deployments/{args.environment}/.env preserved.")
        return
    with os.fdopen(fd, "w") as output:
        output.write(content)
    print(f"Created deployments/{args.environment}/.env (mode 0600).")


if __name__ == "__main__":
    main()
