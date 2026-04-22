from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.case import Case
from app.voyage import AsyncVoyageClient

MODEL = "voyage-law-2"
SEMANTIC_TOP_K = 40
KEYWORD_TOP_K = 40


@dataclass
class CaseResult:
    id: int
    case_name: str
    court: str
    date_decided: date | None
    citation: str | None
    summary: str | None
    pdf_url: str | None
    saflii_url: str


def merge_rrf(
    keyword_ids: list[int],
    semantic_ids: list[int],
    k: int = 60,
) -> list[int]:
    scores: dict[int, float] = {}
    for rank, id_ in enumerate(keyword_ids):
        scores[id_] = scores.get(id_, 0) + 1 / (k + rank + 1)
    for rank, id_ in enumerate(semantic_ids):
        scores[id_] = scores.get(id_, 0) + 1 / (k + rank + 1)
    return sorted(scores, key=lambda id_: scores[id_], reverse=True)


def _apply_filters(
    query: Select,
    court: str | None,
    year_from: int | None,
    year_to: int | None,
    judge: str | None,
    party: str | None,
) -> Select:
    if court:
        query = query.where(Case.court == court)
    if year_from:
        query = query.where(func.extract("year", Case.date_decided) >= year_from)
    if year_to:
        query = query.where(func.extract("year", Case.date_decided) <= year_to)
    if judge:
        query = query.where(Case.judge.ilike(f"%{judge}%"))
    if party:
        query = query.where(Case.case_name.ilike(f"%{party}%"))
    return query


async def search(
    session: AsyncSession,
    q: str | None,
    court: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    judge: str | None = None,
    party: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[CaseResult], int]:
    if not q:
        base = _apply_filters(select(Case), court, year_from, year_to, judge, party)
        count_result = await session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = count_result.scalar_one()
        result = await session.execute(
            base.order_by(Case.date_decided.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        cases = result.scalars().all()
        return [_to_result(c) for c in cases], total

    # Keyword search via tsvector
    ts_query = func.plainto_tsquery("english", q)
    ts_vector = func.to_tsvector(
        "english",
        func.coalesce(Case.case_name, "")
        + " "
        + func.coalesce(Case.citation, "")
        + " "
        + func.coalesce(Case.summary, ""),
    )
    keyword_query = _apply_filters(
        select(Case.id).where(ts_vector.op("@@")(ts_query)),
        court, year_from, year_to, judge, party,
    ).limit(KEYWORD_TOP_K)
    keyword_result = await session.execute(keyword_query)
    keyword_ids = [row[0] for row in keyword_result]

    # Semantic search via pgvector cosine distance
    client = AsyncVoyageClient(api_key=settings.voyage_api_key)
    query_embedding = await client.embed([q], model=MODEL, input_type="query")
    query_vector = query_embedding[0]

    semantic_query = _apply_filters(
        select(Case.id)
        .where(Case.embedding.isnot(None))
        .order_by(Case.embedding.cosine_distance(query_vector)),
        court, year_from, year_to, judge, party,
    ).limit(SEMANTIC_TOP_K)
    semantic_result = await session.execute(semantic_query)
    semantic_ids = [row[0] for row in semantic_result]

    # Merge via RRF
    merged_ids = merge_rrf(keyword_ids, semantic_ids)
    total = len(merged_ids)

    page_ids = merged_ids[(page - 1) * limit : page * limit]
    if not page_ids:
        return [], total

    cases_result = await session.execute(
        select(Case).where(Case.id.in_(page_ids))
    )
    cases_by_id = {c.id: c for c in cases_result.scalars().all()}
    ordered = [cases_by_id[id_] for id_ in page_ids if id_ in cases_by_id]
    return [_to_result(c) for c in ordered], total


async def autocomplete(session: AsyncSession, q: str) -> list[str]:
    result = await session.execute(
        select(Case.case_name)
        .where(Case.case_name.ilike(f"%{q}%"))
        .limit(8)
    )
    return [row[0] for row in result]


def _to_result(case: Case) -> CaseResult:
    return CaseResult(
        id=case.id,
        case_name=case.case_name,
        court=case.court,
        date_decided=case.date_decided,
        citation=case.citation,
        summary=case.summary,
        pdf_url=case.pdf_url,
        saflii_url=case.saflii_url,
    )
