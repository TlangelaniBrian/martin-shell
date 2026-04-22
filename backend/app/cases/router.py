import asyncio
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.users import current_active_user
from app.briefcases.router import _call_ai, _resolve_ai
from app.database import get_async_session
from app.models.case import Case
from app.models.user import User

router = APIRouter()


class CaseSummary(BaseModel):
    id: int
    saflii_url: str
    citation: str | None
    case_number: str | None
    case_name: str
    court: str
    date_decided: date | None
    judge: str | None

    model_config = {"from_attributes": True}


class CaseDetail(CaseSummary):
    summary: str | None
    full_text: str | None
    pdf_url: str | None
    pdf_storage_key: str | None

    model_config = {"from_attributes": True}


class CaseListResponse(BaseModel):
    cases: list[CaseSummary]
    total: int


@router.get("/", response_model=CaseListResponse)
async def list_cases(
    court: str | None = Query(None, max_length=32),
    search: str | None = Query(None, max_length=500),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Case)
    count_query = select(func.count(Case.id))

    if court:
        query = query.where(Case.court == court)
        count_query = count_query.where(Case.court == court)

    if search:
        query = query.where(Case.case_name.ilike(f"%{search}%"))
        count_query = count_query.where(Case.case_name.ilike(f"%{search}%"))

    query = query.order_by(Case.date_decided.desc()).offset(offset).limit(limit)

    result = await session.execute(query)
    cases = result.scalars().all()

    total_result = await session.execute(count_query)
    total = total_result.scalar()

    return CaseListResponse(cases=cases, total=total)


@router.get("/{case_id}", response_model=CaseDetail)
async def get_case(
    case_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str


@router.post("/{case_id}/chat", response_model=ChatResponse)
async def chat_about_case(
    case_id: int,
    body: ChatRequest,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    provider, api_key, model_override = await _resolve_ai(user, session)

    citation = f" ({case.citation})" if case.citation else ""
    case_summary = case.summary or "No summary available."
    system = (
        "You are an AI legal research assistant helping a South African lawyer. "
        f"The user is asking about the following case:\n\n"
        f"**{case.case_name}** — {case.court}{citation}\n\n"
        f"Summary: {case_summary}\n\n"
        "Answer concisely in plain legal English."
    )

    history_lines = "\n".join(
        f"{m.role.capitalize()}: {m.content}" for m in body.history
    )
    prompt = f"{system}\n\n{history_lines}\nUser: {body.message}\nAssistant:"

    reply = await asyncio.to_thread(_call_ai, provider, api_key, model_override, prompt, 512)
    return ChatResponse(reply=reply)
