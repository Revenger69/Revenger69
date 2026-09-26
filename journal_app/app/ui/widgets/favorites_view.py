"""Favorites screen: every entry the user has starred, grouped by date."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.ui.context import AppContext
from app.ui.widgets.journal_list_view import JournalListView


class FavoritesView(QWidget):
    def __init__(self, context: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.context = context

        outer = QVBoxLayout(self)
        outer.setContentsMargins(36, 28, 36, 28)
        outer.setSpacing(14)

        title = QLabel("Favorites")
        title.setObjectName("PageTitle")
        outer.addWidget(title)
        subtitle = QLabel("The entries you've marked as important.")
        subtitle.setObjectName("PageSubtitle")
        outer.addWidget(subtitle)

        self._list = JournalListView()
        self._list.journal_opened.connect(lambda jid: self.context.open_editor(jid))
        self._list.favorite_toggled.connect(self._on_favorite_toggled)
        outer.addWidget(self._list, stretch=1)

    def _on_favorite_toggled(self, journal_id: int) -> None:
        self.context.journal_service.toggle_favorite(journal_id)
        self.context.notify_data_changed()

    def refresh(self) -> None:
        favorites = self.context.journal_service.list_journals(favorites_only=True)
        self._list.set_journals(
            favorites,
            empty_icon="\u2B50",
            empty_title="No favorites yet.",
            empty_subtitle="Tap the star on any entry to save it here.",
        )
