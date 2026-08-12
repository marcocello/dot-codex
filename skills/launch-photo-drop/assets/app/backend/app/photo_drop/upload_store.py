import hashlib
import shutil
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .models import Session
from .filenames import collision_name


class CapacityError(RuntimeError):
    pass


@dataclass(frozen=True)
class UploadReservation:
    id: str
    client_upload_id: str
    original_name: str
    content_type: str
    declared_size: int
    storage_name: str
    state: str
    existing: bool


@dataclass(frozen=True)
class GalleryImage:
    id: str
    storage_name: str
    content_type: str
    completed_at: str


class UploadStore:
    def __init__(self, database: Path):
        self.database = database
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=5, isolation_level=None)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS uploads (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    client_upload_id TEXT NOT NULL,
                    original_name TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    declared_size INTEGER NOT NULL,
                    received_size INTEGER NOT NULL DEFAULT 0,
                    storage_name TEXT NOT NULL,
                    state TEXT NOT NULL,
                    sha256 TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    error_code TEXT,
                    UNIQUE(session_id, client_upload_id)
                )
                """
            )

    def reserve(
        self,
        session: Session,
        client_upload_id: str,
        original_name: str,
        content_type: str,
        declared_size: int,
        max_session_bytes: int,
        free_space_reserve_bytes: int,
    ) -> UploadReservation:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT * FROM uploads WHERE session_id = ? AND client_upload_id = ?",
                (session.id, client_upload_id),
            ).fetchone()
            if existing and existing["state"] == "complete":
                connection.commit()
                return self._from_row(existing, existing=True)
            self._assert_capacity(
                connection,
                session,
                declared_size,
                max_session_bytes,
                free_space_reserve_bytes,
                existing["id"] if existing else None,
            )
            reservation = self._upsert_reservation(
                connection, existing, session, client_upload_id, original_name, content_type, declared_size
            )
            connection.commit()
            return reservation
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def recover_interrupted(self) -> None:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT uploads.id, uploads.declared_size, uploads.storage_name, sessions.destination
                FROM uploads JOIN sessions ON sessions.id = uploads.session_id
                WHERE uploads.state = 'uploading'
                """
            ).fetchall()
            for row in rows:
                destination = Path(row["destination"])
                partial_path = destination / f".{row['id']}.partial"
                final_path = destination / row["storage_name"]
                linked_by_application = (
                    partial_path.is_file()
                    and final_path.is_file()
                    and partial_path.stat().st_ino == final_path.stat().st_ino
                )
                if linked_by_application and final_path.stat().st_size == row["declared_size"]:
                    digest = _sha256_file(final_path)
                    connection.execute(
                        """
                        UPDATE uploads SET state = 'complete', received_size = declared_size,
                            sha256 = ?, completed_at = ?, error_code = NULL WHERE id = ?
                        """,
                        (digest, datetime.now(UTC).isoformat(), row["id"]),
                    )
                else:
                    connection.execute(
                        "UPDATE uploads SET state = 'failed', error_code = 'interrupted' WHERE id = ?",
                        (row["id"],),
                    )
                partial_path.unlink(missing_ok=True)
            completed = connection.execute(
                """
                SELECT uploads.id, sessions.destination
                FROM uploads JOIN sessions ON sessions.id = uploads.session_id
                WHERE uploads.state = 'complete'
                """
            ).fetchall()
            for row in completed:
                (Path(row["destination"]) / f".{row['id']}.partial").unlink(missing_ok=True)

    def _assert_capacity(
        self,
        connection: sqlite3.Connection,
        session: Session,
        declared_size: int,
        max_session_bytes: int,
        free_space_reserve_bytes: int,
        retry_id: str | None,
    ) -> None:
        rows = connection.execute(
            """
            SELECT id, state, declared_size, received_size FROM uploads
            WHERE session_id = ? AND state IN ('uploading', 'complete')
            """,
            (session.id,),
        ).fetchall()
        committed_and_reserved = sum(row["declared_size"] for row in rows if row["id"] != retry_id)
        active_unwritten = sum(
            max(0, row["declared_size"] - row["received_size"])
            for row in rows
            if row["state"] == "uploading" and row["id"] != retry_id
        )
        free_bytes = shutil.disk_usage(session.destination).free
        if committed_and_reserved + declared_size > max_session_bytes:
            raise CapacityError("event quota exceeded")
        if free_bytes - active_unwritten - declared_size < free_space_reserve_bytes:
            raise CapacityError("safe free-space reserve would be crossed")

    def _upsert_reservation(
        self,
        connection: sqlite3.Connection,
        existing: sqlite3.Row | None,
        session: Session,
        client_upload_id: str,
        original_name: str,
        content_type: str,
        declared_size: int,
    ) -> UploadReservation:
        if existing:
            storage_name = self._allocate_storage_name(
                connection, session, original_name, exclude_upload_id=existing["id"]
            )
            connection.execute(
                """
                UPDATE uploads SET state = 'uploading', received_size = 0,
                    sha256 = NULL, completed_at = NULL, error_code = NULL,
                    original_name = ?, content_type = ?, declared_size = ?, storage_name = ?
                WHERE id = ?
                """,
                (original_name, content_type, declared_size, storage_name, existing["id"]),
            )
            row = connection.execute("SELECT * FROM uploads WHERE id = ?", (existing["id"],)).fetchone()
            return self._from_row(row, existing=False)
        upload_id = str(uuid.uuid4())
        storage_name = self._allocate_storage_name(connection, session, original_name)
        connection.execute(
            """
            INSERT INTO uploads (
                id, session_id, client_upload_id, original_name, content_type,
                declared_size, storage_name, state, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'uploading', ?)
            """,
            (
                upload_id,
                session.id,
                client_upload_id,
                original_name,
                content_type,
                declared_size,
                storage_name,
                datetime.now(UTC).isoformat(),
            ),
        )
        row = connection.execute("SELECT * FROM uploads WHERE id = ?", (upload_id,)).fetchone()
        return self._from_row(row, existing=False)

    def reassign_storage_name(self, upload_id: str, session: Session) -> str:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM uploads WHERE id = ? AND session_id = ? AND state = 'uploading'",
                (upload_id, session.id),
            ).fetchone()
            if row is None:
                raise RuntimeError("upload reservation is no longer active")
            storage_name = self._allocate_storage_name(
                connection, session, row["original_name"], exclude_upload_id=upload_id
            )
            connection.execute(
                "UPDATE uploads SET storage_name = ? WHERE id = ?",
                (storage_name, upload_id),
            )
            connection.commit()
            return storage_name
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _allocate_storage_name(
        connection: sqlite3.Connection,
        session: Session,
        preferred_name: str,
        exclude_upload_id: str | None = None,
    ) -> str:
        rows = connection.execute(
            """
            SELECT id, storage_name FROM uploads
            WHERE session_id = ? AND state IN ('uploading', 'complete')
            """,
            (session.id,),
        ).fetchall()
        reserved = {row["storage_name"] for row in rows if row["id"] != exclude_upload_id}
        index = 0
        while True:
            candidate = collision_name(preferred_name, index)
            if candidate not in reserved and not (session.destination / candidate).exists():
                return candidate
            index += 1

    def complete(self, upload_id: str, received_size: int, digest: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE uploads SET state = 'complete', received_size = ?, sha256 = ?,
                    completed_at = ?, error_code = NULL WHERE id = ?
                """,
                (received_size, digest, datetime.now(UTC).isoformat(), upload_id),
            )

    def record_progress(self, upload_id: str, received_size: int) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE uploads SET received_size = ? WHERE id = ? AND state = 'uploading'",
                (received_size, upload_id),
            )

    def fail(self, upload_id: str, code: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE uploads SET state = 'failed', error_code = ? WHERE id = ? AND state != 'complete'",
                (code, upload_id),
            )

    def activity(self, session_id: str) -> dict[str, object]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, original_name, content_type, declared_size,
                    received_size, state, completed_at
                FROM uploads
                WHERE session_id = ? AND state IN ('uploading', 'complete')
                ORDER BY
                    CASE WHEN state = 'uploading' THEN 0 ELSE 1 END,
                    CASE WHEN state = 'uploading' THEN created_at END DESC,
                    completed_at DESC,
                    created_at DESC,
                    id DESC
                """,
                (session_id,),
            ).fetchall()
        items = [
            {
                "id": row["id"],
                "original_name": row["original_name"],
                "content_type": row["content_type"],
                "declared_size": row["declared_size"],
                "received_size": row["received_size"],
                "state": row["state"],
                "completed_at": row["completed_at"],
            }
            for row in rows
        ]
        completed = [item for item in items if item["state"] == "complete"]
        return {
            "active_count": len(items) - len(completed),
            "completed_count": len(completed),
            "completed_bytes": sum(int(item["received_size"]) for item in completed),
            "items": items,
        }

    def gallery_images(self, session_id: str) -> list[GalleryImage]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, storage_name, content_type, completed_at
                FROM uploads
                WHERE session_id = ? AND state = 'complete'
                    AND content_type LIKE 'image/%' AND completed_at IS NOT NULL
                ORDER BY completed_at DESC, created_at DESC, id DESC
                """,
                (session_id,),
            ).fetchall()
        return [self._gallery_from_row(row) for row in rows]

    def gallery_image(self, session_id: str, upload_id: str) -> GalleryImage | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, storage_name, content_type, completed_at
                FROM uploads
                WHERE id = ? AND session_id = ? AND state = 'complete'
                    AND content_type LIKE 'image/%' AND completed_at IS NOT NULL
                """,
                (upload_id, session_id),
            ).fetchone()
        return self._gallery_from_row(row) if row else None

    @staticmethod
    def _gallery_from_row(row: sqlite3.Row) -> GalleryImage:
        return GalleryImage(
            id=row["id"],
            storage_name=row["storage_name"],
            content_type=row["content_type"],
            completed_at=row["completed_at"],
        )

    @staticmethod
    def _from_row(row: sqlite3.Row, existing: bool) -> UploadReservation:
        return UploadReservation(
            id=row["id"],
            client_upload_id=row["client_upload_id"],
            original_name=row["original_name"],
            content_type=row["content_type"],
            declared_size=row["declared_size"],
            storage_name=row["storage_name"],
            state=row["state"],
            existing=existing,
        )


def _sha256_file(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()
