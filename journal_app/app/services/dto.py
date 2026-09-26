"""Plain data-transfer objects the UI layer consumes.

The UI never touches SQLAlchemy ORM instances directly -- sessions are
short-lived (opened, used, closed within a service method), so handing a
detached ORM object to a widget risks DetachedInstanceError the moment it
reads a lazily-loaded relationship. DTOs sidestep that entirely and keep
the UI layer honestly decoupled from the persistence layer.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field


@dataclass(frozen=True)
class TopicDTO:
    id: int
    name: str
    color: str
    icon: str


@dataclass(frozen=True)
class TagDTO:
    id: int
    name: str


@dataclass(frozen=True)
class MediaDTO:
    id: int
    file_path: str


@dataclass(frozen=True)
class JournalDTO:
    id: int
    title: str
    content: str
    created_at: dt.datetime
    updated_at: dt.datetime
    journal_date: dt.date
    topic: TopicDTO | None
    mood: str | None
    is_favorite: bool
    word_count: int
    tags: list[str] = field(default_factory=list)
    media: list[MediaDTO] = field(default_factory=list)

    @property
    def preview(self) -> str:
        text = " ".join(self.content.split())
        return text if len(text) <= 140 else text[:140].rstrip() + "\u2026"


def topic_to_dto(topic) -> TopicDTO | None:
    if topic is None:
        return None
    return TopicDTO(id=topic.id, name=topic.name, color=topic.color, icon=topic.icon)


def journal_to_dto(journal) -> JournalDTO:
    return JournalDTO(
        id=journal.id,
        title=journal.title,
        content=journal.content,
        created_at=journal.created_at,
        updated_at=journal.updated_at,
        journal_date=journal.journal_date,
        topic=topic_to_dto(journal.topic),
        mood=journal.mood,
        is_favorite=journal.is_favorite,
        word_count=journal.word_count,
        tags=sorted(journal.tag_names),
        media=[MediaDTO(id=m.id, file_path=m.file_path) for m in journal.media],
    )
