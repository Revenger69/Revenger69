"""The journal preview card -- the single most important visual element
in the app, since browsing journals should feel like flipping through
memories rather than scanning database rows."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.config import MOOD_GLYPHS
from app.services.dto import JournalDTO
from app.ui.effects import apply_card_shadow
from app.utils.date_utils import relative_date_label
from app.utils.icons import icon


class JournalCard(QFrame):
    opened = Signal(int)
    favorite_toggled = Signal(int)

    def __init__(self, journal: JournalDTO, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.journal_id = journal.id
        self.setObjectName("Card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_card_shadow(self, blur=18, y_offset=3, alpha=22)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 16, 18, 16)
        outer.setSpacing(6)

        top_row = QHBoxLayout()
        date_label = QLabel(relative_date_label(journal.journal_date).upper())
        date_label.setObjectName("CardDate")
        top_row.addWidget(date_label)
        top_row.addStretch(1)

        if journal.mood:
            mood_label = QLabel(MOOD_GLYPHS.get(journal.mood, ""))
            top_row.addWidget(mood_label)

        self._fav_button = QPushButton(icon("favorite_on") if journal.is_favorite else icon("favorite_off"))
        self._fav_button.setObjectName("IconButton")
        self._fav_button.setCheckable(True)
        self._fav_button.setChecked(journal.is_favorite)
        self._fav_button.setFixedSize(24, 24)
        self._fav_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._fav_button.clicked.connect(lambda: self.favorite_toggled.emit(self.journal_id))
        top_row.addWidget(self._fav_button)
        outer.addLayout(top_row)

        title_label = QLabel(journal.title or "Untitled")
        title_label.setObjectName("CardTitle")
        title_label.setWordWrap(True)
        outer.addWidget(title_label)

        if journal.preview:
            preview_label = QLabel(f"\u201c{journal.preview}\u201d")
            preview_label.setObjectName("CardPreview")
            preview_label.setWordWrap(True)
            outer.addWidget(preview_label)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(6)
        if journal.topic:
            badge = QLabel(f"{journal.topic.icon} {journal.topic.name}")
            badge.setObjectName("MutedLabel")
            meta_row.addWidget(badge)
        if journal.tags:
            tags_label = QLabel(" ".join(f"#{t}" for t in journal.tags[:4]))
            tags_label.setObjectName("MutedLabel")
            meta_row.addWidget(tags_label)
        meta_row.addStretch(1)
        outer.addLayout(meta_row)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.button() == Qt.MouseButton.LeftButton:
            self.opened.emit(self.journal_id)
        super().mousePressEvent(event)

    def set_favorite(self, is_favorite: bool) -> None:
        self._fav_button.setChecked(is_favorite)
        self._fav_button.setText(icon("favorite_on") if is_favorite else icon("favorite_off"))
