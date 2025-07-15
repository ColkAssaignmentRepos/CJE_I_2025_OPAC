from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api import search

app = FastAPI(
    title="OPAC API",
    description="API for searching library records.",
    version="0.1.0",
    docs_url="/api/docs",  # Move docs to avoid conflict
    openapi_url="/api/openapi.json",  # Move openapi to avoid conflict
)

# --- API Router ---
app.include_router(search.router, prefix="/api/v1", tags=["search"])

# --- Frontend Serving ---
FRONTEND_DIST_DIR = "frontend/dist"

# This will serve the static files (JS, CSS, etc.) and also serve index.html
# for any route under /ui/, because html=True is set.
app.mount("/ui", StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name="ui")


# --- Root Redirect ---
@app.get("/")
def read_root():
    """
    Redirects the root URL ('/') to the frontend application ('/ui/').
    """
    return RedirectResponse(url="/ui/")
