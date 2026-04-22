import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, CookieTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_async_session
from app.models.user import OAuthAccount, User


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)


logger = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    async def on_after_register(self, user: User, request=None):
        try:
            await self.request_verify(user, request)
        except Exception:
            logger.warning("Failed to send verification email to %s", user.email)

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        from app.auth.email import send_reset_password_email

        try:
            await send_reset_password_email(user.email, token)
        except Exception:
            logger.warning("Failed to send password reset email to %s", user.email)

    async def on_after_request_verify(self, user: User, token: str, request=None):
        from app.auth.email import send_verification_email

        try:
            await send_verification_email(user.email, token)
        except Exception:
            logger.warning("Failed to send verification email to %s", user.email)

    async def on_after_login(self, user: User, request=None, response=None):
        from app.models.refresh_token import RefreshToken

        if response is None:
            return

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        db_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.user_db.session.add(db_token)
        await self.user_db.session.commit()

        response.set_cookie(
            "refresh_token",
            raw_token,
            max_age=60 * 60 * 24 * 30,
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax" if not settings.cookie_secure else "none",
            path="/",
        )


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


cookie_transport = CookieTransport(
    cookie_name="access_token",
    cookie_max_age=900,
    cookie_httponly=True,
    cookie_secure=settings.cookie_secure,
    cookie_samesite="lax" if not settings.cookie_secure else "none",
)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.secret_key,
        lifetime_seconds=900,  # 15 minutes
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_optional_user = fastapi_users.current_user(active=True, optional=True)
