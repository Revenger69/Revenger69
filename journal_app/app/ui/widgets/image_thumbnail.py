"""A small removable image thumbnail used in the journal editor's
optional-photo area."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class ImageThumbnail(QFrame):
    remove_requested = Signal()

    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.setFixedSize(140, 140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(file_path)
        if not pixmap.isNull() and Path(file_path).exists():
            pixmap = pixmap.scaled(
                124, 108, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation
            )
            image_label.setPixmap(pixmap)
        else:
            image_label.setText("\U0001F5BC")
            image_label.setStyleSheet("font-size: 28px;")
        layout.addWidget(image_label)

        remove_row = QHBoxLayout()
        remove_row.addStretch(1)
        remove_button = QPushButton("\u2715")
        remove_button.setObjectName("IconButton")
        remove_button.setFixedSize(20, 20)
        remove_button.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_button.clicked.connect(self.remove_requested.emit)
        remove_row.addWidget(remove_button)
        layout.addLayout(remove_row)
