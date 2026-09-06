from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session


@contextmanager
def controller_read(session: Session) -> Generator[None]:
    try:
        yield
    finally:
        session.rollback()
