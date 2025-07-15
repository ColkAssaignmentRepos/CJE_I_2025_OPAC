from __future__ import annotations

from typing import List, Tuple

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src import model
from src.db import _model as sa_model
from src.db._convert import _convert_sa_to_pydantic


async def __get_or_create_creator(
        db_session: AsyncSession, name: str
) -> sa_model.Creator:
    """
    Retrieve a creator by name, or create it if it doesn't exist.
    """
    stmt = select(sa_model.Creator).where(sa_model.Creator.name == name)
    result = await db_session.execute(stmt)
    creator = result.scalar_one_or_none()
    if not creator:
        creator = sa_model.Creator(name=name)  # type: ignore[call-arg]
        db_session.add(creator)
        # We flush to get the ID without committing the whole transaction
        await db_session.flush()
    return creator


async def create_record(
        db_session: AsyncSession, pydantic_record: model.Record
) -> model.Record:
    """
    Converts a Pydantic Record to a SQLAlchemy Record and saves it to the database.
    """
    # Handle many-to-many relationship for creators
    creators = [
        await __get_or_create_creator(db_session, name)
        for name in pydantic_record.metadata.dc.creator
    ]

    # Create the main SQLAlchemy Record object without relationship fields
    db_record = sa_model.Record(  # type: ignore[call-arg]
        datestamp=pydantic_record.header.datestamp,
        title=pydantic_record.metadata.dc.title,
        publisher=pydantic_record.metadata.dc.publisher,
        alternative=pydantic_record.metadata.dc.alternative,
        series_title=pydantic_record.metadata.dc.series_title,
        date=pydantic_record.metadata.dc.date,
        language=pydantic_record.metadata.dc.language,
        extent=pydantic_record.metadata.dc.extent,
        material_type=pydantic_record.metadata.dc.material_type,
        access_rights=pydantic_record.metadata.dc.access_rights,
        title_transcription=pydantic_record.metadata.dc.title_transcription,
        volume=pydantic_record.metadata.dc.volume,
    )

    # Assign relationship attributes after initialization
    db_record.creators = creators

    # Handle one-to-many relationships
    for p_identifier in pydantic_record.metadata.dc.identifier:
        db_record.identifiers.append(sa_model.Identifier(**p_identifier.model_dump()))

    for p_pub_place in pydantic_record.metadata.dc.publication_place:
        db_record.publication_places.append(
            sa_model.PublicationPlace(**p_pub_place.model_dump())
        )

    for p_issued in pydantic_record.metadata.dc.issued:
        db_record.issued.append(
            sa_model.Issued(value=str(p_issued.value), type=p_issued.type)  # type: ignore
        )

    for p_subject in pydantic_record.metadata.dc.subject:
        db_record.subjects.append(sa_model.Subject(**p_subject.model_dump()))

    for p_see_also in pydantic_record.metadata.dc.see_also:
        db_record.see_alsos.append(sa_model.SeeAlso(**p_see_also.model_dump()))

    for p_same_as in pydantic_record.metadata.dc.same_as:
        db_record.same_as_links.append(sa_model.SameAs(**p_same_as.model_dump()))

    for p_thumbnail in pydantic_record.metadata.dc.thumbnail:
        db_record.thumbnails.append(sa_model.Thumbnail(**p_thumbnail.model_dump()))

    db_session.add(db_record)
    await db_session.flush()

    # Re-fetch the record with all relationships loaded to avoid lazy loading issues.
    stmt = (
        select(sa_model.Record)
        .where(sa_model.Record.id == db_record.id)
        .options(
            selectinload(sa_model.Record.creators),
            selectinload(sa_model.Record.identifiers),
            selectinload(sa_model.Record.publication_places),
            selectinload(sa_model.Record.issued),
            selectinload(sa_model.Record.subjects),
            selectinload(sa_model.Record.see_alsos),
            selectinload(sa_model.Record.same_as_links),
            selectinload(sa_model.Record.thumbnails),
        )
    )
    result = await db_session.execute(stmt)
    loaded_db_record = result.scalar_one()

    return _convert_sa_to_pydantic(loaded_db_record)


async def search_records(
        db_session: AsyncSession,
        q: str | None = None,
        title: str | None = None,
        creator: str | None = None,
        skip: int = 0,
        limit: int = 20,
) -> Tuple[List[model.Record], int]:
    """
    Searches for records in the database with pagination.
    """
    stmt = select(sa_model.Record).options(
        selectinload(sa_model.Record.creators),
        selectinload(sa_model.Record.identifiers),
        selectinload(sa_model.Record.publication_places),
        selectinload(sa_model.Record.issued),
        selectinload(sa_model.Record.subjects),
        selectinload(sa_model.Record.see_alsos),
        selectinload(sa_model.Record.same_as_links),
        selectinload(sa_model.Record.thumbnails),
    )

    filters = []
    if q:
        search_terms = q.split()
        any_clauses = []
        for term in search_terms:
            any_clauses.append(
                or_(
                    sa_model.Record.title.ilike(f"%{term}%"),
                    sa_model.Record.creators.any(sa_model.Creator.name.ilike(f"%{term}%")),
                )
            )
        filters.append(and_(*any_clauses))

    if title:
        filters.append(sa_model.Record.title.ilike(f"%{title}%"))

    if creator:
        stmt = stmt.join(sa_model.Record.creators)
        filters.append(sa_model.Creator.name.ilike(f"%{creator}%"))

    if filters:
        stmt = stmt.where(and_(*filters)).distinct()

    # Get the total count of items before pagination
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_items_result = await db_session.execute(count_stmt)
    total_items = total_items_result.scalar_one()

    # Apply pagination
    paginated_stmt = stmt.offset(skip).limit(limit)
    result = await db_session.execute(paginated_stmt)
    db_records = result.scalars().all()

    pydantic_records = [_convert_sa_to_pydantic(rec) for rec in db_records]

    return pydantic_records, total_items
