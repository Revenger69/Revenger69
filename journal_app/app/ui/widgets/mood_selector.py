"""A row of tappable mood glyphs. Selection is optional: tapping the
already-selected mood deselects it (mood must never feel mandatory)."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from app.config import MOODS


class MoodSelector(QWidget):
    mood_changed = Signal(object)  # str | None

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._selected: str | None = None
        self._buttons: dict[str, QPushButton] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)

        row = QHBoxLayout()
        row.setSpacing(6)
        for key, label, glyph in MOODS:
            button = QPushButton(glyph, self)
            button.setObjectName("MoodButton")
            button.setCheckable(True)
            button.setFixedSize(36, 36)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setToolTip(label)
            button.clicked.connect(lambda _checked, k=key: self._on_clicked(k))
            row.addWidget(button)
            self._buttons[key] = button
        row.addStretch(1)
        outer.addLayout(row)

    def _on_clicked(self, key: str) -> None:
        if self._selected == key:
            self._selected = None
        else:
            self._selected = key
        self._sync_buttons()
        self.mood_changed.emit(self._selected)

    def _sync_buttons(self) -> None:
        for key, button in self._buttons.items():
            button.setChecked(key == self._selected)

    def set_mood(self, mood: str | None) -> None:
        self._selected = mood
        self._sync_buttons()

    def mood(self) -> str | None:
        return self._selected
