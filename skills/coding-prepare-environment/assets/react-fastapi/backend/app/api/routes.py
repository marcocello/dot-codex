from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Note
from app.schemas import NoteCreate, NoteRead

router = APIRouter(prefix="/api")
DatabaseSession = Annotated[Session, Depends(get_session)]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(request: Request) -> dict[str, str]:
    try:
        with request.app.state.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(status_code=503, detail="Database unavailable") from error
    return {"status": "ready"}


@router.get("/notes", response_model=list[NoteRead])
def list_notes(session: DatabaseSession) -> list[Note]:
    return list(session.scalars(select(Note).order_by(Note.id)))


@router.post("/notes", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(body: NoteCreate, session: DatabaseSession) -> Note:
    note = Note(text=body.text)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note
