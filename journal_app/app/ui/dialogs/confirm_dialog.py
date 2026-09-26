"""A calm, consistent confirmation dialog for destructive actions (delete
journal, delete topic). Deliberately not the default OS-styled QMessageBox
so it matches the app's visual language."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class ConfirmDialog(QDialog):
    def __init__(
        self,
        title: str,
        message: str,
        confirm_label: str = "Delete",
        danger: bool = True,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")
        title_label.setStyleSheet("font-size: 17px;")
        layout.addWidget(title_label)

        message_label = QLabel(message)
        message_label.setObjectName("PageSubtitle")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        layout.addSpacing(8)
        button_row = QHBoxLayout()
        button_row.addStretch(1)
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("SecondaryButton")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)

        confirm_button = QPushButton(confirm_label)
        confirm_button.setObjectName("DangerButton" if danger else "PrimaryButton")
        confirm_button.clicked.connect(self.accept)
        confirm_button.setDefault(True)
        button_row.addWidget(confirm_button)
        layout.addLayout(button_row)

    @staticmethod
    def confirm(parent, title: str, message: str, confirm_label: str = "Delete", danger: bool = True) -> bool:
        dialog = ConfirmDialog(title, message, confirm_label, danger, parent)
        return dialog.exec() == QDialog.DialogCode.Accepted
