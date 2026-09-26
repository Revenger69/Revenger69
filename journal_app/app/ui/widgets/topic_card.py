"""A colored topic tile shown in the Topics view and as a filter chip
elsewhere. Clicking opens/filters by the topic; an overflow menu offers
rename/recolor/delete."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMenu, QPushButton, QVBoxLayout, QWidget

from app.services.dto import TopicDTO
from app.ui.effects import apply_card_shadow


class TopicCard(QFrame):
    opened = Signal(int)
    rename_requested = Signal(int)
    delete_requested = Signal(int)
    recolor_requested = Signal(int)

    def __init__(self, topic: TopicDTO, journal_count: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.topic_id = topic.id
        self.setObjectName("Card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(120)
        apply_card_shadow(self, blur=16, y_offset=3, alpha=20)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 16, 14, 14)
        outer.setSpacing(8)

        top_row = QHBoxLayout()
        swatch = QLabel()
        swatch.setFixedSize(14, 14)
        swatch.setStyleSheet(f"background: {topic.color}; border-radius: 7px;")
        top_row.addWidget(swatch)
        top_row.addStretch(1)

        menu_button = QPushButton("\u22EF")
        menu_button.setObjectName("IconButton")
        menu_button.setFixedSize(24, 24)
        menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        menu_button.clicked.connect(self._show_menu)
        self._menu_button = menu_button
        top_row.addWidget(menu_button)
        outer.addLayout(top_row)

        icon_title_row = QHBoxLayout()
        icon_label = QLabel(topic.icon)
        icon_label.setStyleSheet("font-size: 22px;")
        icon_title_row.addWidget(icon_label)
        title_label = QLabel(topic.name)
        title_label.setObjectName("CardTitle")
        icon_title_row.addWidget(title_label)
        icon_title_row.addStretch(1)
        outer.addLayout(icon_title_row)

        count_label = QLabel(f"{journal_count} {'entry' if journal_count == 1 else 'entries'}")
        count_label.setObjectName("MutedLabel")
        outer.addWidget(count_label)
        outer.addStretch(1)

    def _show_menu(self) -> None:
        menu = QMenu(self)
        rename_action = menu.addAction("Rename")
        recolor_action = menu.addAction("Change color")
        menu.addSeparator()
        delete_action = menu.addAction("Delete topic")
        chosen = menu.exec(self._menu_button.mapToGlobal(self._menu_button.rect().bottomLeft()))
        if chosen == rename_action:
            self.rename_requested.emit(self.topic_id)
        elif chosen == recolor_action:
            self.recolor_requested.emit(self.topic_id)
        elif chosen == delete_action:
            self.delete_requested.emit(self.topic_id)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.button() == Qt.MouseButton.LeftButton:
            self.opened.emit(self.topic_id)
        super().mousePressEvent(event)
