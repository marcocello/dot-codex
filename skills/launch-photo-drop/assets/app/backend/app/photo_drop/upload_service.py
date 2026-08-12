import asyncio
from contextlib import suppress
import hashlib
import os
from pathlib import Path

from fastapi import Request

from .models import Session
from .filenames import sanitize_original_name
from .runtime import PhotoDropRuntime
from .upload_store import CapacityError, GalleryImage, UploadReservation, UploadStore


class UploadRejected(RuntimeError):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message

    def payload(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


class UploadService:
    def __init__(
        self,
        runtime: PhotoDropRuntime,
        store: UploadStore,
        max_session_bytes: int,
        free_space_reserve_bytes: int,
    ):
        self.runtime = runtime
        self.store = store
        self.max_session_bytes = max_session_bytes
        self.free_space_reserve_bytes = free_space_reserve_bytes

    def gallery_images(self, session: Session) -> list[GalleryImage]:
        return self.store.gallery_images(session.id)

    def gallery_image(self, session: Session, upload_id: str) -> GalleryImage | None:
        return self.store.gallery_image(session.id, upload_id)

    async def receive(self, token: str, request: Request) -> dict[str, object]:
        metadata = self._metadata(request)
        session = await self.runtime.admit_upload(token, metadata["client_upload_id"])
        reservation: UploadReservation | None = None
        partial_path: Path | None = None
        try:
            reservation = self._reserve(session, metadata)
            if reservation.existing:
                return self._success_payload(reservation)
            partial_path = session.destination / f".{reservation.id}.partial"
            received_size, digest = await self._stream(
                request, partial_path, reservation.id, reservation.declared_size
            )
            if self.runtime.uploads_must_abort:
                raise UploadRejected(410, "event_closed", "This event closed before the upload finished")
            self._finalize(partial_path, session, reservation, received_size, digest)
            partial_path = None
            return self._success_payload(reservation, received_size, digest)
        except UploadRejected as error:
            if reservation:
                self.store.fail(reservation.id, error.code)
            raise
        except asyncio.CancelledError:
            if reservation:
                self.store.fail(reservation.id, "event_closed")
            raise
        except Exception:
            if reservation:
                self.store.fail(reservation.id, "upload_failed")
            raise
        finally:
            if partial_path:
                partial_path.unlink(missing_ok=True)
            await self.runtime.finish_upload(metadata["client_upload_id"])

    def _metadata(self, request: Request) -> dict[str, object]:
        content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
        if not (content_type.startswith("image/") or content_type.startswith("video/")):
            raise UploadRejected(415, "unsupported_media", "Choose a photo or video")
        client_upload_id = request.headers.get("x-upload-id", "").strip()
        raw_name = request.headers.get("x-file-name", "")
        raw_size = request.headers.get("x-file-size", "")
        if not client_upload_id or len(client_upload_id) > 128:
            raise UploadRejected(400, "invalid_upload", "This upload could not be identified")
        try:
            declared_size = int(raw_size)
        except ValueError as error:
            raise UploadRejected(400, "invalid_size", "The file size is invalid") from error
        if declared_size <= 0:
            raise UploadRejected(400, "invalid_size", "The file is empty")
        original_name = sanitize_original_name(raw_name)
        return {
            "client_upload_id": client_upload_id,
            "original_name": original_name,
            "content_type": content_type,
            "declared_size": declared_size,
        }

    def _reserve(self, session: Session, metadata: dict[str, object]) -> UploadReservation:
        try:
            return self.store.reserve(
                session,
                str(metadata["client_upload_id"]),
                str(metadata["original_name"]),
                str(metadata["content_type"]),
                int(metadata["declared_size"]),
                self.max_session_bytes,
                self.free_space_reserve_bytes,
            )
        except CapacityError as error:
            raise UploadRejected(507, "capacity_exceeded", "Host storage is full") from error

    def _finalize(
        self,
        partial_path: Path,
        session: Session,
        reservation: UploadReservation,
        received_size: int,
        digest: str,
    ) -> None:
        storage_name = reservation.storage_name
        while True:
            final_path = session.destination / storage_name
            try:
                os.link(partial_path, final_path)
            except FileExistsError:
                storage_name = self.store.reassign_storage_name(reservation.id, session)
                continue
            try:
                self.store.complete(reservation.id, received_size, digest)
            except Exception:
                final_path.unlink(missing_ok=True)
                raise
            partial_path.unlink(missing_ok=True)
            return

    async def _stream(
        self, request: Request, partial_path: Path, upload_id: str, declared_size: int
    ) -> tuple[int, str]:
        received = 0
        digest = hashlib.sha256()
        stream = request.stream().__aiter__()
        with partial_path.open("wb") as target:
            while True:
                next_chunk = asyncio.create_task(anext(stream))
                abort = asyncio.create_task(self.runtime.wait_for_upload_abort())
                done, _ = await asyncio.wait((next_chunk, abort), return_when=asyncio.FIRST_COMPLETED)
                if abort in done:
                    next_chunk.cancel()
                    with suppress(asyncio.CancelledError, StopAsyncIteration):
                        await next_chunk
                    raise UploadRejected(410, "event_closed", "This event closed before the upload finished")
                abort.cancel()
                with suppress(asyncio.CancelledError):
                    await abort
                try:
                    chunk = next_chunk.result()
                except StopAsyncIteration:
                    break
                received += len(chunk)
                if received > declared_size:
                    raise UploadRejected(400, "size_mismatch", "The received file was larger than declared")
                digest.update(chunk)
                target.write(chunk)
                self.store.record_progress(upload_id, received)
            target.flush()
            os.fsync(target.fileno())
        if received != declared_size:
            raise UploadRejected(400, "size_mismatch", "The upload ended before the complete file arrived")
        return received, digest.hexdigest()

    @staticmethod
    def _success_payload(
        reservation: UploadReservation,
        received_size: int | None = None,
        digest: str | None = None,
    ) -> dict[str, object]:
        return {
            "id": reservation.id,
            "original_name": reservation.original_name,
            "content_type": reservation.content_type,
            "size": received_size if received_size is not None else reservation.declared_size,
            "sha256": digest,
            "state": "complete",
        }
