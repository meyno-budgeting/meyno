import datetime
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session


@contextmanager
def controller_read(session: Session) -> Generator[None]:
    try:
        yield
    finally:
        session.rollback()


def get_local_todays_date() -> datetime.date:
    return datetime.datetime.now().astimezone().date()
