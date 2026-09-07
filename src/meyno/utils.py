import datetime
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session


@contextmanager
def controller_write(session: Session) -> Generator[None]:
    try:
        yield
        session.commit()
    except Exception:
        session.rollback()
        raise


def get_local_todays_date() -> datetime.date:
    return datetime.datetime.now().astimezone().date()
