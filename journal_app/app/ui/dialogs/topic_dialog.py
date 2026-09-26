"""Create/edit a topic: name, color swatch picker (+ custom color), and
icon picker from a curated glyph set."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

SWATCHES = [
    "#8A9A5B", "#6E8AA6", "#C97B63", "#4F9D9D",
    "#B08968", "#9C6ADE", "#D68C8C", "#C9A227",
    "#7A9B6E", "#A65D57", "#5C7A99", "#B58900",
]

ICON_CHOICES = [
    "\U0001F4C1", "\U0001F331", "\U0001F4BC", "\U0001F3E1", "\u2708", "\U0001F4A1",
    "\U0001F3AF", "\U0001F4F7", "\U0001F64F", "\U0001F4DA", "\U0001F3A8", "\U0001F3C3",
    "\U0001F3B5", "\U0001F373", "\U0001F455", "\U0001F4B0", "\U0001F33F", "\u2764",
]


class _SwatchButton(QPushButton):
    def __init__(self, color: str) -> None:
        super().__init__()
        self.color = color
        self.setFixedSize(28, 28)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"QPushButton {{ background: {color}; border-radius: 14px; border: 2px solid transparent; }}"
            f"QPushButton:checked {{ border: 2px solid #2E2A24; }}"
        )


class TopicDialog(QDialog):
    def __init__(self, parent=None, name: str = "", color: str = SWATCHES[0], icon: str = ICON_CHOICES[0]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Topic")
        self.setModal(True)
        self.setMinimumWidth(360)
        self._color = color
        self._icon = icon

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Name"))
        self._name_input = QLineEdit(name)
        self._name_input.setPlaceholderText("e.g. Travel")
        layout.addWidget(self._name_input)

        layout.addWidget(QLabel("Color"))
        swatch_grid = QGridLayout()
        swatch_grid.setSpacing(8)
        self._swatch_buttons: list[_SwatchButton] = []
        for i, hex_color in enumerate(SWATCHES):
            button = _SwatchButton(hex_color)
            button.setChecked(hex_color.lower() == color.lower())
            button.clicked.connect(lambda _c=False, b=button: self._select_color(b))
            swatch_grid.addWidget(button, i // 6, i % 6)
            self._swatch_buttons.append(button)
        custom_button = QPushButton("+")
        custom_button.setFixedSize(28, 28)
        custom_button.setCursor(Qt.CursorShape.PointingHandCursor)
        custom_button.clicked.connect(self._pick_custom_color)
        swatch_grid.addWidget(custom_button, len(SWATCHES) // 6, len(SWATCHES) % 6)
        layout.addLayout(swatch_grid)

        layout.addWidget(QLabel("Icon"))
        icon_grid = QGridLayout()
        icon_grid.setSpacing(6)
        self._icon_buttons: list[QPushButton] = []
        for i, glyph in enumerate(ICON_CHOICES):
            button = QPushButton(glyph)
            button.setObjectName("MoodButton")
            button.setCheckable(True)
            button.setChecked(glyph == icon)
            button.setFixedSize(32, 32)
            button.clicked.connect(lambda _c=False, g=glyph, b=button: self._select_icon(g, b))
            icon_grid.addWidget(button, i // 6, i % 6)
            self._icon_buttons.append(button)
        layout.addLayout(icon_grid)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("SecondaryButton")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)
        save_button = QPushButton("Save")
        save_button.setObjectName("PrimaryButton")
        save_button.setDefault(True)
        save_button.clicked.connect(self._on_save)
        button_row.addWidget(save_button)
        layout.addSpacing(6)
        layout.addLayout(button_row)

    def _select_color(self, chosen: _SwatchButton) -> None:
        for button in self._swatch_buttons:
            button.setChecked(button is chosen)
        self._color = chosen.color

    def _pick_custom_color(self) -> None:
        color = QColorDialog.getColor()
        if color.isValid():
            for button in self._swatch_buttons:
                button.setChecked(False)
            self._color = color.name()

    def _select_icon(self, glyph: str, chosen: QPushButton) -> None:
        for button in self._icon_buttons:
            button.setChecked(button is chosen)
        self._icon = glyph

    def _on_save(self) -> None:
        if not self._name_input.text().strip():
            self._name_input.setFocus()
            return
        self.accept()

    def result_values(self) -> tuple[str, str, str]:
        return self._name_input.text().strip(), self._color, self._icon
