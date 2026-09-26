"""The 'Journal' nav item: every entry, grouped by date (Today,
Yesterday, This Week, ...), newest first."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.ui.context import AppContext
from app.ui.widgets.journal_list_view import JournalListView


class AllJournalsView(QWidget):
    def __init__(self, context: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.context = context

        outer = QVBoxLayout(self)
        outer.setContentsMargins(36, 28, 36, 28)
        outer.setSpacing(14)

        title = QLabel("Journal")
        title.setObjectName("PageTitle")
        outer.addWidget(title)
        subtitle = QLabel("Every entry you've written, in one place.")
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
        journals = self.context.journal_service.list_journals()
        self._list.set_journals(
            journals,
            empty_title="No memories yet.",
            empty_subtitle="Start writing your first journal entry.",
            empty_cta="Write Your First Journal",
            on_empty_cta=lambda: self.context.open_editor(None),
        )
