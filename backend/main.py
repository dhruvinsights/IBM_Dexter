"""Application entrypoint for the IBM Dexter backend."""

from contextlib import asynccontextmanager
import logging
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import auth, pull_requests, repositories, reviews, webhooks
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown events."""
    logger.info("Starting IBM Dexter backend in %s mode", settings.app_env)
    yield
    logger.info("Shutting down IBM Dexter backend")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="IBM Dexter AI Code Reviewer backend API.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version}


app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(repositories.router, prefix="/api/v1", tags=["Repositories"])
app.include_router(pull_requests.router, prefix="/api/v1", tags=["Pull Requests"])
app.include_router(reviews.router, prefix="/api/v1", tags=["Reviews"])
app.include_router(webhooks.router, prefix="/api/v1", tags=["Webhooks"])

# Made with Bob
