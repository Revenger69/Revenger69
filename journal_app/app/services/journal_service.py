"""Business logic for creating, editing, browsing, and organizing journal
entries. This is the layer the UI talks to -- it never touches SQL/ORM
concerns directly beyond what SQLAlchemy needs, and it always hands back
DTOs so the UI stays decoupled from session lifecycles.
"""
from __future__ import annotations

import datetime as dt
import logging

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database import Database
from app.models import Journal, JournalTag, Tag, Topic
from app.services.dto import JournalDTO, journal_to_dto
from app.services.tag_service import TagService
from app.utils.date_utils import compute_streak, word_count
from app.utils.time_utils import utc_now

logger = logging.getLogger(__name__)


class JournalNotFoundError(Exception):
    pass


class JournalService:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.tag_service = TagService(db)

    # ------------------------------------------------------------------ #
    # Create / update / delete
    # ------------------------------------------------------------------ #
    def create_journal(
        self,
        *,
        title: str = "",
        content: str = "",
        journal_date: dt.date | None = None,
        topic_id: int | None = None,
        mood: str | None = None,
        tags: list[str] | None = None,
        is_favorite: bool = False,
    ) -> JournalDTO:
        journal_date = journal_date or dt.date.today()
        with self.db.session() as session:
            journal = Journal(
                title=title.strip(),
                content=content,
                journal_date=journal_date,
                topic_id=topic_id,
                mood=mood,
                is_favorite=is_favorite,
                word_count=word_count(content),
            )
            session.add(journal)
            session.flush()  # obtain journal.id before linking tags
            self._set_tags(session, journal, tags or [])
            session.commit()
            journal_id = journal.id
        return self.get_journal(journal_id)

    def update_journal(
        self,
        journal_id: int,
        *,
        title: str | None = None,
        content: str | None = None,
        journal_date: dt.date | None = None,
        topic_id: int | None = ...,
        mood: str | None = ...,
        tags: list[str] | None = None,
        is_favorite: bool | None = None,
    ) -> JournalDTO:
        """Partial update. `topic_id`/`mood` use `...` as the sentinel for
        "leave unchanged" since `None` is itself a valid value (no topic /
        no mood)."""
        with self.db.session() as session:
            journal = session.get(Journal, journal_id)
            if journal is None:
                raise JournalNotFoundError(f"Journal {journal_id} not found")
            if title is not None:
                journal.title = title.strip()
            if content is not None:
                journal.content = content
                journal.word_count = word_count(content)
            if journal_date is not None:
                journal.journal_date = journal_date
            if topic_id is not ...:
                journal.topic_id = topic_id
            if mood is not ...:
                journal.mood = mood
            if is_favorite is not None:
                journal.is_favorite = is_favorite
            journal.updated_at = utc_now()
            if tags is not None:
                self._set_tags(session, journal, tags)
            session.commit()
        return self.get_journal(journal_id)

    def toggle_favorite(self, journal_id: int) -> JournalDTO:
        with self.db.session() as session:
            journal = session.get(Journal, journal_id)
            if journal is None:
                raise JournalNotFoundError(f"Journal {journal_id} not found")
            journal.is_favorite = not journal.is_favorite
            session.commit()
        return self.get_journal(journal_id)

    def delete_journal(self, journal_id: int) -> None:
        with self.db.session() as session:
            journal = session.get(Journal, journal_id)
            if journal is None:
                return
            session.delete(journal)
            session.commit()

    def _set_tags(self, session, journal: Journal, tag_names: list[str]) -> None:
        journal.tags.clear()
        for tag in self.tag_service.get_or_create_many(session, tag_names):
            session.add(JournalTag(journal_id=journal.id, tag_id=tag.id))

    # ------------------------------------------------------------------ #
    # Reads
    # ------------------------------------------------------------------ #
    def _base_query(self):
        return select(Journal).options(
            joinedload(Journal.topic),
            joinedload(Journal.tags).joinedload(JournalTag.tag),
            joinedload(Journal.media),
        )

    def get_journal(self, journal_id: int) -> JournalDTO:
        with self.db.session() as session:
            journal = session.execute(
                self._base_query().where(Journal.id == journal_id)
            ).unique().scalar_one_or_none()
            if journal is None:
                raise JournalNotFoundError(f"Journal {journal_id} not found")
            return journal_to_dto(journal)

    def list_journals(
        self,
        *,
        topic_id: int | None = None,
        mood: str | None = None,
        favorites_only: bool = False,
        date_from: dt.date | None = None,
        date_to: dt.date | None = None,
        limit: int | None = None,
    ) -> list[JournalDTO]:
        query = self._base_query().order_by(Journal.journal_date.desc(), Journal.created_at.desc())
        if topic_id is not None:
            query = query.where(Journal.topic_id == topic_id)
        if mood is not None:
            query = query.where(Journal.mood == mood)
        if favorites_only:
            query = query.where(Journal.is_favorite.is_(True))
        if date_from is not None:
            query = query.where(Journal.journal_date >= date_from)
        if date_to is not None:
            query = query.where(Journal.journal_date <= date_to)
        if limit is not None:
            query = query.limit(limit)
        with self.db.session() as session:
            journals = session.execute(query).unique().scalars().all()
            return [journal_to_dto(j) for j in journals]

    def get_recent(self, limit: int = 5) -> list[JournalDTO]:
        return self.list_journals(limit=limit)

    def get_journals_for_date(self, date: dt.date) -> list[JournalDTO]:
        return self.list_journals(date_from=date, date_to=date)

    def get_all_journal_dates(self) -> set[dt.date]:
        """Used by the calendar to mark which days have entries, and by the
        dashboard to compute the writing streak."""
        with self.db.session() as session:
            rows = session.execute(select(Journal.journal_date)).scalars().all()
            return set(rows)

    def current_streak(self) -> int:
        return compute_streak(self.get_all_journal_dates())

    def total_count(self) -> int:
        with self.db.session() as session:
            return session.query(Journal).count()

    # ------------------------------------------------------------------ #
    # Media (optional image attachments)
    # ------------------------------------------------------------------ #
    def attach_media(self, journal_id: int, file_path: str) -> JournalDTO:
        from app.models import Media

        with self.db.session() as session:
            journal = session.get(Journal, journal_id)
            if journal is None:
                raise JournalNotFoundError(f"Journal {journal_id} not found")
            session.add(Media(journal_id=journal_id, file_path=file_path))
            session.commit()
        return self.get_journal(journal_id)

    def remove_media(self, journal_id: int, media_id: int) -> JournalDTO:
        from app.models import Media

        with self.db.session() as session:
            media = session.get(Media, media_id)
            if media is not None and media.journal_id == journal_id:
                session.delete(media)
                session.commit()
        return self.get_journal(journal_id)
