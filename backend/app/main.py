from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import get_settings
from app.presentation.api.creative_router import creative_router
from app.presentation.api.router import router as story_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    allow_origins = (
        ["*"]
        if settings.cors_allow_origins.strip() == "*"
        else [item.strip() for item in settings.cors_allow_origins.split(",") if item.strip()]
    )
    allow_credentials = settings.cors_allow_origins.strip() != "*"
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(story_router)
    app.include_router(creative_router)
    return app


app = create_app()
