"""Local full-text-ish search across title, content, topic, and tags.

Uses SQL LIKE with indexed supporting columns rather than SQLite FTS5 to
keep the schema simple; for a local single-user journal (thousands, not
millions, of rows) this stays comfortably fast. Swapping in FTS5 later
would only touch this file.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from app.database import Database
from app.models import Journal, JournalTag, Tag, Topic
from app.services.dto import JournalDTO, journal_to_dto


@dataclass
class SearchFilters:
    query: str = ""
    topic_id: int | None = None
    mood: str | None = None
    favorites_only: bool = False
    date_from: dt.date | None = None
    date_to: dt.date | None = None


class SearchService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def search(self, filters: SearchFilters, limit: int = 200) -> list[JournalDTO]:
        query = (
            select(Journal)
            .options(
                joinedload(Journal.topic),
                joinedload(Journal.tags).joinedload(JournalTag.tag),
                joinedload(Journal.media),
            )
            .order_by(Journal.journal_date.desc(), Journal.created_at.desc())
        )

        text = filters.query.strip()
        if text:
            like = f"%{text}%"
            query = query.outerjoin(Journal.topic).outerjoin(Journal.tags).outerjoin(JournalTag.tag)
            query = query.where(
                or_(
                    Journal.title.ilike(like),
                    Journal.content.ilike(like),
                    Topic.name.ilike(like),
                    Tag.name.ilike(like),
                )
            ).distinct()

        if filters.topic_id is not None:
            query = query.where(Journal.topic_id == filters.topic_id)
        if filters.mood is not None:
            query = query.where(Journal.mood == filters.mood)
        if filters.favorites_only:
            query = query.where(Journal.is_favorite.is_(True))
        if filters.date_from is not None:
            query = query.where(Journal.journal_date >= filters.date_from)
        if filters.date_to is not None:
            query = query.where(Journal.journal_date <= filters.date_to)

        query = query.limit(limit)
        with self.db.session() as session:
            journals = session.execute(query).unique().scalars().all()
            return [journal_to_dto(j) for j in journals]
