import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi_users.authentication import JWTStrategy
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.microsoft import MicrosoftGraphOAuth2
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import UserCreate, UserRead, UserUpdate
from app.auth.users import auth_backend, fastapi_users, current_active_user
from app.config import settings

_SECURE = settings.cookie_secure
_SAMESITE = "none" if _SECURE else "lax"
from app.database import get_async_session
from app.models.refresh_token import RefreshToken
from app.models.user import User

# Custom auth router — must be included BEFORE auth_router in main.py
custom_auth_router = APIRouter()


@custom_auth_router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
):
    raw_token = request.cookies.get("refresh_token")
    if raw_token:
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        result = await session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked.is_(False),
            )
        )
        db_token = result.scalar_one_or_none()
        if db_token:
            db_token.is_revoked = True
            await session.commit()

    response.delete_cookie("access_token", path="/", samesite=_SAMESITE, secure=_SECURE, httponly=True)
    response.delete_cookie("refresh_token", path="/", samesite=_SAMESITE, secure=_SECURE, httponly=True)
    return {"detail": "Logged out"}


@custom_auth_router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
    strategy: JWTStrategy = Depends(auth_backend.get_strategy),
):
    raw_token = request.cookies.get("refresh_token")
    if not raw_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked.is_(False),
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    db_token = result.scalar_one_or_none()
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_result = await session.execute(
        select(User).where(User.id == db_token.user_id, User.is_active.is_(True))
    )
    user = user_result.unique().scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Revoke old token
    db_token.is_revoked = True

    # Issue new refresh token
    new_raw = secrets.token_urlsafe(32)
    new_hash = hashlib.sha256(new_raw.encode()).hexdigest()
    new_expires = datetime.now(timezone.utc) + timedelta(days=30)
    session.add(RefreshToken(user_id=user.id, token_hash=new_hash, expires_at=new_expires))
    await session.commit()

    # Issue new access token
    access_token = await strategy.write_token(user)

    response.set_cookie(
        "access_token", access_token,
        max_age=900, httponly=True, secure=_SECURE, samesite=_SAMESITE, path="/",
    )
    response.set_cookie(
        "refresh_token", new_raw,
        max_age=60 * 60 * 24 * 30, httponly=True, secure=_SECURE, samesite=_SAMESITE, path="/",
    )
    return {"detail": "Tokens refreshed"}


google_oauth_client = GoogleOAuth2(
    settings.google_oauth_client_id,
    settings.google_oauth_client_secret,
)

microsoft_oauth_client = MicrosoftGraphOAuth2(
    settings.microsoft_oauth_client_id,
    settings.microsoft_oauth_client_secret,
)

auth_router = fastapi_users.get_auth_router(auth_backend, requires_verification=True)
register_router = fastapi_users.get_register_router(UserRead, UserCreate)
verify_router = fastapi_users.get_verify_router(UserRead)
reset_router = fastapi_users.get_reset_password_router()
users_router = fastapi_users.get_users_router(UserRead, UserUpdate)

google_oauth_router = fastapi_users.get_oauth_router(
    google_oauth_client,
    auth_backend,
    settings.secret_key,
    redirect_url=f"{settings.frontend_url}/auth/callback/google",
    associate_by_email=True,
)

microsoft_oauth_router = fastapi_users.get_oauth_router(
    microsoft_oauth_client,
    auth_backend,
    settings.secret_key,
    redirect_url=f"{settings.frontend_url}/auth/callback/microsoft",
    associate_by_email=True,
)

# role-based dependency
from fastapi import HTTPException, status
from app.models.user import UserRole

async def require_admin(user: User = Depends(current_active_user)) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return user

admin_router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])

@admin_router.get("/users", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User))
    result = result.unique()
    return result.scalars().all()

from pydantic import BaseModel


class RoleUpdate(BaseModel):
    role: UserRole


@admin_router.patch("/users/{user_id}/role", response_model=UserRead)
async def change_role(
    user_id: uuid.UUID,
    payload: RoleUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = payload.role
    await session.commit()
    await session.refresh(user)
    return user
