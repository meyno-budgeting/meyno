import pytest

from meyno.database.base import Base
from meyno.database.connection import create_engine_and_session_factory


@pytest.fixture
def session():
    engine, session_local = create_engine_and_session_factory("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    with session_local() as session:
        yield session

    engine.dispose()
