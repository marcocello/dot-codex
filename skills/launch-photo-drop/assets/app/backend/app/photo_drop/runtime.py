import asyncio
from datetime import UTC, datetime

from .models import Session
from .session_store import SessionStore
from .tunnel import NgrokTunnel


class PhotoDropRuntime:
    def __init__(self, store: SessionStore, tunnel: NgrokTunnel, upload_grace_seconds: float = 30):
        self.store = store
        self.tunnel = tunnel
        self.session: Session | None = None
        self._stop_lock = asyncio.Lock()
        self.tunnel_error: str | None = None
        self.upload_grace_seconds = upload_grace_seconds
        self._upload_condition = asyncio.Condition()
        self._active_uploads: set[str] = set()
        self._upload_tasks: dict[str, asyncio.Task[object]] = {}
        self._upload_abort_event = asyncio.Event()
        self.uploads_must_abort = False

    def activate(self, session: Session) -> None:
        self.session = session

    def current(self) -> Session | None:
        if self.session is None:
            return None
        self.session = self.store.get(self.session.id)
        return self.session

    def find_token(self, token: str) -> Session | None:
        current = self.current()
        if current is None or current.token != token:
            return None
        return current

    async def stop_session(self, reason: str) -> Session | None:
        async with self._stop_lock:
            current = self.current()
            if current is None or current.state == "ended":
                return current
            self.session = self.store.begin_stopping(current.id)
            await self._await_upload_grace()
            try:
                await self.tunnel.stop()
            except Exception as error:
                self.tunnel_error = str(error)
            self.session = self.store.end_session(current.id, reason)
            return self.session

    async def admit_upload(self, token: str, client_upload_id: str) -> Session:
        async with self._upload_condition:
            session = self.find_token(token)
            if session is None or session.state != "active":
                from .upload_service import UploadRejected

                raise UploadRejected(410, "event_closed", "This event is closed")
            self._active_uploads.add(client_upload_id)
            current_task = asyncio.current_task()
            if current_task is not None:
                self._upload_tasks[client_upload_id] = current_task
            return session

    async def finish_upload(self, client_upload_id: str) -> None:
        async with self._upload_condition:
            self._active_uploads.discard(client_upload_id)
            self._upload_tasks.pop(client_upload_id, None)
            self._upload_condition.notify_all()

    async def wait_for_upload_abort(self) -> None:
        await self._upload_abort_event.wait()

    async def _await_upload_grace(self) -> None:
        async with self._upload_condition:
            try:
                async with asyncio.timeout(self.upload_grace_seconds):
                    while self._active_uploads:
                        await self._upload_condition.wait()
            except TimeoutError:
                self.uploads_must_abort = True
                self._upload_abort_event.set()
                try:
                    async with asyncio.timeout(0.5):
                        while self._active_uploads:
                            await self._upload_condition.wait()
                except TimeoutError:
                    for task in list(self._upload_tasks.values()):
                        task.cancel()
                    while self._active_uploads:
                        await self._upload_condition.wait()

    async def expire_at_deadline(self) -> None:
        current = self.current()
        if current is None:
            return
        seconds = max(0.0, (current.expires_at - datetime.now(UTC)).total_seconds())
        await asyncio.sleep(seconds)
        await self.stop_session("expired")
