import logging
import sys
from collections import defaultdict
from pathlib import Path
from time import time

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.core.config import settings
from app.database.init_db import init_db
from app.api.deps import require_active_user, require_module
from app.api.routes import (
    members, memberships, payments, dashboard, plans,
    body_measurements, attendance, store, backup, notifications, auth, config,
    superadmin,
)

logger = logging.getLogger(__name__)

# In-memory sliding-window state for login rate limiting.
# Keyed by client IP; value = list of request timestamps within the current window.
# Reset on container restart — acceptable for single-PC Local Edition.
# Memory is bounded: one entry per unique IP × max_attempts timestamps.
_login_attempts: defaultdict[str, list[float]] = defaultdict(list)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    # TD-36: OpenAPI docs disabled in production (debug=False).
    app = FastAPI(
        title=settings.project_name,
        version=settings.project_version,
        debug=settings.debug,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    # TD-38: explicit methods, headers and no credentials (JWT via Authorization header).
    # Authorization added to allow_headers for Bearer token support (F2).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # TD-42: sliding-window rate limiter for POST /api/auth/login.
    # Disabled in debug mode (development). Applies only to the login endpoint;
    # all other paths — including /api/health — pass through unconditionally.
    # The 429 response traverses CORSMiddleware on its way out, so CORS headers
    # are present even when the request is rejected.
    @app.middleware("http")
    async def _login_rate_limiter(request: Request, call_next):
        if (
            not settings.debug
            and request.method == "POST"
            and request.url.path == "/api/auth/login"
        ):
            ip = request.client.host or "unknown"
            now = time()
            window = settings.login_rate_limit_window
            max_attempts = settings.login_rate_limit_max_attempts

            # Discard timestamps outside the current window on every request —
            # keeps memory usage bounded without a background cleanup task.
            _login_attempts[ip] = [t for t in _login_attempts[ip] if now - t < window]

            if len(_login_attempts[ip]) >= max_attempts:
                logger.warning(
                    "Rate limit exceeded on /api/auth/login | ip=%s attempts=%d window=%ds",
                    ip, len(_login_attempts[ip]), window,
                )
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Demasiados intentos. Intenta nuevamente en un momento."},
                )

            _login_attempts[ip].append(now)

        return await call_next(request)

    # Database startup — also loads module cache into memory.
    @app.on_event("startup")
    def startup_event() -> None:
        init_db()
        from app.core.module_cache import load_from_db
        load_from_db()

    # Validation error handler — logs field/reason for 422 errors.
    # SEC-013: never log the client-submitted value (`input`/`ctx` may carry PII:
    # names, documents, emails). Keep `loc` (field) + `type` + `msg` for diagnosis.
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        sanitized = [
            {"loc": e.get("loc"), "type": e.get("type"), "msg": e.get("msg")}
            for e in exc.errors()
        ]
        logger.warning(
            "422 Validation Error | %s %s | detail: %s",
            request.method, request.url, sanitized
        )
        return JSONResponse(status_code=422, content={"detail": jsonable_encoder(sanitized)})

    # Public routers — no authentication required.
    app.include_router(auth.router, prefix="/api")
    app.include_router(config.router, prefix="/api")

    # Core routers — require valid non-temporary token.
    _protected = {"dependencies": [Depends(require_active_user)]}
    app.include_router(members.router, prefix="/api", **_protected)
    app.include_router(memberships.router, prefix="/api", **_protected)
    app.include_router(payments.router, prefix="/api", **_protected)
    app.include_router(dashboard.router, prefix="/api", **_protected)
    app.include_router(plans.router, prefix="/api", **_protected)
    app.include_router(attendance.router, prefix="/api", **_protected)
    app.include_router(backup.router, prefix="/api", **_protected)

    # Premium module routers — always registered; require_module enforces licensing at
    # request time (A4). super_admin bypasses checks. Returns 403 (not 404) when inactive.
    # Falls back to active=True when the gym is not in the module cache (A3).
    app.include_router(
        notifications.router, prefix="/api",
        dependencies=[Depends(require_module("MODULE_NOTIFICATIONS"))],
    )
    app.include_router(
        body_measurements.router, prefix="/api",
        dependencies=[Depends(require_module("MODULE_BODY_TRACKING"))],
    )
    app.include_router(
        store.router, prefix="/api",
        dependencies=[Depends(require_module("MODULE_STORE"))],
    )

    # Super Admin router — requires role='super_admin' (enforced inside router).
    app.include_router(superadmin.router, prefix="/api")

    # Health check endpoint — public (no auth required, used by Docker and monitoring).
    @app.get("/api/health")
    def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok", "version": settings.project_version}

    # Root endpoint
    @app.get("/")
    def root() -> dict[str, str]:
        """Root endpoint."""
        return {"message": f"Welcome to {settings.project_name}"}

    return app


# Create app instance
app = create_app()


# For uvicorn direct execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
