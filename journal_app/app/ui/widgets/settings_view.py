"""Settings screen: appearance, typography, defaults, reminders, backup/
export, database info, and privacy notes."""
from __future__ import annotations

from PySide6.QtCore import QTime, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from app.ui.context import AppContext
from app.ui.dialogs.export_dialog import ExportDialog
from app.utils.icons import icon


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


class _Section(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(20, 18, 20, 18)
        self.layout_.setSpacing(10)
        header = QLabel(title)
        header.setObjectName("SectionHeader")
        self.layout_.addWidget(header)

    def add(self, widget_or_layout) -> None:
        if isinstance(widget_or_layout, QWidget):
            self.layout_.addWidget(widget_or_layout)
        else:
            self.layout_.addLayout(widget_or_layout)


class SettingsView(QWidget):
    def __init__(self, context: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.context = context

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)

        host = QWidget()
        scroll.setWidget(host)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(36, 28, 36, 40)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        layout.addWidget(self._build_appearance_section())
        layout.addWidget(self._build_typography_section())
        layout.addWidget(self._build_defaults_section())
        layout.addWidget(self._build_reminder_section())
        layout.addWidget(self._build_backup_section())
        layout.addWidget(self._build_database_section())
        layout.addWidget(self._build_privacy_section())
        layout.addStretch(1)

    # ------------------------------------------------------------------ #
    # Appearance
    # ------------------------------------------------------------------ #
    def _build_appearance_section(self) -> QFrame:
        section = _Section("Appearance")
        row = QHBoxLayout()
        self._theme_group = QButtonGroup(self)
        self._light_radio = QRadioButton(f"{icon('sun')}  Light -- warm paper")
        self._dark_radio = QRadioButton(f"{icon('moon')}  Dark -- true dark")
        self._theme_group.addButton(self._light_radio)
        self._theme_group.addButton(self._dark_radio)
        self._light_radio.toggled.connect(self._on_theme_changed)
        row.addWidget(self._light_radio)
        row.addWidget(self._dark_radio)
        row.addStretch(1)
        section.add(row)
        return section

    def _on_theme_changed(self) -> None:
        theme = "light" if self._light_radio.isChecked() else "dark"
        if theme != self.context.settings.theme:
            self.context.update_settings(theme=theme)

    # ------------------------------------------------------------------ #
    # Typography
    # ------------------------------------------------------------------ #
    def _build_typography_section(self) -> QFrame:
        section = _Section("Typography")

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Journal font size"))
        self._font_size_slider = QSlider(Qt.Orientation.Horizontal)
        self._font_size_slider.setRange(12, 28)
        self._font_size_slider.valueChanged.connect(self._on_font_size_changed)
        size_row.addWidget(self._font_size_slider, stretch=1)
        self._font_size_label = QLabel()
        self._font_size_label.setObjectName("MutedLabel")
        size_row.addWidget(self._font_size_label)
        section.add(size_row)

        spacing_row = QHBoxLayout()
        spacing_row.addWidget(QLabel("Line spacing"))
        self._line_spacing_slider = QSlider(Qt.Orientation.Horizontal)
        self._line_spacing_slider.setRange(10, 22)  # represents 1.0x - 2.2x
        self._line_spacing_slider.valueChanged.connect(self._on_line_spacing_changed)
        spacing_row.addWidget(self._line_spacing_slider, stretch=1)
        self._line_spacing_label = QLabel()
        self._line_spacing_label.setObjectName("MutedLabel")
        spacing_row.addWidget(self._line_spacing_label)
        section.add(spacing_row)

        from app.ui.styles.fonts import FontResolver

        font_note = QLabel(
            f"Using \u201c{FontResolver.ui_family()}\u201d for the interface and "
            f"\u201c{FontResolver.serif_family()}\u201d for your journal entries, "
            f"the best-matching fonts available on this device."
        )
        font_note.setObjectName("MutedLabel")
        font_note.setWordWrap(True)
        section.add(font_note)
        return section

    def _on_font_size_changed(self, value: int) -> None:
        self._font_size_label.setText(f"{value}px")
        if value != self.context.settings.journal_font_size:
            self.context.update_settings(journal_font_size=value)

    def _on_line_spacing_changed(self, value: int) -> None:
        spacing = value / 10
        self._line_spacing_label.setText(f"{spacing:.1f}\u00d7")
        if abs(spacing - self.context.settings.line_spacing) > 1e-6:
            self.context.update_settings(line_spacing=spacing)

    # ------------------------------------------------------------------ #
    # Defaults
    # ------------------------------------------------------------------ #
    def _build_defaults_section(self) -> QFrame:
        section = _Section("Defaults")
        row = QHBoxLayout()
        row.addWidget(QLabel("Default topic for new entries"))
        self._default_topic_combo = QComboBox()
        self._default_topic_combo.currentIndexChanged.connect(self._on_default_topic_changed)
        row.addWidget(self._default_topic_combo, stretch=1)
        section.add(row)
        return section

    def _on_default_topic_changed(self, _index: int) -> None:
        topic_id = self._default_topic_combo.currentData()
        if topic_id != self.context.settings.default_topic_id:
            self.context.update_settings(default_topic_id=topic_id)

    # ------------------------------------------------------------------ #
    # Reminders
    # ------------------------------------------------------------------ #
    def _build_reminder_section(self) -> QFrame:
        section = _Section("Daily Reminder")
        row = QHBoxLayout()
        self._reminder_check = QCheckBox("Remind me to write")
        self._reminder_check.stateChanged.connect(self._on_reminder_toggled)
        row.addWidget(self._reminder_check)
        self._reminder_time = QTimeEdit()
        self._reminder_time.setDisplayFormat("h:mm AP")
        self._reminder_time.timeChanged.connect(self._on_reminder_time_changed)
        row.addWidget(self._reminder_time)
        row.addStretch(1)
        section.add(row)
        note = QLabel("A gentle nudge, shown only while the app is open.")
        note.setObjectName("MutedLabel")
        section.add(note)
        return section

    def _on_reminder_toggled(self, _state: int) -> None:
        self.context.update_settings(reminder_enabled=self._reminder_check.isChecked())

    def _on_reminder_time_changed(self, time: QTime) -> None:
        self.context.update_settings(reminder_time=time.toString("HH:mm"))

    # ------------------------------------------------------------------ #
    # Backup / export
    # ------------------------------------------------------------------ #
    def _build_backup_section(self) -> QFrame:
        section = _Section("Backup & Export")
        row = QHBoxLayout()

        export_button = QPushButton(f"{icon('export')}  Export Journals\u2026")
        export_button.setObjectName("SecondaryButton")
        export_button.setCursor(Qt.CursorShape.PointingHandCursor)
        export_button.clicked.connect(self._on_export_clicked)
        row.addWidget(export_button)

        backup_button = QPushButton(f"{icon('backup')}  Backup Database\u2026")
        backup_button.setObjectName("SecondaryButton")
        backup_button.setCursor(Qt.CursorShape.PointingHandCursor)
        backup_button.clicked.connect(self._on_backup_clicked)
        row.addWidget(backup_button)
        row.addStretch(1)
        section.add(row)
        return section

    def _on_export_clicked(self) -> None:
        dialog = ExportDialog(self, pdf_available=self.context.export_service.pdf_available())
        if not dialog.exec():
            return
        fmt = dialog.selected_format()
        extensions = {"json": "json", "markdown": "md", "txt": "txt", "pdf": "pdf"}
        suggested = str(self.context.paths.exports_dir / f"journal_export.{extensions[fmt]}")
        path, _ = QFileDialog.getSaveFileName(self, "Export Journals", suggested)
        if not path:
            return
        journals = self.context.journal_service.list_journals()
        try:
            self.context.export_service.export(journals, fmt, path)
            self.context.toast(f"Exported {len(journals)} journals")
        except Exception as exc:  # noqa: BLE001 - user-facing error, not a silent failure
            self.context.toast(f"Export failed: {exc}")

    def _on_backup_clicked(self) -> None:
        suggested = str(self.context.paths.backups_dir / "journal_backup.db")
        path, _ = QFileDialog.getSaveFileName(self, "Backup Database", suggested)
        if not path:
            return
        try:
            self.context.db.backup_to(path)
            self.context.toast("Backup created")
        except Exception as exc:  # noqa: BLE001
            self.context.toast(f"Backup failed: {exc}")

    # ------------------------------------------------------------------ #
    # Database info
    # ------------------------------------------------------------------ #
    def _build_database_section(self) -> QFrame:
        section = _Section("Database")
        self._db_info_label = QLabel()
        self._db_info_label.setObjectName("MutedLabel")
        self._db_info_label.setWordWrap(True)
        section.add(self._db_info_label)
        return section

    # ------------------------------------------------------------------ #
    # Privacy
    # ------------------------------------------------------------------ #
    def _build_privacy_section(self) -> QFrame:
        section = _Section("Privacy")
        note = QLabel(
            "Everything you write stays on this device, in a local SQLite database. "
            "Nothing is uploaded, synced, or sent anywhere -- including to Claude or any "
            "other external service -- unless you explicitly export or back it up yourself."
        )
        note.setObjectName("MutedLabel")
        note.setWordWrap(True)
        section.add(note)
        return section

    # ------------------------------------------------------------------ #
    # Refresh
    # ------------------------------------------------------------------ #
    def refresh(self) -> None:
        settings = self.context.settings
        self._light_radio.blockSignals(True)
        self._dark_radio.blockSignals(True)
        self._light_radio.setChecked(settings.theme == "light")
        self._dark_radio.setChecked(settings.theme == "dark")
        self._light_radio.blockSignals(False)
        self._dark_radio.blockSignals(False)

        self._font_size_slider.blockSignals(True)
        self._font_size_slider.setValue(settings.journal_font_size)
        self._font_size_slider.blockSignals(False)
        self._font_size_label.setText(f"{settings.journal_font_size}px")

        self._line_spacing_slider.blockSignals(True)
        self._line_spacing_slider.setValue(round(settings.line_spacing * 10))
        self._line_spacing_slider.blockSignals(False)
        self._line_spacing_label.setText(f"{settings.line_spacing:.1f}\u00d7")

        self._default_topic_combo.blockSignals(True)
        self._default_topic_combo.clear()
        self._default_topic_combo.addItem("None", None)
        for topic in self.context.topic_service.list_topics():
            self._default_topic_combo.addItem(f"{topic.icon} {topic.name}", topic.id)
        index = self._default_topic_combo.findData(settings.default_topic_id)
        self._default_topic_combo.setCurrentIndex(index if index >= 0 else 0)
        self._default_topic_combo.blockSignals(False)

        self._reminder_check.blockSignals(True)
        self._reminder_check.setChecked(settings.reminder_enabled)
        self._reminder_check.blockSignals(False)
        self._reminder_time.blockSignals(True)
        hour, _, minute = settings.reminder_time.partition(":")
        self._reminder_time.setTime(QTime(int(hour), int(minute)))
        self._reminder_time.blockSignals(False)

        size = _human_size(self.context.db.database_size_bytes())
        count = self.context.journal_service.total_count()
        self._db_info_label.setText(
            f"Location: {self.context.paths.database_path}\n"
            f"Size: {size}  \u00b7  {count} {'entry' if count == 1 else 'entries'}"
        )
