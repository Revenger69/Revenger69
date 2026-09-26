"""A reusable "nothing here yet" placeholder with an icon, message, and
optional call-to-action button, used by empty journal lists, empty
search results, empty favorites, etc. Keeps every empty screen from
feeling like a dead end."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class EmptyState(QWidget):
    def __init__(
        self,
        icon: str,
        title: str,
        subtitle: str,
        cta_label: str | None = None,
        on_cta: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)
        layout.setContentsMargins(40, 60, 40, 60)

        icon_label = QLabel(icon)
        icon_label.setObjectName("EmptyStateIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setObjectName("EmptyStateTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("EmptyStateSubtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)

        if cta_label:
            layout.addSpacing(10)
            button = QPushButton(cta_label)
            button.setObjectName("PrimaryButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            if on_cta:
                button.clicked.connect(on_cta)
            button_row = QVBoxLayout()
            button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button_row.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addLayout(button_row)
