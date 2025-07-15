from __future__ import annotations

import math
from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import crud
from src.db.session import get_db
from src.model import Record

router = APIRouter()


class PaginatedRecordResponse(BaseModel):
    items: List[Record]
    total_items: int
    total_pages: int
    current_page: int
    per_page: int


class APIResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[dict] = None


@router.get("/search", response_model=PaginatedRecordResponse)
async def search_records(
        db: AsyncSession = Depends(get_db),
        q: str | None = Query(None, description="Search query for all fields (title and creator)."),
        title: str | None = Query(None, description="Search query for title."),
        creator: str | None = Query(None, description="Search query for creator."),
        page: int = Query(1, ge=1, description="Page number."),
        per_page: int = Query(20, ge=1, le=100, description="Items per page."),
):
    """
    Search for records with pagination.
    You can use `q` for a general search across title and creator,
    or use `title` and `creator` for specific field searches.
    """
    skip = (page - 1) * per_page
    records, total_items = await crud.search_records(
        db_session=db, q=q, title=title, creator=creator, skip=skip, limit=per_page
    )

    total_pages = math.ceil(total_items / per_page)

    return PaginatedRecordResponse(
        items=records,
        total_items=total_items,
        total_pages=total_pages,
        current_page=page,
        per_page=per_page,
    )
