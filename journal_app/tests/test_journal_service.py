"""Tests for JournalService: CRUD, tags, favorites, streaks, media."""
from __future__ import annotations

import datetime as dt

import pytest

from app.services.journal_service import JournalNotFoundError


def test_create_journal_sets_word_count_and_defaults(journal_service):
    dto = journal_service.create_journal(title="  Hello  ", content="one two three four")
    assert dto.title == "Hello"
    assert dto.word_count == 4
    assert dto.is_favorite is False
    assert dto.journal_date == dt.date.today()
    assert dto.tags == []


def test_create_journal_with_topic_and_tags(journal_service, topic_service):
    topic = topic_service.create_topic("Wanderlust", "#4F9D9D", "\u2708")
    dto = journal_service.create_journal(
        title="Trip", content="Nepal was beautiful.", topic_id=topic.id, tags=["#Nepal", "memories", "nepal"]
    )
    assert dto.topic is not None
    assert dto.topic.name == "Wanderlust"
    # Duplicate/variant-cased tags should collapse to one normalized tag.
    assert dto.tags == ["memories", "nepal"]


def test_update_journal_partial_fields(journal_service):
    dto = journal_service.create_journal(title="Original", content="content")
    updated = journal_service.update_journal(dto.id, title="Updated Title")
    assert updated.title == "Updated Title"
    assert updated.content == "content"  # untouched


def test_update_journal_topic_id_none_sentinel_behavior(journal_service, topic_service):
    topic = topic_service.create_topic("Career", "#6E8AA6", "\U0001F4BC")
    dto = journal_service.create_journal(title="A", content="B", topic_id=topic.id)
    assert dto.topic.id == topic.id

    # Explicitly clearing the topic (topic_id=None) should remove it.
    cleared = journal_service.update_journal(dto.id, topic_id=None)
    assert cleared.topic is None

    # Not passing topic_id at all should leave it unchanged.
    unchanged = journal_service.update_journal(dto.id, title="A2")
    assert unchanged.topic is None  # still cleared from before


def test_update_journal_raises_for_missing_id(journal_service):
    with pytest.raises(JournalNotFoundError):
        journal_service.update_journal(9999, title="nope")


def test_toggle_favorite(journal_service):
    dto = journal_service.create_journal(title="A", content="B")
    assert dto.is_favorite is False
    toggled = journal_service.toggle_favorite(dto.id)
    assert toggled.is_favorite is True
    toggled_back = journal_service.toggle_favorite(dto.id)
    assert toggled_back.is_favorite is False


def test_delete_journal_removes_it(journal_service):
    dto = journal_service.create_journal(title="A", content="B")
    journal_service.delete_journal(dto.id)
    with pytest.raises(JournalNotFoundError):
        journal_service.get_journal(dto.id)


def test_delete_journal_is_safe_for_missing_id(journal_service):
    journal_service.delete_journal(999999)  # should not raise


def test_list_journals_filters(journal_service, topic_service):
    topic = topic_service.create_topic("Big Ideas", "#B08968", "\U0001F4A1")
    journal_service.create_journal(title="A", content="x", topic_id=topic.id, mood="happy")
    journal_service.create_journal(title="B", content="y", mood="sad", is_favorite=True)
    journal_service.create_journal(title="C", content="z", journal_date=dt.date.today() - dt.timedelta(days=10))

    by_topic = journal_service.list_journals(topic_id=topic.id)
    assert [j.title for j in by_topic] == ["A"]

    by_mood = journal_service.list_journals(mood="sad")
    assert [j.title for j in by_mood] == ["B"]

    favorites = journal_service.list_journals(favorites_only=True)
    assert [j.title for j in favorites] == ["B"]

    recent_only = journal_service.list_journals(date_from=dt.date.today())
    titles = {j.title for j in recent_only}
    assert "C" not in titles


def test_get_journals_for_date(journal_service):
    today = dt.date.today()
    journal_service.create_journal(title="Today entry", content="x", journal_date=today)
    journal_service.create_journal(title="Old entry", content="y", journal_date=today - dt.timedelta(days=5))
    results = journal_service.get_journals_for_date(today)
    assert len(results) == 1
    assert results[0].title == "Today entry"


def test_current_streak_counts_consecutive_days(journal_service):
    today = dt.date.today()
    for offset in range(3):
        journal_service.create_journal(title=f"Day {offset}", content="x", journal_date=today - dt.timedelta(days=offset))
    assert journal_service.current_streak() == 3


def test_current_streak_zero_when_no_entries(journal_service):
    assert journal_service.current_streak() == 0


def test_current_streak_breaks_on_gap(journal_service):
    today = dt.date.today()
    journal_service.create_journal(title="Today", content="x", journal_date=today)
    journal_service.create_journal(title="Three days ago", content="y", journal_date=today - dt.timedelta(days=3))
    assert journal_service.current_streak() == 1


def test_attach_and_remove_media(journal_service):
    dto = journal_service.create_journal(title="A", content="B")
    assert dto.media == []
    with_media = journal_service.attach_media(dto.id, "/tmp/fake.png")
    assert len(with_media.media) == 1
    assert with_media.media[0].file_path == "/tmp/fake.png"
    without_media = journal_service.remove_media(dto.id, with_media.media[0].id)
    assert without_media.media == []


def test_deleting_topic_unassigns_but_keeps_journal(journal_service, topic_service):
    topic = topic_service.create_topic("Ambitions", "#9C6ADE", "\U0001F3AF")
    dto = journal_service.create_journal(title="Keep me", content="x", topic_id=topic.id)
    topic_service.delete_topic(topic.id)
    reloaded = journal_service.get_journal(dto.id)
    assert reloaded.title == "Keep me"
    assert reloaded.topic is None
