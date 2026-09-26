"""Shared pytest fixtures: every test gets its own isolated data
directory and a fresh Database/service instances, so tests never share
state or touch the real user data directory."""
from __future__ import annotations

import pytest

from app.config import AppPaths
from app.database import Database
from app.services import (
    ExportService,
    JournalService,
    SearchService,
    SettingsService,
    TagService,
    TopicService,
)


@pytest.fixture
def paths(tmp_path):
    return AppPaths(root_override=tmp_path / "journal_data")


@pytest.fixture
def db(paths):
    database = Database(paths)
    database.init_db()
    return database


@pytest.fixture
def journal_service(db):
    return JournalService(db)


@pytest.fixture
def topic_service(db):
    return TopicService(db)


@pytest.fixture
def tag_service(db):
    return TagService(db)


@pytest.fixture
def search_service(db):
    return SearchService(db)


@pytest.fixture
def export_service():
    return ExportService()


@pytest.fixture
def settings_service(paths):
    return SettingsService(paths)
