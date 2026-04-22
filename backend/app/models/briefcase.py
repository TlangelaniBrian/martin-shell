import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Briefcase(Base):
    __tablename__ = "briefcase"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    reasons: Mapped[list["BriefcaseReason"]] = relationship(
        back_populates="briefcase",
        cascade="all, delete-orphan",
        order_by="BriefcaseReason.order",
    )


class BriefcaseReason(Base):
    __tablename__ = "briefcase_reason"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True
    )
    briefcase_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("briefcase.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    briefcase: Mapped["Briefcase"] = relationship(back_populates="reasons")
    cases: Mapped[list["BriefcaseReasonCase"]] = relationship(
        back_populates="reason",
        cascade="all, delete-orphan",
        order_by="BriefcaseReasonCase.order",
    )


class BriefcaseReasonCase(Base):
    __tablename__ = "briefcase_reason_case"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True
    )
    reason_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("briefcase_reason.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    case_id: Mapped[int] = mapped_column(
        ForeignKey("case.id"), nullable=False
    )
    content: Mapped[str | None] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    reason: Mapped["BriefcaseReason"] = relationship(back_populates="cases")
    case: Mapped["Case"] = relationship(lazy="joined")

    __table_args__ = (
        UniqueConstraint("reason_id", "case_id", name="uq_reason_case"),
    )


class ContentVersion(Base):
    __tablename__ = "content_version"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True
    )
    parent_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "reason" or "reason_case"
    parent_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
