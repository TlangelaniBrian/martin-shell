import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_chat_returns_reply(client, auth_headers):
    with patch("app.cases.router._call_ai", return_value="This case concerns X."):
        with patch(
            "app.cases.router._resolve_ai",
            new_callable=AsyncMock,
            return_value=("anthropic", "sk-fake", None),
        ):
            resp = await client.post(
                "/cases/1/chat",
                json={"message": "Summarise the key ratio.", "history": []},
            )
    # 404 acceptable when no seed data; 422/401/500 are failures
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert resp.json()["reply"] == "This case concerns X."


@pytest.mark.asyncio
async def test_chat_requires_auth(client):
    resp = await client.post(
        "/cases/1/chat",
        json={"message": "Hello", "history": []},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_chat_404_unknown_case(client, auth_headers):
    with patch(
        "app.cases.router._resolve_ai",
        new_callable=AsyncMock,
        return_value=("anthropic", "sk-fake", None),
    ):
        resp = await client.post(
            "/cases/999999/chat",
            json={"message": "Hello", "history": []},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_chat_with_seeded_case(client, auth_headers, mocker):
    """Happy path with an actual case row in the DB."""
    from app.database import get_async_session
    from app.main import app as _app
    from app.models.case import Case

    override = _app.dependency_overrides.get(get_async_session)
    case_id = None
    if override:
        async for session in override():
            case = Case(
                saflii_url="https://saflii.org/za/cases/ZASCA/2024/99.html",
                case_name="Test v Test",
                court="ZASCA",
                summary="A landmark case on contract law.",
            )
            session.add(case)
            await session.commit()
            await session.refresh(case)
            case_id = case.id

    with patch("app.cases.router._call_ai", return_value="This case held that X."):
        with patch(
            "app.cases.router._resolve_ai",
            new_callable=AsyncMock,
            return_value=("anthropic", "sk-fake", None),
        ):
            resp = await client.post(
                f"/cases/{case_id}/chat",
                json={"message": "What did this case decide?", "history": []},
            )

    assert resp.status_code == 200
    assert resp.json()["reply"] == "This case held that X."
