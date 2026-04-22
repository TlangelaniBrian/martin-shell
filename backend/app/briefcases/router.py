import asyncio
import uuid

import anthropic
import openai
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.users import current_active_user
from app.briefcases.schemas import (
    BriefcaseCreate,
    BriefcaseListResponse,
    BriefcaseRead,
    BriefcaseUpdate,
    ContentVersionRead,
    ReasonCaseCreate,
    ReasonCaseRead,
    ReasonCaseUpdate,
    ReasonCreate,
    ReasonRead,
    ReasonReorder,
    ReasonUpdate,
)
from app.config import settings
from app.database import get_async_session
from app.models.briefcase import (
    Briefcase,
    BriefcaseReason,
    BriefcaseReasonCase,
    ContentVersion,
)
from app.models.ai_settings import UserAISettings
from app.models.case import Case
from app.models.user import User

router = APIRouter()

MAX_VERSIONS = 5


async def _get_user_briefcase(
    briefcase_id: uuid.UUID,
    user: User,
    session: AsyncSession,
) -> Briefcase:
    result = await session.execute(
        select(Briefcase)
        .options(
            selectinload(Briefcase.reasons).selectinload(BriefcaseReason.cases)
        )
        .where(Briefcase.id == briefcase_id, Briefcase.user_id == user.id)
    )
    briefcase = result.scalar_one_or_none()
    if not briefcase:
        raise HTTPException(status_code=404, detail="Briefcase not found")
    return briefcase


async def _save_content_version(
    session: AsyncSession,
    parent_type: str,
    parent_id: uuid.UUID,
    content: str,
):
    """Save a content version, maintaining a rolling window of MAX_VERSIONS."""
    agg = await session.execute(
        select(
            func.count(ContentVersion.id),
            func.max(ContentVersion.version),
        ).where(
            ContentVersion.parent_type == parent_type,
            ContentVersion.parent_id == parent_id,
        )
    )
    count, max_version = agg.one()
    max_version = max_version or 0

    if count >= MAX_VERSIONS:
        oldest = await session.execute(
            select(ContentVersion)
            .where(
                ContentVersion.parent_type == parent_type,
                ContentVersion.parent_id == parent_id,
            )
            .order_by(ContentVersion.version.asc())
            .limit(count - MAX_VERSIONS + 1)
        )
        for old in oldest.scalars():
            await session.delete(old)

    session.add(
        ContentVersion(
            parent_type=parent_type,
            parent_id=parent_id,
            content=content,
            version=max_version + 1,
        )
    )


# --- Briefcase CRUD ---

