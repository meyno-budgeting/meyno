from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database.db import SessionLocal
from database.models import User


def add_user(email_in: str, password_in: str, full_name: str | None = None) -> User:
    with SessionLocal() as session:

        # Check if email exists
        existing_user = session.scalar(
            select(User).where(User.email == email_in)
        )

        if existing_user:
            raise ValueError("Email already exists")

        user = User(
            email=email_in,
            password=password_in,
            full_name=full_name
        )

        session.add(user)

        try:
            session.commit()

        except IntegrityError:
            session.rollback()
            raise ValueError("Email already exists")

        session.refresh(user)

        return user