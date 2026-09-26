"""Left navigation sidebar: app identity, the prominent 'New Journal'
button, and the primary nav list. Icons are paired with text labels
throughout, never icon-only, for accessibility and clarity."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QLabel, QPushButton, QVBoxLayout, QWidget

from app.config import APP_TITLE, NAV_ITEMS
from app.utils.icons import icon


class Sidebar(QWidget):
    nav_selected = Signal(str)
    new_journal_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(6)

        title = QLabel(APP_TITLE.split("\u2014")[0].strip())
        title.setObjectName("AppTitle")
        layout.addWidget(title)
        subtitle = QLabel("A private journal")
        subtitle.setObjectName("AppSubtitle")
        layout.addWidget(subtitle)

        layout.addSpacing(16)
        new_button = QPushButton(f"{icon('new')}  New Journal")
        new_button.setObjectName("NewJournalButton")
        new_button.setCursor(Qt.CursorShape.PointingHandCursor)
        new_button.clicked.connect(self.new_journal_clicked.emit)
        layout.addWidget(new_button)
        layout.addSpacing(20)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, QPushButton] = {}
        for key, label, glyph in NAV_ITEMS:
            button = QPushButton(f"{glyph}   {label}")
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _c=False, k=key: self.nav_selected.emit(k))
            self._group.addButton(button)
            layout.addWidget(button)
            self._buttons[key] = button

        layout.addStretch(1)

        streak_caption = QLabel("")
        streak_caption.setObjectName("MutedLabel")
        streak_caption.setWordWrap(True)
        self._streak_label = streak_caption
        layout.addWidget(streak_caption)

    def set_active(self, key: str) -> None:
        button = self._buttons.get(key)
        if button is not None:
            button.setChecked(True)

    def set_streak_text(self, text: str) -> None:
        self._streak_label.setText(text)
