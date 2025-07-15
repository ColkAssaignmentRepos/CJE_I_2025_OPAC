from __future__ import annotations

from datetime import datetime
from typing import Optional, List, TypeVar, Generic

from pydantic import BaseModel, Field

T = TypeVar("T")


class TypedValue(BaseModel, Generic[T]):
    value: T
    type: Optional[str] = None


class ResourceLink(BaseModel):
    resource: str


class Header(BaseModel):
    identifier: str
    datestamp: datetime


class DcndlSimple(BaseModel):
    title: str
    identifier: List[TypedValue[str]] = Field(..., min_length=1)
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

    publication_place: List[TypedValue[str]] = []
    issued: List[TypedValue[datetime | str]] = []
    subject: List[TypedValue[str]] = []

    see_also: List[ResourceLink] = []
    same_as: List[ResourceLink] = []
    thumbnail: List[ResourceLink] = []


class Metadata(BaseModel):
    dc: DcndlSimple


class Record(BaseModel):
    header: Header
    metadata: Metadata
