"""SQLAlchemy ORM models for the journal database.

Schema overview
----------------
User        -- single local profile + free-form JSON preferences blob
Topic       -- user-defined categories (Personal, Work, Travel, ...)
Journal     -- the entries themselves
Tag         -- free-form labels, many-to-many with Journal via JournalTag
JournalTag  -- association table
Media       -- attachments (e.g. an optional image) linked to a journal

Indexes are declared on the columns that drive the app's most common
queries: journal_date (calendar + date grouping), topic_id / mood /
is_favorite (filtering), and tag name (search/autocomplete).
"""
from __future__ import annotations

import datetime as dt

from app.utils.time_utils import utc_now
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    """A single local profile. The app is single-user/local-first, but
    modelling a User table keeps the door open for multi-profile support
    later without a schema migration."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, default="You")
    preferences = Column(Text, nullable=True)  # JSON-encoded AppSettings
    created_at = Column(DateTime, default=utc_now, nullable=False)


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    color = Column(String(16), nullable=False, default="#8A9A5B")
    icon = Column(String(8), nullable=False, default="\U0001F4C1")
    created_at = Column(DateTime, default=utc_now, nullable=False)

    journals = relationship("Journal", back_populates="topic")


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (Index("ix_tags_name", "name"),)

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False, unique=True)

    journals = relationship("JournalTag", back_populates="tag", cascade="all, delete-orphan")


class Journal(Base):
    __tablename__ = "journals"
    __table_args__ = (
        Index("ix_journals_journal_date", "journal_date"),
        Index("ix_journals_topic_id", "topic_id"),
        Index("ix_journals_mood", "mood"),
        Index("ix_journals_is_favorite", "is_favorite"),
    )

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False, default="")
    content = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    journal_date = Column(Date, nullable=False, default=dt.date.today)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    mood = Column(String(20), nullable=True)
    is_favorite = Column(Boolean, nullable=False, default=False)
    word_count = Column(Integer, nullable=False, default=0)

    topic = relationship("Topic", back_populates="journals")
    tags = relationship("JournalTag", back_populates="journal", cascade="all, delete-orphan")
    media = relationship("Media", back_populates="journal", cascade="all, delete-orphan")

    @property
    def tag_names(self) -> list[str]:
        return [jt.tag.name for jt in self.tags if jt.tag is not None]


class JournalTag(Base):
    __tablename__ = "journal_tags"
    __table_args__ = (UniqueConstraint("journal_id", "tag_id", name="uq_journal_tag"),)

    journal_id = Column(Integer, ForeignKey("journals.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    journal = relationship("Journal", back_populates="tags")
    tag = relationship("Tag", back_populates="journals")


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True)
    journal_id = Column(Integer, ForeignKey("journals.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    journal = relationship("Journal", back_populates="media")
