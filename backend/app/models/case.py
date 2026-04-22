from datetime import date, datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Case(Base):
    __tablename__ = "case"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    saflii_url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    citation: Mapped[str | None] = mapped_column(String(256))
    case_number: Mapped[str | None] = mapped_column(String(256))
    case_name: Mapped[str] = mapped_column(String(512), nullable=False)
    court: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    date_decided: Mapped[date | None] = mapped_column(Date)
    judge: Mapped[str | None] = mapped_column(String(512))
    summary: Mapped[str | None] = mapped_column(Text)
    full_text: Mapped[str | None] = mapped_column(Text)
    pdf_storage_key: Mapped[str | None] = mapped_column(String(512))
    pdf_url: Mapped[str | None] = mapped_column(String(512))
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
