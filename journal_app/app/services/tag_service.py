"""Business logic for free-form tags (#travel #nepal ...)."""
from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Database
from app.models import Tag
from app.services.dto import TagDTO

_TAG_CLEAN_RE = re.compile(r"^[#\s]+")


def normalize_tag(raw: str) -> str:
    """Strip leading '#'/whitespace and lowercase, so '#Nepal' and 'nepal'
    are treated as the same tag."""
    return _TAG_CLEAN_RE.sub("", raw).strip().lower()


class TagService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def list_all_tags(self) -> list[TagDTO]:
        with self.db.session() as session:
            tags = session.execute(select(Tag).order_by(Tag.name)).scalars().all()
            return [TagDTO(id=t.id, name=t.name) for t in tags]

    def get_or_create_many(self, session: Session, raw_names: list[str]) -> list[Tag]:
        """Used internally by JournalService within an existing session/
        transaction so tag creation and journal linkage stay atomic."""
        names = sorted({normalize_tag(n) for n in raw_names if normalize_tag(n)})
        if not names:
            return []
        existing = {
            t.name: t
            for t in session.execute(select(Tag).where(Tag.name.in_(names))).scalars().all()
        }
        result = []
        for name in names:
            tag = existing.get(name)
            if tag is None:
                tag = Tag(name=name)
                session.add(tag)
                session.flush()
            result.append(tag)
        return result

    def parse_tag_input(self, text: str) -> list[str]:
        """Splits a free-typed tag field like '#travel #nepal, memories'
        into individual normalized tag names."""
        parts = re.split(r"[\s,]+", text)
        return [normalize_tag(p) for p in parts if normalize_tag(p)]
