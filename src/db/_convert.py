from __future__ import annotations
from datetime import timezone

from src import model
from src.db import _model as sa_model


def _convert_sa_to_pydantic(db_record: sa_model.Record) -> model.Record:
    """
    Converts a SQLAlchemy Record object to a Pydantic Record object.
    """
    # Find the header identifier from the list of identifiers
    header_identifier_obj = next(
        (id for id in db_record.identifiers if id.type == "dcterms:URI"), None
    )
    if not header_identifier_obj:
        raise ValueError(
            "Header identifier (dcterms:URI) not found in identifiers list"
        )

    return model.Record(
        header=model.Header(
            identifier=header_identifier_obj.value,
            datestamp=db_record.datestamp.replace(tzinfo=timezone.utc),
        ),
        metadata=model.Metadata(
            dc=model.DcndlSimple(
                title=db_record.title,
                publisher=db_record.publisher,
                alternative=db_record.alternative,
                series_title=db_record.series_title,
                date=db_record.date,
                language=db_record.language,
                extent=db_record.extent,
                material_type=db_record.material_type,
                access_rights=db_record.access_rights,
                title_transcription=db_record.title_transcription,
                volume=db_record.volume,
                # Map relationships
                creator=[creator.name for creator in db_record.creators],
                # Convert all identifiers from the DB
                identifier=[
                    model.TypedValue(value=id.value, type=id.type)
                    for id in db_record.identifiers
                ],
                publication_place=[
                    model.TypedValue(value=p.value, type=p.type)
                    for p in db_record.publication_places
                ],
                issued=[
                    model.TypedValue(value=i.value, type=i.type)
                    for i in db_record.issued
                ],
                subject=[
                    model.TypedValue(value=s.value, type=s.type)
                    for s in db_record.subjects
                ],
                see_also=[
                    model.ResourceLink(resource=sa.resource)
                    for sa in db_record.see_alsos
                ],
                same_as=[
                    model.ResourceLink(resource=sa.resource)
                    for sa in db_record.same_as_links
                ],
                thumbnail=[
                    model.ResourceLink(resource=th.resource)
                    for th in db_record.thumbnails
                ],
            )
        ),
    )
