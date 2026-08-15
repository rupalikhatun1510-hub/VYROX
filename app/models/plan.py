"""
The plans table.

Stores the AI-generated plan for a user as JSON. One plan per user for
now (we overwrite on regeneration). Kept separate from the users table
because a plan is a big blob and gets regenerated independently.
"""

from datetime import datetime

from sqlalchemy import Integer, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # The whole generated plan as one JSON object:
    # { workout: {...}, meals: {...}, grooming: {...}, habits: [...], insight: "" }
    data: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
