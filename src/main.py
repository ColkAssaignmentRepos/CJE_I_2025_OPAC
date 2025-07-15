from fastapi import FastAPI

from src.api import search

app = FastAPI(
    title="OPAC API",
    description="API for searching library records.",
    version="0.1.0",
)

app.include_router(search.router, prefix="/api/v1", tags=["search"])
