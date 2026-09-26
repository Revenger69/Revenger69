"""Tests for TagService: normalization, parsing, get-or-create dedup."""
from __future__ import annotations

from app.services.tag_service import normalize_tag


def test_normalize_tag_strips_hash_and_lowercases():
    assert normalize_tag("#Nepal") == "nepal"
    assert normalize_tag("  travel  ") == "travel"
    assert normalize_tag("##Memories") == "memories"


def test_parse_tag_input_splits_on_space_and_comma(tag_service):
    result = tag_service.parse_tag_input("#travel #nepal, memories")
    assert result == ["travel", "nepal", "memories"]


def test_get_or_create_many_deduplicates_across_case(tag_service, db):
    with db.session() as session:
        tags = tag_service.get_or_create_many(session, ["Nepal", "#nepal", "  NEPAL  "])
        session.commit()
        assert len(tags) == 1
        assert tags[0].name == "nepal"


def test_get_or_create_many_reuses_existing_tags(tag_service, db):
    with db.session() as session:
        first = tag_service.get_or_create_many(session, ["travel"])
        session.commit()
        first_id = first[0].id

    with db.session() as session:
        second = tag_service.get_or_create_many(session, ["travel", "new-tag"])
        session.commit()
        ids = {t.id for t in second}
        assert first_id in ids
        assert len(second) == 2


def test_list_all_tags_sorted(tag_service, db):
    with db.session() as session:
        tag_service.get_or_create_many(session, ["zebra", "apple"])
        session.commit()
    names = [t.name for t in tag_service.list_all_tags()]
    assert names == sorted(names)
