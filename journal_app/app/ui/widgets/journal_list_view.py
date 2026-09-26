"""A reusable, date-grouped journal list. Used for the "Journal" nav item
(all entries), the Favorites view, and Search results -- each just feeds
it a different list of JournalDTOs."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from app.services.dto import JournalDTO
from app.ui.layout_utils import clear_layout
from app.ui.widgets.empty_state import EmptyState
from app.ui.widgets.journal_card import JournalCard
from app.utils.date_utils import group_key, sort_group_keys


class JournalListView(QWidget):
    journal_opened = Signal(int)
    favorite_toggled = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        outer.addWidget(self._scroll)

        self._host = QWidget()
        self._host_layout = QVBoxLayout(self._host)
        self._host_layout.setContentsMargins(2, 2, 2, 2)
        self._host_layout.setSpacing(10)
        self._scroll.setWidget(self._host)

    def set_journals(
        self,
        journals: list[JournalDTO],
        *,
        grouped: bool = True,
        empty_icon: str = "\U0001F4DD",
        empty_title: str = "No memories yet.",
        empty_subtitle: str = "Start writing your first journal entry.",
        empty_cta: str | None = None,
        on_empty_cta=None,
    ) -> None:
        self._clear()
        if not journals:
            self._host_layout.addWidget(
                EmptyState(empty_icon, empty_title, empty_subtitle, empty_cta, on_empty_cta)
            )
            return

        if not grouped:
            for journal in journals:
                self._host_layout.addWidget(self._make_card(journal))
            self._host_layout.addStretch(1)
            return

        buckets: dict[str, list[JournalDTO]] = {}
        for journal in journals:
            key = group_key(journal.journal_date)
            buckets.setdefault(key, []).append(journal)

        for key in sort_group_keys(list(buckets.keys())):
            header = QLabel(key.upper())
            header.setObjectName("SectionHeader")
            self._host_layout.addWidget(header)
            for journal in buckets[key]:
                self._host_layout.addWidget(self._make_card(journal))
        self._host_layout.addStretch(1)

    def _make_card(self, journal: JournalDTO) -> JournalCard:
        card = JournalCard(journal)
        card.opened.connect(self.journal_opened.emit)
        card.favorite_toggled.connect(self.favorite_toggled.emit)
        return card

    def _clear(self) -> None:
        clear_layout(self._host_layout)
