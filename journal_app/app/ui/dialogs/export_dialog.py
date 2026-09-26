"""Choose an export format before the caller opens a native "Save As"
file dialog. Kept separate from file-picking so it stays simple and
testable without touching the filesystem."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)


class ExportDialog(QDialog):
    FORMATS = [
        ("json", "JSON", "Structured data, ideal for backups or importing elsewhere."),
        ("markdown", "Markdown", "Readable, portable text with light formatting."),
        ("txt", "Plain Text", "Simple text file, readable anywhere."),
        ("pdf", "PDF", "A polished, printable document."),
    ]

    def __init__(self, parent=None, pdf_available: bool = True) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export Journals")
        self.setModal(True)
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Choose a format"))

        self._group = QButtonGroup(self)
        for i, (key, label, description) in enumerate(self.FORMATS):
            row = QHBoxLayout()
            radio = QRadioButton(label)
            radio.setProperty("format_key", key)
            if key == "json":
                radio.setChecked(True)
            if key == "pdf" and not pdf_available:
                radio.setEnabled(False)
            self._group.addButton(radio, i)
            row.addWidget(radio)
            row.addStretch(1)
            layout.addLayout(row)
            desc_label = QLabel(description)
            desc_label.setObjectName("MutedLabel")
            layout.addWidget(desc_label)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("SecondaryButton")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)
        export_button = QPushButton("Continue")
        export_button.setObjectName("PrimaryButton")
        export_button.setDefault(True)
        export_button.clicked.connect(self.accept)
        button_row.addWidget(export_button)
        layout.addSpacing(6)
        layout.addLayout(button_row)

    def selected_format(self) -> str:
        button = self._group.checkedButton()
        return button.property("format_key") if button else "json"
