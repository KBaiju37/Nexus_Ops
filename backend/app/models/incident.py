from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    deployment_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default="Medium")
    error_logs: Mapped[str] = mapped_column(Text, default="")
    root_cause_category: Mapped[str] = mapped_column(String(100), default="Unknown")
    diagnosis: Mapped[str] = mapped_column(Text, default="")
    recommended_resolution: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default="Open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    ml_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ml_confidence: Mapped[float | None] = mapped_column(nullable=True)
