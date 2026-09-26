"""Tests for TopicService: create/rename/style/delete + duplicate guard."""
from __future__ import annotations

import pytest

from app.services.topic_service import DuplicateTopicError, TopicNotFoundError


def test_default_topics_are_seeded(topic_service):
    topics = topic_service.list_topics()
    names = {t.name for t in topics}
    assert len(topics) == 8
    assert "Personal" in names and "Gratitude" in names


def test_create_topic(topic_service):
    topic = topic_service.create_topic("Fitness", "#7A9B6E", "\U0001F3C3")
    assert topic.name == "Fitness"
    assert topic.color == "#7A9B6E"


def test_create_topic_rejects_duplicate_name(topic_service):
    topic_service.create_topic("Fitness", "#7A9B6E", "\U0001F3C3")
    with pytest.raises(DuplicateTopicError):
        topic_service.create_topic("Fitness", "#000000", "\U0001F600")


def test_create_topic_rejects_empty_name(topic_service):
    with pytest.raises(ValueError):
        topic_service.create_topic("   ")


def test_rename_topic(topic_service):
    topic = topic_service.create_topic("Fitness", "#7A9B6E", "\U0001F3C3")
    renamed = topic_service.rename_topic(topic.id, "Health")
    assert renamed.name == "Health"


def test_rename_missing_topic_raises(topic_service):
    with pytest.raises(TopicNotFoundError):
        topic_service.rename_topic(999999, "Nope")


def test_update_style(topic_service):
    topic = topic_service.create_topic("Fitness", "#7A9B6E", "\U0001F3C3")
    updated = topic_service.update_style(topic.id, color="#111111")
    assert updated.color == "#111111"
    assert updated.icon == "\U0001F3C3"  # unchanged


def test_delete_topic_removes_it_and_returns_affected_count(topic_service, journal_service):
    topic = topic_service.create_topic("Fitness", "#7A9B6E", "\U0001F3C3")
    journal_service.create_journal(title="A", content="x", topic_id=topic.id)
    journal_service.create_journal(title="B", content="y", topic_id=topic.id)
    affected = topic_service.delete_topic(topic.id)
    assert affected == 2
    remaining = [t for t in topic_service.list_topics() if t.id == topic.id]
    assert remaining == []


def test_journal_count(topic_service, journal_service):
    topic = topic_service.create_topic("Fitness", "#7A9B6E", "\U0001F3C3")
    assert topic_service.journal_count(topic.id) == 0
    journal_service.create_journal(title="A", content="x", topic_id=topic.id)
    assert topic_service.journal_count(topic.id) == 1
