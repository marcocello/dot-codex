"""Create local database settings once, without printing secrets."""

import os
from pathlib import Path
import secrets


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    destination = root / ".env"
    password = secrets.token_urlsafe(32)
    content = (root / ".env.example").read_text()
    content = content.replace("POSTGRES_PASSWORD=\n", f"POSTGRES_PASSWORD={password}\n")
    content = content.replace(
        "DATABASE_URL=\n",
        f"DATABASE_URL=postgresql+psycopg://app:{password}@127.0.0.1:5432/app?connect_timeout=5\n",
    )
    try:
        fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        print("Existing .env preserved.")
        return
    with os.fdopen(fd, "w") as output:
        output.write(content)
    print("Created .env with local database settings (mode 0600).")


if __name__ == "__main__":
    main()
