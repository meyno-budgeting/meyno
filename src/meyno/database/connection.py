from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_PATH = Path(__file__).resolve().parents[3] / "meyno.db"
DATABASE_URL = f"sqlite:////{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args = {"check_same_thread": False}
    )

SessionLocal = sessionmaker(
    bind = engine,
    class_ = Session,
    expire_on_commit = False
)