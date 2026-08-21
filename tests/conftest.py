import pytest

from meyno.database.base import Base
from meyno.database.connection import create_engine_and_session_factory


@pytest.fixture
def session():
    engine, SessionLocal = create_engine_and_session_factory("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        yield session

    engine.dispose()
