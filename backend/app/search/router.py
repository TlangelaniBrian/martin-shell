from datetime import date

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.search.service import autocomplete, search

router = APIRouter()


class SearchResult(BaseModel):
    id: int
    case_name: str
    court: str
    date_decided: date | None
    citation: str | None
    summary: str | None
    pdf_url: str | None
    saflii_url: str


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int
    page: int


class AutocompleteResponse(BaseModel):
    suggestions: list[str]


@router.get("/", response_model=SearchResponse)
async def search_cases(
    q: str | None = Query(None, max_length=500),
    court: str | None = Query(None, max_length=32),
    year_from: int | None = Query(None, ge=1900, le=2100),
    year_to: int | None = Query(None, ge=1900, le=2100),
    judge: str | None = Query(None, max_length=200),
    party: str | None = Query(None, max_length=200),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
):
    results, total = await search(
        session, q=q, court=court, year_from=year_from, year_to=year_to,
        judge=judge, party=party, page=page, limit=limit,
    )
    return SearchResponse(
        results=[SearchResult(**vars(r)) for r in results],
        total=total,
        page=page,
    )


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_cases(
    q: str = Query(..., min_length=2, max_length=200),
    session: AsyncSession = Depends(get_async_session),
):
    suggestions = await autocomplete(session, q)
    return AutocompleteResponse(suggestions=suggestions)
