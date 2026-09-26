"""The application's top-level window: sidebar + stacked content pages,
plus a floating toast layer. Owns the wiring between AppContext signals
and page navigation, but delegates all actual page behavior to the page
widgets themselves."""
from __future__ import annotations

import datetime as dt
import logging

from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QWidget

from app.config import APP_TITLE
from app.ui.context import AppContext
from app.ui.styles import ThemeManager, build_stylesheet
from app.ui.widgets.all_journals_view import AllJournalsView
from app.ui.widgets.calendar_view import CalendarView
from app.ui.widgets.dashboard_view import DashboardView
from app.ui.widgets.favorites_view import FavoritesView
from app.ui.widgets.journal_editor import JournalEditor
from app.ui.widgets.search_view import SearchView
from app.ui.widgets.settings_view import SettingsView
from app.ui.widgets.sidebar import Sidebar
from app.ui.widgets.toast import Toast
from app.ui.widgets.topics_view import TopicsView

logger = logging.getLogger(__name__)

# Nav key -> stack index mapping is assigned in the order pages are added.
NAV_ORDER = ["dashboard", "journal", "calendar", "topics", "favorites", "search", "settings"]


class MainWindow(QMainWindow):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self.context = context
        self.setWindowTitle(APP_TITLE)
        self.resize(1180, 780)
        self.setMinimumSize(860, 560)

        self._previous_page_key = "dashboard"
        self._current_page_key = "dashboard"

        central = QWidget()
        central.setObjectName("CentralArea")
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._sidebar = Sidebar()
        root_layout.addWidget(self._sidebar)

        self._stack = QStackedWidget()
        root_layout.addWidget(self._stack, stretch=1)

        self._pages: dict[str, QWidget] = {}
        self._dashboard = DashboardView(context)
        self._journal_list = AllJournalsView(context)
        self._calendar = CalendarView(context)
        self._topics = TopicsView(context)
        self._favorites = FavoritesView(context)
        self._search = SearchView(context)
        self._settings = SettingsView(context)
        self._editor = JournalEditor(context)

        for key, widget in zip(
            NAV_ORDER,
            [self._dashboard, self._journal_list, self._calendar, self._topics, self._favorites, self._search, self._settings],
        ):
            self._stack.addWidget(widget)
            self._pages[key] = widget
        self._stack.addWidget(self._editor)
        self._pages["editor"] = self._editor

        self._toast = Toast(central)

        self._connect_signals()
        self._apply_theme()
        self._show_page("dashboard")

    # ------------------------------------------------------------------ #
    # Signal wiring
    # ------------------------------------------------------------------ #
    def _connect_signals(self) -> None:
        self._sidebar.nav_selected.connect(self._show_page)
        self._sidebar.new_journal_clicked.connect(lambda: self.context.open_editor(None, dt.date.today()))

        self.context.navigate_requested.connect(self._show_page)
        self.context.open_editor_requested.connect(self._open_editor_page)
        self.context.toast_requested.connect(self._toast.show_message)
        self.context.data_changed.connect(self._refresh_current_page)
        self.context.settings_changed.connect(self._apply_theme)
        self.context.search_requested.connect(self._open_search_with_query)

        self._editor.back_requested.connect(self._on_editor_back)

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def _show_page(self, key: str) -> None:
        page = self._pages.get(key)
        if page is None:
            return
        if key != "editor":
            self._previous_page_key = key
        self._current_page_key = key
        self._stack.setCurrentWidget(page)
        self._sidebar.set_active(key)
        self._refresh_page(key)

    def _refresh_page(self, key: str) -> None:
        page = self._pages.get(key)
        if page is not None and hasattr(page, "refresh"):
            page.refresh()
        if key == "dashboard":
            streak = self.context.journal_service.current_streak()
            self._sidebar.set_streak_text(f"\U0001F525 {streak}-day streak" if streak else "")

    def _refresh_current_page(self) -> None:
        self._refresh_page(self._current_page_key)
        # Keep the sidebar streak indicator live regardless of which page
        # triggered the data change.
        streak = self.context.journal_service.current_streak()
        self._sidebar.set_streak_text(f"\U0001F525 {streak}-day streak" if streak else "")

    def _open_editor_page(self, journal_id, prefill_date) -> None:
        if journal_id is not None:
            self._editor.load_journal(journal_id)
        else:
            self._editor.load_new(prefill_date)
        self._current_page_key = "editor"
        self._stack.setCurrentWidget(self._editor)
        self._sidebar.set_active(self._previous_page_key)

    def _on_editor_back(self) -> None:
        self._show_page(self._previous_page_key)

    def _open_search_with_query(self, query: str) -> None:
        self._search.set_query(query)
        self._show_page("search")

    # ------------------------------------------------------------------ #
    # Theming
    # ------------------------------------------------------------------ #
    def _apply_theme(self) -> None:
        theme = ThemeManager.get(self.context.settings.theme)
        app = self._qapp()
        if app is not None:
            app.setStyleSheet(build_stylesheet(theme))
        self._refresh_current_page()

    @staticmethod
    def _qapp():
        from PySide6.QtWidgets import QApplication

        return QApplication.instance()

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        if hasattr(self, "_toast"):
            self._toast.resize(self.centralWidget().size())

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt override
        try:
            self._editor.flush()
        except Exception:  # noqa: BLE001 - never block shutdown on a save error
            logger.exception("Failed to flush editor on close")
        super().closeEvent(event)
