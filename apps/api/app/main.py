"""FastAPI entrypoint for QuantTwin."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis, repository
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered digital twin services for quantitative finance codebases.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    repository.router,
    prefix="/api/v1/repo",
    tags=["Repository"],
)

app.include_router(
    analysis.router,
    prefix="/api/v1/analysis",
    tags=["Analysis"],
)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Report that the API process is available."""

    return {"status": "ok", "environment": settings.environment}
