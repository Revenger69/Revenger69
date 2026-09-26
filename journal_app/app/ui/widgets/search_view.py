"""Search screen: fast local search across title, content, topics, and
tags, with filters for date, topic, mood, and favorites."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.config import MOODS
from app.services.search_service import SearchFilters
from app.ui.context import AppContext
from app.ui.widgets.journal_list_view import JournalListView
from app.utils.icons import icon


class SearchView(QWidget):
    def __init__(self, context: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.context = context

        outer = QVBoxLayout(self)
        outer.setContentsMargins(36, 28, 36, 28)
        outer.setSpacing(14)

        title = QLabel("Search")
        title.setObjectName("PageTitle")
        outer.addWidget(title)

        self._search_input = QLineEdit()
        self._search_input.setObjectName("SearchBar")
        self._search_input.setPlaceholderText(f"{icon('search')}  Search title, content, topics, tags\u2026")
        self._search_input.textChanged.connect(self._run_search)
        outer.addWidget(self._search_input)

        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self._topic_combo = QComboBox()
        self._topic_combo.currentIndexChanged.connect(self._run_search)
        filters_row.addWidget(self._topic_combo)

        self._mood_combo = QComboBox()
        self._mood_combo.addItem("Any mood", None)
        for key, label, glyph in MOODS:
            self._mood_combo.addItem(f"{glyph} {label}", key)
        self._mood_combo.currentIndexChanged.connect(self._run_search)
        filters_row.addWidget(self._mood_combo)

        self._favorites_check = QCheckBox("Favorites only")
        self._favorites_check.stateChanged.connect(self._run_search)
        filters_row.addWidget(self._favorites_check)

        filters_row.addStretch(1)
        clear_button = QPushButton("Clear filters")
        clear_button.setObjectName("SecondaryButton")
        clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_button.clicked.connect(self._clear_filters)
        filters_row.addWidget(clear_button)
        outer.addLayout(filters_row)

        self._results_list = JournalListView()
        self._results_list.journal_opened.connect(lambda jid: self.context.open_editor(jid))
        self._results_list.favorite_toggled.connect(self._on_favorite_toggled)
        outer.addWidget(self._results_list, stretch=1)

    def _refresh_topic_combo(self) -> None:
        current = self._topic_combo.currentData()
        self._topic_combo.blockSignals(True)
        self._topic_combo.clear()
        self._topic_combo.addItem("Any topic", None)
        for topic in self.context.topic_service.list_topics():
            self._topic_combo.addItem(f"{topic.icon} {topic.name}", topic.id)
        index = self._topic_combo.findData(current)
        self._topic_combo.setCurrentIndex(index if index >= 0 else 0)
        self._topic_combo.blockSignals(False)

    def _clear_filters(self) -> None:
        self._search_input.clear()
        self._topic_combo.setCurrentIndex(0)
        self._mood_combo.setCurrentIndex(0)
        self._favorites_check.setChecked(False)
        self._run_search()

    def _on_favorite_toggled(self, journal_id: int) -> None:
        self.context.journal_service.toggle_favorite(journal_id)
        self.context.notify_data_changed()

    def _run_search(self, *_args) -> None:
        filters = SearchFilters(
            query=self._search_input.text(),
            topic_id=self._topic_combo.currentData(),
            mood=self._mood_combo.currentData(),
            favorites_only=self._favorites_check.isChecked(),
        )
        results = self.context.search_service.search(filters)
        has_active_query = bool(
            filters.query.strip() or filters.topic_id or filters.mood or filters.favorites_only
        )
        self._results_list.set_journals(
            results,
            grouped=True,
            empty_icon="\U0001F50D",
            empty_title="No journal entries found." if has_active_query else "Search your journals",
            empty_subtitle=(
                "Try another keyword or filter." if has_active_query
                else "Start typing to search titles, content, topics, and tags."
            ),
        )

    def set_query(self, query: str) -> None:
        self._search_input.setText(query)

    def refresh(self) -> None:
        self._refresh_topic_combo()
        self._run_search()
