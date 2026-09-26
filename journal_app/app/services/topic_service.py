"""Business logic for user-defined topics (create/rename/delete/color)."""
from __future__ import annotations

import logging

from sqlalchemy import select

from app.database import Database
from app.models import Journal, Topic
from app.services.dto import TopicDTO, topic_to_dto

logger = logging.getLogger(__name__)


class TopicNotFoundError(Exception):
    pass


class DuplicateTopicError(Exception):
    pass


class TopicService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def list_topics(self) -> list[TopicDTO]:
        with self.db.session() as session:
            topics = session.execute(select(Topic).order_by(Topic.name)).scalars().all()
            return [topic_to_dto(t) for t in topics]

    def create_topic(self, name: str, color: str = "#8A9A5B", icon: str = "\U0001F4C1") -> TopicDTO:
        name = name.strip()
        if not name:
            raise ValueError("Topic name cannot be empty")
        with self.db.session() as session:
            exists = session.execute(select(Topic).where(Topic.name == name)).scalar_one_or_none()
            if exists is not None:
                raise DuplicateTopicError(f"Topic '{name}' already exists")
            topic = Topic(name=name, color=color, icon=icon)
            session.add(topic)
            session.commit()
            return topic_to_dto(topic)

    def rename_topic(self, topic_id: int, new_name: str) -> TopicDTO:
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Topic name cannot be empty")
        with self.db.session() as session:
            topic = session.get(Topic, topic_id)
            if topic is None:
                raise TopicNotFoundError(f"Topic {topic_id} not found")
            topic.name = new_name
            session.commit()
            return topic_to_dto(topic)

    def update_style(self, topic_id: int, *, color: str | None = None, icon: str | None = None) -> TopicDTO:
        with self.db.session() as session:
            topic = session.get(Topic, topic_id)
            if topic is None:
                raise TopicNotFoundError(f"Topic {topic_id} not found")
            if color is not None:
                topic.color = color
            if icon is not None:
                topic.icon = icon
            session.commit()
            return topic_to_dto(topic)

    def delete_topic(self, topic_id: int) -> int:
        """Deletes the topic and un-assigns it from any journals (journals
        are never deleted as a side effect of removing a topic). Returns
        the number of journals that were affected."""
        with self.db.session() as session:
            topic = session.get(Topic, topic_id)
            if topic is None:
                return 0
            affected = session.query(Journal).filter(Journal.topic_id == topic_id).update(
                {Journal.topic_id: None}
            )
            session.delete(topic)
            session.commit()
            return affected

    def journal_count(self, topic_id: int) -> int:
        with self.db.session() as session:
            return session.query(Journal).filter(Journal.topic_id == topic_id).count()
