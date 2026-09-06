from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy.orm import Session


@contextmanager
def controller_read(session: Session) -> Generator[None, Any]:
    try:
        yield
    finally:
        session.rollback()
