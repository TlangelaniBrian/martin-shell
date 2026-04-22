import logging
import time
from collections import defaultdict

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import settings
from app.models import ai_settings  # noqa: F401 — registers UserAISettings model
from app.models import refresh_token  # noqa: F401 — registers RefreshToken model
from app.auth.router import (
    auth_router,
    custom_auth_router,
    google_oauth_router,
    microsoft_oauth_router,
    register_router,
    reset_router,
    users_router,
    verify_router,
)
from app.ai_settings.router import router as ai_settings_router
from app.briefcases.router import router as briefcases_router
from app.cases.router import router as cases_router
from app.database import get_async_session
from app.search.router import router as search_router

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}',
)
logger = logging.getLogger("martin")

# ---------------------------------------------------------------------------
# Rate-limit store (in-process; resets on restart — acceptable for free tier)
# ---------------------------------------------------------------------------
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
# Alias kept for test compatibility
_rate_limit_requests = _rate_limit_store

# (max_requests, window_seconds)
_RATE_LIMITS: dict[str, tuple[int, int]] = {
    "/auth/": (5, 60),
    "/search/": (30, 60),
    "/briefcases/": (20, 60),
}
_AI_GENERATE_LIMIT = (10, 60)  # per user for AI endpoints


def _check_rate_limit(key: str, max_req: int, window: int) -> bool:
    """Return True if the request should be allowed, False if rate-limited."""
    now = time.time()
    _rate_limit_store[key] = [t for t in _rate_limit_store[key] if now - t < window]
    if len(_rate_limit_store[key]) >= max_req:
        return False
    _rate_limit_store[key].append(now)
    return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    """IP-based rate limiting for auth, search, and briefcase endpoints."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        for prefix, (max_req, window) in _RATE_LIMITS.items():
            if path.startswith(prefix):
                if not _check_rate_limit(f"{prefix}:{client_ip}", max_req, window):
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many requests"},
                        headers={"Retry-After": str(window)},
                    )
                break

        # AI generate endpoints get a tighter per-user limit
        if "/generate" in path and request.method == "POST":
            user_id = request.headers.get("X-User-ID", client_ip)
            max_req, window = _AI_GENERATE_LIMIT
            if not _check_rate_limit(f"ai:{user_id}", max_req, window):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "AI generation rate limit exceeded"},
                    headers={"Retry-After": str(window)},
                )

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every response."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with method, path, status, and duration."""

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000)
        logger.info(
            "%s %s %s %dms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


app = FastAPI(title="Martin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Cookie"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "An internal error occurred"})


app.include_router(custom_auth_router, prefix="/auth", tags=["auth"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(register_router, prefix="/auth", tags=["auth"])
app.include_router(verify_router, prefix="/auth", tags=["auth"])
app.include_router(reset_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(google_oauth_router, prefix="/auth/oauth/google", tags=["auth"])
app.include_router(microsoft_oauth_router, prefix="/auth/oauth/microsoft", tags=["auth"])
app.include_router(cases_router, prefix="/cases", tags=["cases"])
app.include_router(search_router, prefix="/search", tags=["search"])
app.include_router(briefcases_router, prefix="/briefcases", tags=["briefcases"])
app.include_router(ai_settings_router, prefix="/users/me/ai-settings", tags=["ai-settings"])

# admin endpoints (must come after including users/auth routers)
from app.auth.router import admin_router
app.include_router(admin_router)


@app.get("/health")
async def health(session: AsyncSession = Depends(get_async_session)):
    try:
        from sqlalchemy import text
        await session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unhealthy"})
