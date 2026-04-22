import re

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base, get_async_session
from app.main import _rate_limit_requests, app

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def override_get_async_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    _rate_limit_requests.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[get_async_session] = override_get_async_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


def _extract_cookie_value(set_cookie_header: str, cookie_name: str) -> str | None:
    pattern = rf"(?:^|,\s*){re.escape(cookie_name)}=([^;,]+)"
    match = re.search(pattern, set_cookie_header)
    return match.group(1) if match else None


@pytest_asyncio.fixture
async def auth_headers(client, mocker):
    """Register a user, force-verify them, log in via cookie. Returns {} — auth via cookie."""
    mocker.patch("app.auth.email.resend.Emails.send", return_value={"id": "x"})

    await client.post(
        "/auth/register",
        json={"email": "testuser@example.com", "password": "StrongPass123!"},
    )

    from sqlalchemy import update

    from app.database import get_async_session
    from app.main import app as _app
    from app.models.user import User

    override = _app.dependency_overrides.get(get_async_session)
    if override:
        async for session in override():
            await session.execute(
                update(User)
                .where(User.email == "testuser@example.com")
                .values(is_verified=True)
            )
            await session.commit()

    r = await client.post(
        "/auth/login",
        data={"username": "testuser@example.com", "password": "StrongPass123!"},
    )
    access_token = _extract_cookie_value(r.headers.get("set-cookie", ""), "access_token")
    if access_token:
        client.cookies.set("access_token", access_token)
    return {}