@router.get("/", response_model=BriefcaseListResponse)
async def list_briefcases(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    count_result = await session.execute(
        select(func.count(Briefcase.id)).where(Briefcase.user_id == user.id)
    )
    total = count_result.scalar()

    result = await session.execute(
        select(Briefcase)
        .options(
            selectinload(Briefcase.reasons).selectinload(BriefcaseReason.cases)
        )
        .where(Briefcase.user_id == user.id)
        .order_by(Briefcase.updated_at.desc())
    )
    briefcases = result.scalars().all()

    return BriefcaseListResponse(briefcases=briefcases, total=total)


@router.post("/", response_model=BriefcaseRead, status_code=201)
async def create_briefcase(
    body: BriefcaseCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    briefcase = Briefcase(
        user_id=user.id,
        name=body.name,
        description=body.description,
    )
    session.add(briefcase)
    await session.commit()
    result = await session.execute(
        select(Briefcase)
        .options(selectinload(Briefcase.reasons))
        .where(Briefcase.id == briefcase.id)
    )
    return result.scalar_one()


@router.get("/{briefcase_id}", response_model=BriefcaseRead)
async def get_briefcase(
    briefcase_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await _get_user_briefcase(briefcase_id, user, session)


@router.patch("/{briefcase_id}", response_model=BriefcaseRead)
async def update_briefcase(
    briefcase_id: uuid.UUID,
    body: BriefcaseUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    briefcase = result.scalar_one_or_none()
    if not briefcase:
        raise HTTPException(status_code=404, detail="Briefcase not found")

    if body.name is not None:
        briefcase.name = body.name
    if body.description is not None:
        briefcase.description = body.description

    await session.commit()
    return await _get_user_briefcase(briefcase.id, user, session)


@router.delete("/{briefcase_id}")
async def delete_briefcase(
    briefcase_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    briefcase = result.scalar_one_or_none()
    if not briefcase:
        raise HTTPException(status_code=404, detail="Briefcase not found")

    await session.delete(briefcase)
    await session.commit()
    return {"detail": "Briefcase deleted"}


# --- Reason CRUD ---
# IMPORTANT: reorder route MUST be registered before /{reason_id} routes
# so FastAPI doesn't try to parse "reorder" as a UUID.

@router.post("/{briefcase_id}/reasons", response_model=ReasonRead, status_code=201)
async def create_reason(
    briefcase_id: uuid.UUID,
    body: ReasonCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Briefcase not found")

    count_result = await session.execute(
        select(func.count(BriefcaseReason.id)).where(
            BriefcaseReason.briefcase_id == briefcase_id
        )
    )
    next_order = count_result.scalar()

    reason = BriefcaseReason(
        briefcase_id=briefcase_id,
        title=body.title,
        description=body.description,
        order=next_order,
    )
    session.add(reason)
    await session.commit()
    result = await session.execute(
        select(BriefcaseReason)
        .options(selectinload(BriefcaseReason.cases))
        .where(BriefcaseReason.id == reason.id)
    )
    return result.scalar_one()


@router.patch("/{briefcase_id}/reasons/reorder")
async def reorder_reasons(
    briefcase_id: uuid.UUID,
    body: ReasonReorder,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Briefcase not found")

    for i, reason_id in enumerate(body.reason_ids):
        result = await session.execute(
            select(BriefcaseReason).where(
                BriefcaseReason.id == reason_id,
                BriefcaseReason.briefcase_id == briefcase_id,
            )
        )
        reason = result.scalar_one_or_none()
        if reason:
            reason.order = i

    await session.commit()
    return {"detail": "Reasons reordered"}


@router.patch("/{briefcase_id}/reasons/{reason_id}", response_model=ReasonRead)
async def update_reason(
    briefcase_id: uuid.UUID,
    reason_id: uuid.UUID,
    body: ReasonUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Briefcase not found")

    result = await session.execute(
        select(BriefcaseReason).where(
            BriefcaseReason.id == reason_id,
            BriefcaseReason.briefcase_id == briefcase_id,
        )
    )
    reason = result.scalar_one_or_none()
    if not reason:
        raise HTTPException(status_code=404, detail="Reason not found")

    if body.title is not None:
        reason.title = body.title
    if body.description is not None:
        reason.description = body.description
    if body.content is not None:
        reason.content = body.content
        await _save_content_version(session, "reason", reason.id, body.content)

    await session.commit()
    result = await session.execute(
        select(BriefcaseReason)
        .options(selectinload(BriefcaseReason.cases))
        .where(BriefcaseReason.id == reason.id)
    )
    return result.scalar_one()


@router.delete("/{briefcase_id}/reasons/{reason_id}")
async def delete_reason(
    briefcase_id: uuid.UUID,
    reason_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Briefcase not found")

    result = await session.execute(
        select(BriefcaseReason).where(
            BriefcaseReason.id == reason_id,
            BriefcaseReason.briefcase_id == briefcase_id,
        )
    )
    reason = result.scalar_one_or_none()
    if not reason:
        raise HTTPException(status_code=404, detail="Reason not found")

    await session.delete(reason)
    await session.commit()
    return {"detail": "Reason deleted"}


# --- ReasonCase CRUD ---

@router.post(
    "/{briefcase_id}/reasons/{reason_id}/cases",
    response_model=ReasonCaseRead,
    status_code=201,
)
async def add_case_to_reason(
    briefcase_id: uuid.UUID,
    reason_id: uuid.UUID,
    body: ReasonCaseCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Briefcase not found")

    result = await session.execute(
        select(BriefcaseReason).where(
            BriefcaseReason.id == reason_id,
            BriefcaseReason.briefcase_id == briefcase_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Reason not found")

    result = await session.execute(select(Case).where(Case.id == body.case_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Case not found")

    result = await session.execute(
        select(BriefcaseReasonCase).where(
            BriefcaseReasonCase.reason_id == reason_id,
            BriefcaseReasonCase.case_id == body.case_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Case already added to this reason")

    count_result = await session.execute(
        select(func.count(BriefcaseReasonCase.id)).where(
            BriefcaseReasonCase.reason_id == reason_id
        )
    )
    next_order = count_result.scalar()

    entry = BriefcaseReasonCase(
        reason_id=reason_id,
        case_id=body.case_id,
        content=body.content,
        order=next_order,
    )
    session.add(entry)
    await session.flush()

    if body.content:
        await _save_content_version(session, "reason_case", entry.id, body.content)

    await session.commit()
    result = await session.execute(
        select(BriefcaseReasonCase).where(BriefcaseReasonCase.id == entry.id)
    )
    return result.scalar_one()


@router.patch(
    "/{briefcase_id}/reasons/{reason_id}/cases/{entry_id}",
    response_model=ReasonCaseRead,
)
async def update_reason_case(
    briefcase_id: uuid.UUID,
    reason_id: uuid.UUID,
    entry_id: uuid.UUID,
    body: ReasonCaseUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Briefcase not found")

    result = await session.execute(
        select(BriefcaseReasonCase).where(
            BriefcaseReasonCase.id == entry_id,
            BriefcaseReasonCase.reason_id == reason_id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    if body.content is not None:
        entry.content = body.content
        await _save_content_version(session, "reason_case", entry.id, body.content)
    if body.order is not None:
        entry.order = body.order

    await session.commit()
    result = await session.execute(
        select(BriefcaseReasonCase).where(BriefcaseReasonCase.id == entry.id)
    )
    return result.scalar_one()


@router.delete("/{briefcase_id}/reasons/{reason_id}/cases/{entry_id}")
async def remove_case_from_reason(
    briefcase_id: uuid.UUID,
    reason_id: uuid.UUID,
    entry_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Briefcase not found")

    result = await session.execute(
        select(BriefcaseReasonCase).where(
            BriefcaseReasonCase.id == entry_id,
            BriefcaseReasonCase.reason_id == reason_id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    await session.delete(entry)
    await session.commit()
    return {"detail": "Case removed from reason"}


# --- Version history ---

@router.get(
    "/{briefcase_id}/reasons/{reason_id}/versions",
    response_model=list[ContentVersionRead],
)
async def list_reason_versions(
    briefcase_id: uuid.UUID,
    reason_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Briefcase not found")

    result = await session.execute(
        select(ContentVersion)
        .where(
            ContentVersion.parent_type == "reason",
            ContentVersion.parent_id == reason_id,
        )
        .order_by(ContentVersion.version.desc())
    )
    return result.scalars().all()


@router.get(
    "/{briefcase_id}/reasons/{reason_id}/cases/{entry_id}/versions",
    response_model=list[ContentVersionRead],
)
async def list_reason_case_versions(
    briefcase_id: uuid.UUID,
    reason_id: uuid.UUID,
    entry_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Briefcase not found")

    result = await session.execute(
        select(ContentVersion)
        .where(
            ContentVersion.parent_type == "reason_case",
            ContentVersion.parent_id == entry_id,
        )
        .order_by(ContentVersion.version.desc())
    )
    return result.scalars().all()


@router.post("/{briefcase_id}/versions/{version_id}/restore")
async def restore_version(
    briefcase_id: uuid.UUID,
    version_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Briefcase not found")

    result = await session.execute(
        select(ContentVersion).where(ContentVersion.id == version_id)
    )
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    if version.parent_type == "reason":
        result = await session.execute(
            select(BriefcaseReason).where(BriefcaseReason.id == version.parent_id)
        )
        parent = result.scalar_one_or_none()
        if parent:
            parent.content = version.content
            await _save_content_version(session, "reason", parent.id, version.content)
    elif version.parent_type == "reason_case":
        result = await session.execute(
            select(BriefcaseReasonCase).where(
                BriefcaseReasonCase.id == version.parent_id
            )
        )
        parent = result.scalar_one_or_none()
        if parent:
            parent.content = version.content
            await _save_content_version(
                session, "reason_case", parent.id, version.content
            )

    await session.commit()
    return {"detail": "Version restored"}


# --- AI Generation ---

PROVIDER_DEFAULTS: dict[str, str] = {
    "anthropic": "claude-haiku-4-5-20251001",
    "openai": "gpt-4o-mini",
    "google": "gemini-2.0-flash",
    "deepseek": "deepseek-chat",
}


def _call_ai(provider: str, api_key: str, model_override: str | None, prompt: str, max_tokens: int) -> str:
    model = model_override or PROVIDER_DEFAULTS.get(provider, "gpt-4o-mini")
    if provider == "anthropic":
        msg = anthropic.Anthropic(api_key=api_key).messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    elif provider in ("openai", "deepseek"):
        kwargs: dict = {"api_key": api_key}
        if provider == "deepseek":
            kwargs["base_url"] = "https://api.deepseek.com/v1"
        resp = openai.OpenAI(**kwargs).chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""
    elif provider == "google":
        import google.generativeai as genai  # type: ignore[import-untyped]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(model).generate_content(prompt).text
    raise ValueError(f"Unknown provider: {provider}")


async def _resolve_ai(user: User, session: AsyncSession) -> tuple[str, str, str | None]:
    """Return (provider, api_key, model_override) for the user, or fall back to global key."""
    result = await session.execute(
        select(UserAISettings).where(UserAISettings.user_id == user.id)
    )
    row = result.scalar_one_or_none()

    if row is not None:
        provider = row.provider
        key_map = {
            "anthropic": row.anthropic_api_key,
            "openai": row.openai_api_key,
            "google": row.google_api_key,
            "deepseek": row.deepseek_api_key,
        }
        api_key = key_map.get(provider)
        if not api_key:
            raise HTTPException(status_code=503, detail="AI provider not configured")
        return provider, api_key, row.model

    if not settings.claude_api_key:
        raise HTTPException(status_code=503, detail="AI generation not configured")
    return "anthropic", settings.claude_api_key, None


class GenerateResponse(BaseModel):
    content: str


@router.post(
    "/{briefcase_id}/reasons/{reason_id}/cases/{entry_id}/generate",
    response_model=GenerateResponse,
)
async def generate_case_content(
    briefcase_id: uuid.UUID,
    reason_id: uuid.UUID,
    entry_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    provider, api_key, model_override = await _resolve_ai(user, session)

    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Briefcase not found")

    result = await session.execute(
        select(BriefcaseReason).where(
            BriefcaseReason.id == reason_id,
            BriefcaseReason.briefcase_id == briefcase_id,
        )
    )
    reason = result.scalar_one_or_none()
    if not reason:
        raise HTTPException(status_code=404, detail="Reason not found")

    result = await session.execute(
        select(BriefcaseReasonCase)
        .options(selectinload(BriefcaseReasonCase.case))
        .where(
            BriefcaseReasonCase.id == entry_id,
            BriefcaseReasonCase.reason_id == reason_id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    case = entry.case
    reason_context = reason.title
    if reason.description:
        reason_context += f" — {reason.description}"
    citation = f" ({case.citation})" if case.citation else ""
    case_summary = case.summary or "No summary available."

    prompt = (
        "You are assisting a South African commercial lawyer preparing a legal argument.\n\n"
        f"The legal argument being made is: {reason_context}\n\n"
        f"The following case is cited in support:\n"
        f"**{case.case_name}** ({case.court}{citation})\n\n"
        f"Case summary: {case_summary}\n\n"
        "Write a concise 2–3 sentence note explaining how this case supports the argument. "
        "Write in plain legal English, suitable for a court submission."
    )

    generated = await asyncio.to_thread(_call_ai, provider, api_key, model_override, prompt, 512)

    if entry.content:
        await _save_content_version(session, "reason_case", entry.id, entry.content)
    entry.content = generated
    await _save_content_version(session, "reason_case", entry.id, generated)
    await session.commit()

    return GenerateResponse(content=generated)


@router.post(
    "/{briefcase_id}/reasons/{reason_id}/generate",
    response_model=GenerateResponse,
)
async def generate_reason_argument(
    briefcase_id: uuid.UUID,
    reason_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    provider, api_key, model_override = await _resolve_ai(user, session)

    result = await session.execute(
        select(Briefcase).where(
            Briefcase.id == briefcase_id, Briefcase.user_id == user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Briefcase not found")

    result = await session.execute(
        select(BriefcaseReason)
        .options(
            selectinload(BriefcaseReason.cases).selectinload(BriefcaseReasonCase.case)
        )
        .where(
            BriefcaseReason.id == reason_id,
            BriefcaseReason.briefcase_id == briefcase_id,
        )
    )
    reason = result.scalar_one_or_none()
    if not reason:
        raise HTTPException(status_code=404, detail="Reason not found")

    reason_context = reason.title
    if reason.description:
        reason_context += f" — {reason.description}"

    case_lines = []
    for entry in reason.cases:
        case = entry.case
        citation = f" ({case.citation})" if case.citation else ""
        note = entry.content or "[no note]"
        case_lines.append(f"- {case.case_name}{citation}: {note}")

    cases_block = "\n".join(case_lines) if case_lines else "No cases added yet."

    prompt = (
        "You are assisting a South African commercial lawyer preparing a legal argument.\n\n"
        f"The legal ground being argued is: {reason_context}\n\n"
        "The following cases have been collected in support, with notes on their relevance:\n\n"
        f"{cases_block}\n\n"
        "Write a synthesized legal argument of 3–5 sentences drawing on these cases, "
        "suitable for a court submission."
    )

    generated = await asyncio.to_thread(_call_ai, provider, api_key, model_override, prompt, 1024)

    if reason.content:
        await _save_content_version(session, "reason", reason.id, reason.content)
    reason.content = generated
    await _save_content_version(session, "reason", reason.id, generated)
    await session.commit()

    return GenerateResponse(content=generated)
