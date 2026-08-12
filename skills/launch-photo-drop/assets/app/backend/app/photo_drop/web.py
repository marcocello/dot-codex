from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .runtime import PhotoDropRuntime
from .upload_service import UploadRejected, UploadService
from .upload_store import UploadStore


def _spa_response(frontend_dist: Path) -> FileResponse:
    return FileResponse(frontend_dist / "index.html")


def _mount_static(app: FastAPI, frontend_dist: Path) -> None:
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")
    images = frontend_dist / "images"
    if images.is_dir():
        app.mount("/images", StaticFiles(directory=images), name="images")


def create_admin_app(runtime: PhotoDropRuntime, frontend_dist: Path, uploads: UploadStore | None = None) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    _mount_static(app, frontend_dist)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/session")
    async def session() -> JSONResponse:
        current = runtime.current()
        if current is None:
            return JSONResponse({"state": "starting"})
        payload = current.admin_payload()
        payload["tunnel_error"] = runtime.tunnel_error
        return JSONResponse(payload)

    @app.post("/api/session/stop")
    async def stop_session() -> JSONResponse:
        current = await runtime.stop_session("host")
        if current is None:
            raise HTTPException(status_code=409, detail="No session is active")
        payload = current.admin_payload()
        payload["tunnel_error"] = runtime.tunnel_error
        return JSONResponse(payload)

    @app.get("/api/uploads")
    async def upload_activity() -> JSONResponse:
        current = runtime.current()
        if current is None or uploads is None:
            return JSONResponse({"active_count": 0, "completed_count": 0, "completed_bytes": 0, "items": []})
        return JSONResponse(uploads.activity(current.id))

    @app.get("/{path:path}")
    async def admin_spa(path: str) -> FileResponse:
        return _spa_response(frontend_dist)

    return app


def create_guest_app(runtime: PhotoDropRuntime, frontend_dist: Path, uploads: UploadService | None = None) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    _mount_static(app, frontend_dist)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/events/{token}/status")
    async def event_status(token: str) -> JSONResponse:
        session = runtime.find_token(token)
        if session is None or session.state != "active":
            return JSONResponse({"state": "closed"}, status_code=410)
        return JSONResponse(
            {
                "state": "active",
                "event_name": session.event_name,
                "expires_at": session.expires_at.isoformat(),
            }
        )

    @app.post("/api/events/{token}/uploads")
    async def receive_upload(token: str, request: Request) -> JSONResponse:
        if uploads is None:
            return JSONResponse({"code": "unavailable", "message": "Uploads are unavailable"}, status_code=503)
        try:
            return JSONResponse(await uploads.receive(token, request))
        except UploadRejected as error:
            return JSONResponse(error.payload(), status_code=error.status)

    @app.get("/api/events/{token}/gallery")
    async def gallery(token: str) -> JSONResponse:
        session = runtime.find_token(token)
        if session is None or session.state != "active":
            return JSONResponse({"state": "closed"}, status_code=410)
        if uploads is None:
            return JSONResponse({"items": []})
        items = [
            {
                "id": image.id,
                "url": f"/api/events/{token}/gallery/{image.id}",
                "completed_at": image.completed_at,
            }
            for image in uploads.gallery_images(session)
        ]
        return JSONResponse({"items": items}, headers={"Cache-Control": "no-store"})

    @app.get("/api/events/{token}/gallery/{upload_id}")
    async def gallery_image(token: str, upload_id: str):
        session = runtime.find_token(token)
        if session is None or session.state != "active":
            return JSONResponse({"state": "closed"}, status_code=410)
        image = uploads.gallery_image(session, upload_id) if uploads else None
        if image is None:
            return JSONResponse({"detail": "Photo not found"}, status_code=404)
        image_path = session.destination / image.storage_name
        if not image_path.is_file():
            return JSONResponse({"detail": "Photo not found"}, status_code=404)
        return FileResponse(
            image_path,
            media_type=image.content_type,
            headers={
                "Cache-Control": "no-store",
                "Content-Security-Policy": "sandbox; default-src 'none'",
                "X-Content-Type-Options": "nosniff",
            },
        )

    @app.get("/event/{token}")
    async def guest_spa(token: str) -> FileResponse:
        return _spa_response(frontend_dist)

    return app
