import logging
import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.core.config import settings
from app.database.init_db import init_db
from app.api.routes import members, memberships, payments, dashboard, plans, body_measurements, attendance, store, backup, notifications

logger = logging.getLogger(__name__)


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

    # TD-38: explicit methods, headers and no credentials (no cookie/session auth).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    # Database startup event
    @app.on_event("startup")
    def startup_event() -> None:
        """Initialize database on startup."""
        init_db()

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

    # Include routers
    app.include_router(members.router, prefix="/api")
    app.include_router(memberships.router, prefix="/api")
    app.include_router(payments.router, prefix="/api")
    app.include_router(dashboard.router, prefix="/api")
    app.include_router(plans.router, prefix="/api")
    app.include_router(body_measurements.router, prefix="/api")
    app.include_router(attendance.router, prefix="/api")
    app.include_router(store.router, prefix="/api")
    app.include_router(backup.router, prefix="/api")
    app.include_router(notifications.router, prefix="/api")

    # Health check endpoint
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
