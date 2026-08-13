"""
The users table.

This is the first and most important table. Every other piece of data
(goals, body metrics, habits, plans) will eventually link back to a row
here. For now it holds just enough to create and log in a user.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"

    # Primary key: a unique integer id auto-assigned by Postgres.
    id: Mapped[int] = mapped_column(primary_key=True)

    # The display name collected on onboarding step 1 ("What should we call you?").
    name: Mapped[str] = mapped_column(String(80))

    # Login email. unique=True stops two accounts sharing one email.
    # index=True makes "find user by email" (every login) fast.
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # The bcrypt HASH of the password, never the password itself.
    hashed_password: Mapped[str] = mapped_column(String(255))

    # Set automatically by the database when the row is created.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
