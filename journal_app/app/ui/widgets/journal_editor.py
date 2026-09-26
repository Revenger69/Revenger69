"""The distraction-free journal editor: the visual and functional heart
of the app. Autosaves in the background on a short debounce, never
interrupting the user with save dialogs or spinners."""
from __future__ import annotations

import datetime as dt
import shutil
import uuid
from pathlib import Path

from PySide6.QtCore import QDate, Qt, QTimer, Signal
from PySide6.QtGui import QFont, QTextBlockFormat, QTextCursor
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.services.journal_service import JournalNotFoundError
from app.ui.context import AppContext
from app.ui.layout_utils import clear_layout
from app.ui.styles.fonts import FontResolver
from app.ui.widgets.image_thumbnail import ImageThumbnail
from app.ui.widgets.mood_selector import MoodSelector
from app.ui.widgets.tag_selector import TagSelector
from app.utils.date_utils import word_count
from app.utils.icons import icon

AUTOSAVE_DELAY_MS = 900
MAX_CONTENT_WIDTH = 760


class JournalEditor(QWidget):
    back_requested = Signal()

    def __init__(self, context: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.context = context
        self.journal_id: int | None = None
        self._is_favorite = False
        self._dirty = False
        self._loading = False
        self._media_ids: dict[int, str] = {}

        self._autosave_timer = QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.timeout.connect(self._perform_save)

        self._build_ui()
        context.settings_changed.connect(self._apply_typography)

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 20, 32, 20)
        outer.setSpacing(14)

        # --- Top bar -------------------------------------------------- #
        top_bar = QHBoxLayout()
        back_button = QPushButton(f"{icon('back')} Back")
        back_button.setObjectName("SecondaryButton")
        back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        back_button.clicked.connect(self._on_back)
        top_bar.addWidget(back_button)
        top_bar.addStretch(1)

        self._status_label = QLabel("")
        self._status_label.setObjectName("StatusLabel")
        top_bar.addWidget(self._status_label)

        self._favorite_button = QPushButton(icon("favorite_off"))
        self._favorite_button.setObjectName("IconButton")
        self._favorite_button.setCheckable(True)
        self._favorite_button.setFixedSize(30, 30)
        self._favorite_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._favorite_button.setToolTip("Favorite this entry")
        self._favorite_button.clicked.connect(self._on_favorite_clicked)
        top_bar.addWidget(self._favorite_button)

        self._delete_button = QPushButton(icon("delete"))
        self._delete_button.setObjectName("IconButton")
        self._delete_button.setFixedSize(30, 30)
        self._delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._delete_button.setToolTip("Delete this entry")
        self._delete_button.clicked.connect(self._on_delete_clicked)
        top_bar.addWidget(self._delete_button)
        outer.addLayout(top_bar)

        # --- Scrollable writing column --------------------------------- #
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_host = QWidget()
        scroll.setWidget(content_host)
        host_layout = QHBoxLayout(content_host)
        host_layout.setContentsMargins(0, 0, 0, 0)
        host_layout.addStretch(1)

        column = QWidget()
        column.setMaximumWidth(MAX_CONTENT_WIDTH)
        column_layout = QVBoxLayout(column)
        column_layout.setContentsMargins(0, 0, 0, 0)
        column_layout.setSpacing(10)
        host_layout.addWidget(column, stretch=0)
        host_layout.addStretch(1)
        outer.addWidget(scroll, stretch=1)

        # Meta row: date + topic
        meta_row = QHBoxLayout()
        self._date_edit = QDateEdit(QDate.currentDate())
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("MMM d, yyyy")
        self._date_edit.setFixedWidth(140)
        self._date_edit.dateChanged.connect(self._mark_dirty)
        meta_row.addWidget(self._date_edit)

        self._topic_combo = QComboBox()
        self._topic_combo.setFixedWidth(180)
        self._topic_combo.currentIndexChanged.connect(self._mark_dirty)
        meta_row.addWidget(self._topic_combo)

        meta_row.addStretch(1)
        self._written_label = QLabel("")
        self._written_label.setObjectName("MutedLabel")
        meta_row.addWidget(self._written_label)
        column_layout.addLayout(meta_row)

        # Title
        self._title_input = QLineEdit()
        self._title_input.setObjectName("TitleInput")
        self._title_input.setPlaceholderText("Title")
        self._title_input.textChanged.connect(self._mark_dirty)
        column_layout.addWidget(self._title_input)

        # Content
        self._content_editor = QTextEdit()
        self._content_editor.setObjectName("ContentEditor")
        self._content_editor.setPlaceholderText("How was your day?")
        self._content_editor.setMinimumHeight(320)
        self._content_editor.textChanged.connect(self._on_content_changed)
        column_layout.addWidget(self._content_editor, stretch=1)

        self._word_count_label = QLabel("0 words")
        self._word_count_label.setObjectName("MutedLabel")
        column_layout.addWidget(self._word_count_label)

        # Mood
        mood_row = QVBoxLayout()
        mood_row.setSpacing(4)
        mood_caption = QLabel("Mood")
        mood_caption.setObjectName("SectionHeader")
        mood_row.addWidget(mood_caption)
        self._mood_selector = MoodSelector()
        self._mood_selector.mood_changed.connect(lambda _m: self._mark_dirty())
        mood_row.addWidget(self._mood_selector)
        column_layout.addLayout(mood_row)

        # Tags
        tags_row = QVBoxLayout()
        tags_row.setSpacing(4)
        tags_caption = QLabel("Tags")
        tags_caption.setObjectName("SectionHeader")
        tags_row.addWidget(tags_caption)
        self._tag_selector = TagSelector()
        self._tag_selector.tags_changed.connect(lambda _t: self._mark_dirty())
        tags_row.addWidget(self._tag_selector)
        column_layout.addLayout(tags_row)

        # Photos
        photo_section = QVBoxLayout()
        photo_section.setSpacing(4)
        photo_caption = QLabel("Photo")
        photo_caption.setObjectName("SectionHeader")
        photo_section.addWidget(photo_caption)
        self._photo_row = QHBoxLayout()
        self._photo_row.setSpacing(8)
        add_photo_button = QPushButton(f"{icon('image')} Add a photo")
        add_photo_button.setObjectName("SecondaryButton")
        add_photo_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_photo_button.clicked.connect(self._on_add_photo)
        self._photo_row.addWidget(add_photo_button)
        self._photo_row.addStretch(1)
        photo_section.addLayout(self._photo_row)
        column_layout.addLayout(photo_section)

        column_layout.addSpacing(20)

    # ------------------------------------------------------------------ #
    # Loading state in/out
    # ------------------------------------------------------------------ #
    def _refresh_topic_combo(self, selected_id: int | None) -> None:
        self._topic_combo.blockSignals(True)
        self._topic_combo.clear()
        self._topic_combo.addItem("No topic", None)
        for topic in self.context.topic_service.list_topics():
            self._topic_combo.addItem(f"{topic.icon} {topic.name}", topic.id)
        index = self._topic_combo.findData(selected_id)
        self._topic_combo.setCurrentIndex(index if index >= 0 else 0)
        self._topic_combo.blockSignals(False)

    def load_new(self, prefill_date: dt.date | None = None) -> None:
        self._loading = True
        self.journal_id = None
        self._is_favorite = False
        self._media_ids = {}
        self._favorite_button.setChecked(False)
        self._favorite_button.setText(icon("favorite_off"))
        self._title_input.clear()
        self._content_editor.clear()
        self._date_edit.setDate(QDate(prefill_date) if prefill_date else QDate.currentDate())
        default_topic = self.context.settings.default_topic_id
        self._refresh_topic_combo(default_topic)
        self._mood_selector.set_mood(None)
        self._tag_selector.set_tags([])
        self._written_label.setText("")
        self._clear_photo_thumbnails()
        self._status_label.setText("")
        self._dirty = False
        self._apply_typography()
        self._update_word_count()
        self._loading = False
        self._title_input.setFocus()

    def load_journal(self, journal_id: int) -> None:
        try:
            dto = self.context.journal_service.get_journal(journal_id)
        except JournalNotFoundError:
            self.load_new()
            return
        self._loading = True
        self.journal_id = dto.id
        self._is_favorite = dto.is_favorite
        self._favorite_button.setChecked(dto.is_favorite)
        self._favorite_button.setText(icon("favorite_on") if dto.is_favorite else icon("favorite_off"))
        self._title_input.setText(dto.title)
        self._content_editor.setPlainText(dto.content)
        self._date_edit.setDate(QDate(dto.journal_date))
        self._refresh_topic_combo(dto.topic.id if dto.topic else None)
        self._mood_selector.set_mood(dto.mood)
        self._tag_selector.set_tags(dto.tags)
        self._written_label.setText(
            f"Written {dto.created_at.strftime('%b %-d')} at {dto.created_at.strftime('%-I:%M %p')}"
        )
        self._refresh_media(dto.media)
        self._status_label.setText("Saved")
        self._dirty = False
        self._apply_typography()
        self._update_word_count()
        self._loading = False

    # ------------------------------------------------------------------ #
    # Typography
    # ------------------------------------------------------------------ #
    def _apply_typography(self) -> None:
        settings = self.context.settings
        self._content_editor.setFont(FontResolver.serif_font(settings.journal_font_size))
        self._title_input.setFont(
            FontResolver.serif_font(settings.journal_font_size + 8, QFont.Weight.Bold)
        )
        self._content_editor.document().setDocumentMargin(4)

        cursor = self._content_editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        block_format = QTextBlockFormat()
        block_format.setLineHeight(
            settings.line_spacing * 100, QTextBlockFormat.LineHeightTypes.ProportionalHeight.value
        )
        cursor.mergeBlockFormat(block_format)

    # ------------------------------------------------------------------ #
    # Dirty tracking + autosave
    # ------------------------------------------------------------------ #
    def _mark_dirty(self, *_args) -> None:
        if self._loading:
            return
        self._dirty = True
        self._status_label.setText("Saving\u2026")
        self._autosave_timer.start(AUTOSAVE_DELAY_MS)

    def _on_content_changed(self) -> None:
        self._update_word_count()
        self._mark_dirty()

    def _update_word_count(self) -> None:
        count = word_count(self._content_editor.toPlainText())
        self._word_count_label.setText(f"{count} word" if count == 1 else f"{count} words")

    def _current_field_values(self) -> dict:
        return dict(
            title=self._title_input.text(),
            content=self._content_editor.toPlainText(),
            journal_date=self._date_edit.date().toPython(),
            topic_id=self._topic_combo.currentData(),
            mood=self._mood_selector.mood(),
            tags=self._tag_selector.tags(),
            is_favorite=self._is_favorite,
        )

    def _perform_save(self) -> None:
        if not self._dirty:
            return
        values = self._current_field_values()
        if self.journal_id is None:
            if not values["title"].strip() and not values["content"].strip():
                # Nothing meaningful typed yet -- don't create a ghost entry.
                self._dirty = False
                self._status_label.setText("")
                return
            dto = self.context.journal_service.create_journal(**values)
            self.journal_id = dto.id
        else:
            dto = self.context.journal_service.update_journal(self.journal_id, **values)
        self._dirty = False
        self._word_count_label.setText(f"{dto.word_count} words")
        self._status_label.setText(f"Saved \u00b7 {dt.datetime.now().strftime('%-I:%M %p')}")
        self.context.notify_data_changed()

    def flush(self) -> None:
        """Force an immediate save of any pending changes (called before
        navigating away or closing the app)."""
        if self._autosave_timer.isActive():
            self._autosave_timer.stop()
        self._perform_save()

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def _on_back(self) -> None:
        self.flush()
        self.back_requested.emit()

    def _on_favorite_clicked(self) -> None:
        self._is_favorite = self._favorite_button.isChecked()
        self._favorite_button.setText(icon("favorite_on") if self._is_favorite else icon("favorite_off"))
        self._mark_dirty()
        self.flush()

    def _on_delete_clicked(self) -> None:
        from app.ui.dialogs.confirm_dialog import ConfirmDialog

        if self.journal_id is None:
            self.back_requested.emit()
            return
        confirmed = ConfirmDialog.confirm(
            self,
            "Delete this entry?",
            "This journal entry will be permanently deleted. This cannot be undone.",
            confirm_label="Delete",
        )
        if confirmed:
            self.context.journal_service.delete_journal(self.journal_id)
            self.context.notify_data_changed()
            self.context.toast("Journal deleted")
            self.journal_id = None
            self.back_requested.emit()

    def _ensure_journal_exists(self) -> int:
        if self.journal_id is None:
            values = self._current_field_values()
            dto = self.context.journal_service.create_journal(**values)
            self.journal_id = dto.id
            self._dirty = False
            self._status_label.setText(f"Saved \u00b7 {dt.datetime.now().strftime('%-I:%M %p')}")
            self.context.notify_data_changed()
        return self.journal_id

    def _on_add_photo(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose a photo", "", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp)"
        )
        if not file_path:
            return
        journal_id = self._ensure_journal_exists()
        dest_dir = self.context.paths.media_dir
        dest_name = f"{journal_id}_{uuid.uuid4().hex[:8]}{Path(file_path).suffix.lower()}"
        dest_path = dest_dir / dest_name
        try:
            shutil.copy2(file_path, dest_path)
        except OSError:
            self.context.toast("Couldn't add that photo")
            return
        dto = self.context.journal_service.attach_media(journal_id, str(dest_path))
        self._refresh_media(dto.media)
        self.context.toast("Photo added")

    def _clear_photo_thumbnails(self) -> None:
        clear_layout(self._photo_row, keep_last=2)

    def _refresh_media(self, media_list) -> None:
        clear_layout(self._photo_row, keep_last=2)
        for media in media_list:
            thumb = ImageThumbnail(media.file_path)
            thumb.remove_requested.connect(lambda mid=media.id: self._on_remove_photo(mid))
            self._photo_row.insertWidget(self._photo_row.count() - 2, thumb)

    def _on_remove_photo(self, media_id: int) -> None:
        if self.journal_id is None:
            return
        dto = self.context.journal_service.remove_media(self.journal_id, media_id)
        self._refresh_media(dto.media)
