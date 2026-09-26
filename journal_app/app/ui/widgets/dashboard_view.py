"""The Home / Dashboard screen: a calm, uncluttered landing page that
gets the user writing as fast as possible while surfacing recent work."""
from __future__ import annotations

import datetime as dt

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.ui.context import AppContext
from app.ui.effects import apply_card_shadow
from app.ui.widgets.journal_list_view import JournalListView
from app.utils.icons import icon


def _greeting(now: dt.datetime | None = None) -> str:
    hour = (now or dt.datetime.now()).hour
    if hour < 5:
        return "Still up?"
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


class DashboardView(QWidget):
    def __init__(self, context: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.context = context

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)

        host = QWidget()
        scroll.setWidget(host)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        # --- Greeting header ------------------------------------------ #
        self._greeting_label = QLabel()
        self._greeting_label.setObjectName("PageTitle")
        layout.addWidget(self._greeting_label)

        self._date_label = QLabel()
        self._date_label.setObjectName("PageSubtitle")
        layout.addWidget(self._date_label)

        layout.addSpacing(4)
        cta_row = QHBoxLayout()
        self._cta_button = QPushButton()
        self._cta_button.setObjectName("NewJournalButton")
        self._cta_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cta_button.setFixedHeight(46)
        self._cta_button.clicked.connect(lambda: self.context.open_editor(None, dt.date.today()))
        cta_row.addWidget(self._cta_button, stretch=1)

        self._streak_pill = QLabel()
        self._streak_pill.setObjectName("Badge")
        self._streak_pill.setStyleSheet("padding: 10px 14px; font-size: 13px; font-weight: 700;")
        cta_row.addWidget(self._streak_pill)
        layout.addLayout(cta_row)

        # --- Quick search ------------------------------------------- #
        self._search_input = QLineEdit()
        self._search_input.setObjectName("SearchBar")
        self._search_input.setPlaceholderText(f"{icon('search')}  Search your journals\u2026")
        self._search_input.returnPressed.connect(self._on_search_submitted)
        layout.addWidget(self._search_input)

        # --- Recent journals ------------------------------------------ #
        recent_header = QHBoxLayout()
        recent_title = QLabel("Recent Journals")
        recent_title.setObjectName("SectionHeader")
        recent_header.addWidget(recent_title)
        recent_header.addStretch(1)
        see_all = QPushButton("See all \u2192")
        see_all.setObjectName("IconButton")
        see_all.setCursor(Qt.CursorShape.PointingHandCursor)
        see_all.clicked.connect(lambda: self.context.navigate("journal"))
        recent_header.addWidget(see_all)
        layout.addLayout(recent_header)

        self._recent_list = JournalListView()
        self._recent_list.setMinimumHeight(260)
        self._recent_list.journal_opened.connect(lambda jid: self.context.open_editor(jid))
        self._recent_list.favorite_toggled.connect(self._on_favorite_toggled)
        layout.addWidget(self._recent_list)

        # --- Favorites + Topics + Calendar shortcuts (3-up row) ------- #
        shortcuts_row = QGridLayout()
        shortcuts_row.setSpacing(14)

        self._favorites_card = self._make_shortcut_card(
            "\u2B50 Favorites", "Your favorite entries, all in one place.", lambda: self.context.navigate("favorites")
        )
        shortcuts_row.addWidget(self._favorites_card, 0, 0)

        self._topics_card = self._make_shortcut_card(
            "\U0001F3F7 Topics", "Browse by what matters to you.", lambda: self.context.navigate("topics")
        )
        shortcuts_row.addWidget(self._topics_card, 0, 1)

        self._calendar_card = self._make_shortcut_card(
            "\U0001F4C5 Calendar", "See your journal, day by day.", lambda: self.context.navigate("calendar")
        )
        shortcuts_row.addWidget(self._calendar_card, 0, 2)

        layout.addLayout(shortcuts_row)
        layout.addStretch(1)

    def _make_shortcut_card(self, title: str, subtitle: str, on_click) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setMinimumHeight(96)
        apply_card_shadow(card, blur=14, y_offset=2, alpha=18)
        inner = QVBoxLayout(card)
        inner.setContentsMargins(16, 14, 16, 14)
        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")
        inner.addWidget(title_label)
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("MutedLabel")
        subtitle_label.setWordWrap(True)
        inner.addWidget(subtitle_label)

        def _mouse_press(event, cb=on_click):
            if event.button() == Qt.MouseButton.LeftButton:
                cb()

        card.mousePressEvent = _mouse_press
        return card

    def _on_search_submitted(self) -> None:
        self.context.search(self._search_input.text())
        self._search_input.clear()

    def _on_favorite_toggled(self, journal_id: int) -> None:
        self.context.journal_service.toggle_favorite(journal_id)
        self.context.notify_data_changed()

    def refresh(self) -> None:
        now = dt.datetime.now()
        self._greeting_label.setText(_greeting(now))
        self._date_label.setText(now.strftime("%A, %B %-d, %Y"))

        has_any = self.context.journal_service.total_count() > 0
        self._cta_button.setText(
            f"{icon('new')}  Write Today's Journal" if not has_any else f"{icon('new')}  New Journal Entry"
        )

        streak = self.context.journal_service.current_streak()
        self._streak_pill.setText(f"{icon('streak')} {streak}-day streak" if streak else f"{icon('streak')} Start a streak")

        recent = self.context.journal_service.get_recent(limit=5)
        self._recent_list.set_journals(
            recent,
            grouped=False,
            empty_title="No memories yet.",
            empty_subtitle="Start writing your first journal entry.",
            empty_cta="Write Your First Journal",
            on_empty_cta=lambda: self.context.open_editor(None, dt.date.today()),
        )
