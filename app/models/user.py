"""
The users table.

Now covers onboarding steps 1-6. Face analysis results and the daily
habit answers are added here. The actual AI vision call happens in a
service (app/services/vision.py) and its result is cached in
face_analysis so we never re-run it on every page load.
"""

from datetime import datetime

from sqlalchemy import String, Integer, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # ---- Account ----
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ---- Step 1: basic profile ----
    name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    age_bracket: Mapped[str | None] = mapped_column(String(10), nullable=True)
    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ---- Step 2: goals ----
    goals: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # ---- Step 3: body + activity ----
    body_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    activity_level: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ---- Step 4: diet ----
    diet_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    food_likes: Mapped[list | None] = mapped_column(JSON, nullable=True)
    food_dislikes: Mapped[str | None] = mapped_column(String(300), nullable=True)
    allergies: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # ---- Step 5: face upload ----
    # Path to the saved (resized, EXIF-stripped) front photo on disk.
    face_photo_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # The cached AI vision result as JSON (face shape, hair, skin notes).
    # Computed ONCE, then read from here forever.
    face_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ---- Step 6: daily habits ----
    sleep_hours: Mapped[str | None] = mapped_column(String(10), nullable=True)   # "<5","5-6","6-7","7-8","8+"
    water_intake: Mapped[str | None] = mapped_column(String(10), nullable=True)  # "<1L","1-2L","2-3L","3L+"
    routine_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # student/working/self/other
    stress_level: Mapped[str | None] = mapped_column(String(10), nullable=True)  # low/medium/high

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
