"""AppContext wires together the database, every service, current
settings, and a small set of cross-cutting Qt signals that let far-apart
widgets talk to each other (e.g. "a journal changed, please refresh"),
without every view needing a reference to every other view.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal

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
from app.services.settings_service import AppSettings


class AppContext(QObject):
    # Emitted whenever a journal or topic is created/edited/deleted, so
    # any visible list/dashboard/calendar can refresh itself.
    data_changed = Signal()
    # Ask the main window to switch the main content page.
    navigate_requested = Signal(str)
    # Ask the main window to open the editor for a given journal id, or
    # None to start a brand-new entry (optionally pre-filled with a date).
    open_editor_requested = Signal(object, object)  # journal_id, prefill_date
    # Ask the main window to show a brief toast notification.
    toast_requested = Signal(str)
    # Emitted after settings (theme, fonts, etc.) change, so the app can
    # rebuild its stylesheet / propagate font changes live.
    settings_changed = Signal()
    # Ask the main window to switch to Search with a pre-filled query.
    search_requested = Signal(str)

    def __init__(self, paths: AppPaths | None = None) -> None:
        super().__init__()
        self.paths = paths or AppPaths()
        self.db = Database(self.paths)
        self.db.init_db()

        self.journal_service = JournalService(self.db)
        self.topic_service = TopicService(self.db)
        self.tag_service = TagService(self.db)
        self.search_service = SearchService(self.db)
        self.export_service = ExportService()
        self.settings_service = SettingsService(self.paths)

        self.settings: AppSettings = self.settings_service.load()

    def update_settings(self, **kwargs) -> None:
        self.settings = self.settings_service.update(**kwargs)
        self.settings_changed.emit()

    def notify_data_changed(self) -> None:
        self.data_changed.emit()

    def toast(self, message: str) -> None:
        self.toast_requested.emit(message)

    def open_editor(self, journal_id: int | None = None, prefill_date=None) -> None:
        self.open_editor_requested.emit(journal_id, prefill_date)

    def navigate(self, view_key: str) -> None:
        self.navigate_requested.emit(view_key)

    def search(self, query: str) -> None:
        self.search_requested.emit(query)
