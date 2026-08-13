"""
The users table.

Holds account info (email, password) plus the profile fields collected
during onboarding. Fields are nullable because onboarding happens across
12 steps - a user exists before every field is filled.
"""

from datetime import datetime

from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # ---- Account ----
    # Email/password are optional for now: onboarding starts BEFORE signup,
    # so an anonymous profile can exist and get an email attached later.
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ---- Onboarding step 1: basic profile ----
    name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    # Stored as text bracket ("16-18", "19-24", "25+"), not a raw age.
    age_bracket: Mapped[str | None] = mapped_column(String(10), nullable=True)
    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
