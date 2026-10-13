from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


def get_session(request: Request) -> Iterator[Session]:
    with Session(request.app.state.engine) as session:
        yield session
