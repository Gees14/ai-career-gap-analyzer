from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler, generic_error_handler
from app.core.logging import setup_logging
from app.api import cv, jobs, skills, match, health

setup_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered career gap analyser. "
        "Upload a CV, provide job descriptions, and receive an explainable fit score, "
        "skill gap analysis, and structured improvement plan."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, generic_error_handler)

app.include_router(health.router)
app.include_router(cv.router)
app.include_router(jobs.router)
app.include_router(skills.router)
app.include_router(match.router)
