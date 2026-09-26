"""A tag input: type a word and press Enter/Comma/Space to turn it into a
removable chip. Supports '#travel #nepal' style typing."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QCompleter,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.tag_service import normalize_tag
from app.ui.layout_utils import clear_layout


class _FlowRow(QWidget):
    """Simple wrapping row of chips using a plain QHBoxLayout; the editor
    context keeps tag counts small so a flow-layout implementation would
    be over-engineering here."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout_ = QHBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.setSpacing(6)
        self.layout_.addStretch(1)

    def add_widget(self, widget: QWidget) -> None:
        self.layout_.insertWidget(self.layout_.count() - 1, widget)

    def clear(self) -> None:
        clear_layout(self.layout_, keep_last=1)


class _TagChip(QWidget):
    remove_requested = Signal()

    def __init__(self, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("TagChip")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 3, 6, 3)
        layout.setSpacing(4)
        label = QLabel(f"#{name}")
        label.setObjectName("TagChipLabel")
        layout.addWidget(label)
        remove_btn = QPushButton("\u2715")
        remove_btn.setObjectName("IconButton")
        remove_btn.setFixedSize(16, 16)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.clicked.connect(self._emit_remove)
        layout.addWidget(remove_btn)
        self._remove_signal_target: TagSelector | None = None

    def _emit_remove(self) -> None:
        self.setParent(None)
        self.deleteLater()


class TagSelector(QWidget):
    tags_changed = Signal(list)

    def __init__(self, parent: QWidget | None = None, suggestions: list[str] | None = None) -> None:
        super().__init__(parent)
        self._tags: list[str] = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        self._chip_row = _FlowRow(self)
        outer.addWidget(self._chip_row)

        self._input = QLineEdit(self)
        self._input.setPlaceholderText("Add tags\u2026 (press Enter)")
        if suggestions:
            self.set_suggestions(suggestions)
        self._input.installEventFilter(self)
        outer.addWidget(self._input)

    def set_suggestions(self, names: list[str]) -> None:
        completer = QCompleter(names, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._input.setCompleter(completer)

    def eventFilter(self, obj, event):  # noqa: N802 - Qt override
        if obj is self._input and event.type() == QKeyEvent.Type.KeyPress:
            key = event.key()
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Comma):
                self._commit_input()
                return True
        return super().eventFilter(obj, event)

    def _commit_input(self) -> None:
        text = self._input.text()
        name = normalize_tag(text)
        self._input.clear()
        if name and name not in self._tags:
            self._add_tag(name)
            self.tags_changed.emit(list(self._tags))

    def _add_tag(self, name: str) -> None:
        self._tags.append(name)
        chip = _TagChip(name, self._chip_row)
        chip_button = chip.findChild(QPushButton)
        chip_button.clicked.connect(lambda: self._remove_tag(name, chip))
        self._chip_row.add_widget(chip)

    def _remove_tag(self, name: str, chip: QWidget) -> None:
        if name in self._tags:
            self._tags.remove(name)
        chip.setParent(None)
        chip.deleteLater()
        self.tags_changed.emit(list(self._tags))

    def set_tags(self, tags: list[str]) -> None:
        self._chip_row.clear()
        self._tags = []
        for name in tags:
            normalized = normalize_tag(name)
            if normalized:
                self._add_tag(normalized)

    def tags(self) -> list[str]:
        return list(self._tags)
