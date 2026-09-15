import secrets
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

from .event_names import DEFAULT_EVENT_NAME, normalize_event_name
from .models import Session


class SessionStore:
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        if not self.state_dir.is_dir():
            raise NotADirectoryError(state_dir)
        self.database = self.state_dir / "photo-drop.sqlite3"
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=5)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    token TEXT UNIQUE NOT NULL,
                    state TEXT NOT NULL,
                    event_name TEXT NOT NULL DEFAULT 'Photo Drop',
                    destination TEXT NOT NULL,
                    guest_url TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    ended_at TEXT,
                    end_reason TEXT
                )
                """
            )
            columns = {row["name"] for row in connection.execute("PRAGMA table_info(sessions)")}
            if "event_name" not in columns:
                connection.execute(
                    "ALTER TABLE sessions ADD COLUMN event_name TEXT NOT NULL DEFAULT 'Photo Drop'"
                )

    def start_session(
        self,
        destination: Path,
        expires_at: datetime,
        public_origin: str,
        event_name: str = DEFAULT_EVENT_NAME,
    ) -> Session:
        now = datetime.now(UTC)
        session_id = str(uuid.uuid4())
        token = secrets.token_urlsafe(24)
        guest_url = f"{public_origin.rstrip('/')}/event/{token}"
        normalized_event_name = normalize_event_name(event_name)
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE sessions
                SET state = 'ended', ended_at = ?, end_reason = 'interrupted'
                WHERE state IN ('starting', 'active', 'stopping')
                """,
                (now.isoformat(),),
            )
            connection.execute(
                """
                INSERT INTO sessions (
                    id, token, state, event_name, destination, guest_url,
                    created_at, expires_at, ended_at, end_reason
                ) VALUES (?, ?, 'active', ?, ?, ?, ?, ?, NULL, NULL)
                """,
                (
                    session_id,
                    token,
                    normalized_event_name,
                    str(destination.resolve()),
                    guest_url,
                    now.isoformat(),
                    expires_at.astimezone(UTC).isoformat(),
                ),
            )
        return self.get(session_id)

    def recover_interrupted(self) -> None:
        now = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE sessions
                SET state = 'ended', ended_at = COALESCE(ended_at, ?),
                    end_reason = COALESCE(end_reason, 'interrupted')
                WHERE state IN ('starting', 'active', 'stopping')
                """,
                (now,),
            )

    def get(self, session_id: str) -> Session:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            raise KeyError(session_id)
        return self._from_row(row)

    def get_by_token(self, token: str) -> Session | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM sessions WHERE token = ?", (token,)).fetchone()
        return self._from_row(row) if row else None

    def active(self) -> Session | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM sessions WHERE state IN ('starting', 'active', 'stopping') ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
        return self._from_row(row) if row else None

    def begin_stopping(self, session_id: str) -> Session:
        with self._connect() as connection:
            connection.execute(
                "UPDATE sessions SET state = 'stopping' WHERE id = ? AND state = 'active'",
                (session_id,),
            )
        return self.get(session_id)

    def end_session(self, session_id: str, reason: str) -> Session:
        now = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE sessions
                SET state = 'ended', ended_at = COALESCE(ended_at, ?),
                    end_reason = COALESCE(end_reason, ?)
                WHERE id = ?
                """,
                (now, reason, session_id),
            )
        return self.get(session_id)

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Session:
        return Session(
            id=row["id"],
            token=row["token"],
            state=row["state"],
            event_name=row["event_name"],
            destination=Path(row["destination"]),
            guest_url=row["guest_url"],
            created_at=datetime.fromisoformat(row["created_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
            ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
            end_reason=row["end_reason"],
        )
