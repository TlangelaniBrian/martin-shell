import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserAISettings(Base):
    __tablename__ = "user_ai_settings"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="cascade"), unique=True, nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), default="anthropic", nullable=False)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    anthropic_api_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    openai_api_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    google_api_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    deepseek_api_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
