from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_settings.schemas import AISettingsRead, AISettingsUpdate
from app.auth.users import current_active_user
from app.database import get_async_session
from app.models.ai_settings import UserAISettings
from app.models.user import User

router = APIRouter()

_DEFAULT = AISettingsRead(
    provider="anthropic",
    model=None,
    anthropic_configured=False,
    openai_configured=False,
    google_configured=False,
    deepseek_configured=False,
)


def _to_read(row: UserAISettings) -> AISettingsRead:
    return AISettingsRead(
        provider=row.provider,
        model=row.model,
        anthropic_configured=bool(row.anthropic_api_key),
        openai_configured=bool(row.openai_api_key),
        google_configured=bool(row.google_api_key),
        deepseek_configured=bool(row.deepseek_api_key),
    )


@router.get("/", response_model=AISettingsRead)
async def get_ai_settings(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> AISettingsRead:
    result = await session.execute(
        select(UserAISettings).where(UserAISettings.user_id == user.id)
    )
    row = result.scalar_one_or_none()
    return _to_read(row) if row else _DEFAULT


@router.patch("/", response_model=AISettingsRead)
async def update_ai_settings(
    body: AISettingsUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
) -> AISettingsRead:
    result = await session.execute(
        select(UserAISettings).where(UserAISettings.user_id == user.id)
    )
    row = result.scalar_one_or_none()

    if row is None:
        row = UserAISettings(user_id=user.id)
        session.add(row)

    if body.provider is not None:
        row.provider = body.provider
    if body.model is not None:
        row.model = body.model
    if body.anthropic_api_key:
        row.anthropic_api_key = body.anthropic_api_key
    if body.openai_api_key:
        row.openai_api_key = body.openai_api_key
    if body.google_api_key:
        row.google_api_key = body.google_api_key
    if body.deepseek_api_key:
        row.deepseek_api_key = body.deepseek_api_key

    await session.commit()
    await session.refresh(row)
    return _to_read(row)
