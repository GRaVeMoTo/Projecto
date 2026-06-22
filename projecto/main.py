from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from projecto.auth.router import router as auth_router
from projecto.exceptions import register_exception_handlers
from projecto.logging import configure_logging, get_logger
from projecto.projects.router import router as projects_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application startup and shutdown lifecycle."""
    configure_logging()
    logger.info("Starting Projecto API")
    yield
    logger.info("Shutting down Projecto API")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Projecto",
        description="Project Management Software - backend API",
        version="0.1.0",
        lifespan=lifespan,
    )
    register_exception_handlers(app)

    api_router = APIRouter()
    api_router.include_router(auth_router)
    api_router.include_router(projects_router)
    app.include_router(api_router)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok"}

    return app


app = create_app()
