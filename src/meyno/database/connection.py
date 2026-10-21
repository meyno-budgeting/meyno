from pathlib import Path
from sqlite3 import Connection

from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry

DATABASE_PATH = Path(__file__).resolve().parents[3] / "meyno.db"

DATABASE_URL = URL.create(
    "sqlite",
    database=str(DATABASE_PATH),
).render_as_string(hide_password=False)


def create_engine_and_session_factory(database_url: str) -> tuple:

    engine = create_engine(database_url, connect_args={"check_same_thread": False})

    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def enforce_foreign_keys_sqlite(
            dbapi_connection: Connection, _connection_record: ConnectionPoolEntry
        ) -> None:
            dbapi_connection.execute("PRAGMA Foreign_keys=ON")

    session_factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)

    return engine, session_factory


engine, SessionLocal = create_engine_and_session_factory(DATABASE_URL)
