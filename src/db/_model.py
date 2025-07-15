from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    UUID,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    declared_attr,
    declarative_base,
)

Base = declarative_base()


# --- Mixin Classes for DRY principle ---


class TypedValueMixin:
    """Mixin for models that represent a value with an optional type."""

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    value: Mapped[str] = mapped_column(String)
    type: Mapped[str | None] = mapped_column(String, nullable=True)

    @declared_attr
    def record_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(ForeignKey("records.id"))


class ResourceLinkMixin:
    """Mixin for models that represent a resource link."""

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    resource: Mapped[str] = mapped_column(String)

    @declared_attr
    def record_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(ForeignKey("records.id"))


# --- Association Model ---


class RecordCreatorAssociation(Base):
    __tablename__ = "record_creator_association"

    record_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("records.id"), primary_key=True
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("creators.id"), primary_key=True
    )


# --- Main Models ---


class Record(Base):
    __tablename__ = "records"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    # Header fields
    datestamp: Mapped[datetime] = mapped_column(DateTime)

    # DcndlSimple direct fields
    title: Mapped[str] = mapped_column(String)
    publisher: Mapped[str | None] = mapped_column(String, nullable=True)
    alternative: Mapped[str | None] = mapped_column(String, nullable=True)
    series_title: Mapped[str | None] = mapped_column(String, nullable=True)
    date: Mapped[str | None] = mapped_column(String, nullable=True)
    language: Mapped[str | None] = mapped_column(String, nullable=True)
    extent: Mapped[str | None] = mapped_column(String, nullable=True)
    material_type: Mapped[str | None] = mapped_column(String, nullable=True)
    access_rights: Mapped[str | None] = mapped_column(String, nullable=True)
    title_transcription: Mapped[str | None] = mapped_column(String, nullable=True)
    volume: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    creators: Mapped[List["Creator"]] = relationship(
        secondary="record_creator_association", back_populates="records"
    )
    identifiers: Mapped[List["Identifier"]] = relationship(
        back_populates="record", cascade="all, delete-orphan"
    )
    publication_places: Mapped[List["PublicationPlace"]] = relationship(
        back_populates="record", cascade="all, delete-orphan"
    )
    issued: Mapped[List["Issued"]] = relationship(
        back_populates="record", cascade="all, delete-orphan"
    )
    subjects: Mapped[List["Subject"]] = relationship(
        back_populates="record", cascade="all, delete-orphan"
    )
    see_alsos: Mapped[List["SeeAlso"]] = relationship(
        back_populates="record", cascade="all, delete-orphan"
    )
    same_as_links: Mapped[List["SameAs"]] = relationship(
        back_populates="record", cascade="all, delete-orphan"
    )
    thumbnails: Mapped[List["Thumbnail"]] = relationship(
        back_populates="record", cascade="all, delete-orphan"
    )


class Creator(Base):
    __tablename__ = "creators"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    name: Mapped[str] = mapped_column(String, unique=False, index=True)

    records: Mapped[List["Record"]] = relationship(
        secondary="record_creator_association", back_populates="creators"
    )


# --- TypedValue-based Models ---


class Identifier(TypedValueMixin, Base):
    __tablename__ = "identifiers"

    record: Mapped["Record"] = relationship(back_populates="identifiers")

    __table_args__ = (
        UniqueConstraint("value", "type", "record_id", name="_identifier_uc"),
    )


class PublicationPlace(TypedValueMixin, Base):
    __tablename__ = "publication_places"

    record: Mapped["Record"] = relationship(back_populates="publication_places")


class Issued(TypedValueMixin, Base):
    __tablename__ = "issued"

    record: Mapped["Record"] = relationship(back_populates="issued")


class Subject(TypedValueMixin, Base):
    __tablename__ = "subjects"

    record: Mapped["Record"] = relationship(back_populates="subjects")


# --- ResourceLink-based Models ---


class SeeAlso(ResourceLinkMixin, Base):
    __tablename__ = "see_alsos"

    record: Mapped["Record"] = relationship(back_populates="see_alsos")


class SameAs(ResourceLinkMixin, Base):
    __tablename__ = "same_as_links"

    record: Mapped["Record"] = relationship(back_populates="same_as_links")


class Thumbnail(ResourceLinkMixin, Base):
    __tablename__ = "thumbnails"

    record: Mapped["Record"] = relationship(back_populates="thumbnails")
