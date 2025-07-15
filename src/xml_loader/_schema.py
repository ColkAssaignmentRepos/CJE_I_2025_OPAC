from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from src.model.record import Record, Header, Metadata, DcndlSimple


class _TypedValue(BaseModel):
    value: str = ""
    type: Optional[str] = None


class _ResourceLink(BaseModel):
    resource: str = ""


class _Header(BaseModel):
    identifier: Optional[str] = None
    datestamp: Optional[str] = None


class _DcndlSimple(BaseModel):
    title: Optional[str] = None
    identifier: List[_TypedValue] = []
    creator: List[str] = []
    publisher: Optional[str] = None
    alternative: Optional[str] = None
    series_title: Optional[str] = None
    date: Optional[str] = None
    language: Optional[str] = None
    extent: Optional[str] = None
    material_type: Optional[str] = None
    access_rights: Optional[str] = None
    title_transcription: Optional[str] = None
    volume: Optional[str] = None
    publication_place: List[_TypedValue] = []
    issued: List[_TypedValue] = []
    subject: List[_TypedValue] = []
    see_also: List[_ResourceLink] = []
    same_as: List[_ResourceLink] = []
    thumbnail: List[_ResourceLink] = []


class _Metadata(BaseModel):
    dc: Optional[_DcndlSimple] = None


class _Record(BaseModel):
    header: Optional[_Header] = None
    metadata: Optional[_Metadata] = None

    @staticmethod
    def to_public(private_record: _Record) -> Record:
        if not private_record.header:
            raise ValueError("Header is missing")
        if not private_record.metadata or not private_record.metadata.dc:
            raise ValueError("Metadata or DcndlSimple is missing")

        # Pydantic V2では、**private_record.header.model_dump()のように展開するのが一般的
        return Record(
            header=Header(**private_record.header.model_dump(exclude_none=True)),
            metadata=Metadata(
                dc=DcndlSimple(**private_record.metadata.dc.model_dump(exclude_none=True))
            )
        )
