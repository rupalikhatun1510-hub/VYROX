"""
The users table.

Holds account info plus everything collected during onboarding.
Fields are nullable because a user row exists before every step is done.

Goals, food likes, and allergies are lists, so they're stored as JSON
columns (a simple list of strings). This avoids extra tables while we're
still small; we can normalise later if needed.
"""

from datetime import datetime

from sqlalchemy import String, Integer, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # ---- Account (filled at signup, later) ----
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ---- Step 1: basic profile ----
    name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    age_bracket: Mapped[str | None] = mapped_column(String(10), nullable=True)
    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ---- Step 2: goals (multi-select, stored as a JSON list of strings) ----
    goals: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # ---- Step 3: body type + activity level ----
    body_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    activity_level: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ---- Step 4: diet ----
    diet_type: Mapped[str | None] = mapped_column(String(20), nullable=True)      # veg / non-veg / other
    food_likes: Mapped[list | None] = mapped_column(JSON, nullable=True)          # ["chicken","eggs",...]
    food_dislikes: Mapped[str | None] = mapped_column(String(300), nullable=True) # free text
    allergies: Mapped[str | None] = mapped_column(String(50), nullable=True)      # none / lactose / gluten / other

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
