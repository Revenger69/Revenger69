"""Tests for SearchService: text search + combined filters."""
from __future__ import annotations

import datetime as dt

from app.services.search_service import SearchFilters


def test_search_matches_title_content_topic_and_tags(journal_service, topic_service, search_service):
    topic = topic_service.create_topic("Wanderlust", "#4F9D9D", "\u2708")
    journal_service.create_journal(
        title="A Quiet Evening", content="Thinking about the mountains of Nepal.",
        topic_id=topic.id, tags=["nepal", "memories"],
    )
    journal_service.create_journal(title="Busy Day", content="Work was hectic.")

    by_content = search_service.search(SearchFilters(query="mountains"))
    assert [j.title for j in by_content] == ["A Quiet Evening"]

    by_tag = search_service.search(SearchFilters(query="nepal"))
    assert [j.title for j in by_tag] == ["A Quiet Evening"]

    by_topic_name = search_service.search(SearchFilters(query="wanderlust"))
    assert [j.title for j in by_topic_name] == ["A Quiet Evening"]

    no_match = search_service.search(SearchFilters(query="nonexistentword"))
    assert no_match == []


def test_search_combines_query_and_filters(journal_service, topic_service, search_service):
    travel = topic_service.create_topic("Wanderlust", "#4F9D9D", "\u2708")
    work = topic_service.create_topic("Career", "#6E8AA6", "\U0001F4BC")
    journal_service.create_journal(title="Trip notes", content="mountains and lakes", topic_id=travel.id)
    journal_service.create_journal(title="Meeting notes", content="mountains of paperwork", topic_id=work.id)

    results = search_service.search(SearchFilters(query="mountains", topic_id=travel.id))
    assert [j.title for j in results] == ["Trip notes"]


def test_search_with_no_query_applies_filters_only(journal_service, search_service):
    journal_service.create_journal(title="Fav one", content="x", is_favorite=True)
    journal_service.create_journal(title="Not fav", content="y", is_favorite=False)
    results = search_service.search(SearchFilters(favorites_only=True))
    assert [j.title for j in results] == ["Fav one"]


def test_search_date_range(journal_service, search_service):
    today = dt.date.today()
    journal_service.create_journal(title="Recent", content="x", journal_date=today)
    journal_service.create_journal(title="Old", content="y", journal_date=today - dt.timedelta(days=30))
    results = search_service.search(SearchFilters(date_from=today - dt.timedelta(days=5)))
    assert [j.title for j in results] == ["Recent"]
