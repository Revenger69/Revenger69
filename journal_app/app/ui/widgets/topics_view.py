"""Topics screen: a grid of colorful topic tiles, with create / rename /
recolor / delete, and drilling into a topic to see its entries."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.context import AppContext
from app.ui.dialogs.confirm_dialog import ConfirmDialog
from app.ui.dialogs.topic_dialog import TopicDialog
from app.ui.layout_utils import clear_layout
from app.ui.widgets.empty_state import EmptyState
from app.ui.widgets.journal_list_view import JournalListView
from app.ui.widgets.topic_card import TopicCard
from app.utils.icons import icon

GRID_COLUMNS = 3


class TopicsView(QWidget):
    def __init__(self, context: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.context = context
        self._current_topic_id: int | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        outer.addWidget(self._stack)

        self._grid_page = self._build_grid_page()
        self._detail_page = self._build_detail_page()
        self._stack.addWidget(self._grid_page)
        self._stack.addWidget(self._detail_page)

    # ------------------------------------------------------------------ #
    # Grid page
    # ------------------------------------------------------------------ #
    def _build_grid_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(16)

        header_row = QHBoxLayout()
        title = QLabel("Topics")
        title.setObjectName("PageTitle")
        header_row.addWidget(title)
        header_row.addStretch(1)
        new_button = QPushButton(f"{icon('add')}  New Topic")
        new_button.setObjectName("PrimaryButton")
        new_button.setCursor(Qt.CursorShape.PointingHandCursor)
        new_button.clicked.connect(self._on_new_topic)
        header_row.addWidget(new_button)
        layout.addLayout(header_row)

        subtitle = QLabel("Organize your entries by what matters to you.")
        subtitle.setObjectName("PageSubtitle")
        layout.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll, stretch=1)

        self._grid_host = QWidget()
        self._grid_layout = QGridLayout(self._grid_host)
        self._grid_layout.setSpacing(14)
        scroll.setWidget(self._grid_host)
        return page

    def _build_detail_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(12)

        back_row = QHBoxLayout()
        back_button = QPushButton(f"{icon('back')} All Topics")
        back_button.setObjectName("SecondaryButton")
        back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        back_button.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        back_row.addWidget(back_button)
        back_row.addStretch(1)
        layout.addLayout(back_row)

        self._detail_title = QLabel()
        self._detail_title.setObjectName("PageTitle")
        layout.addWidget(self._detail_title)

        self._detail_subtitle = QLabel()
        self._detail_subtitle.setObjectName("PageSubtitle")
        layout.addWidget(self._detail_subtitle)

        self._detail_list = JournalListView()
        self._detail_list.journal_opened.connect(lambda jid: self.context.open_editor(jid))
        self._detail_list.favorite_toggled.connect(self._on_favorite_toggled)
        layout.addWidget(self._detail_list, stretch=1)
        return page

    # ------------------------------------------------------------------ #
    # Refresh / population
    # ------------------------------------------------------------------ #
    def refresh(self) -> None:
        clear_layout(self._grid_layout)

        topics = self.context.topic_service.list_topics()
        if not topics:
            empty = EmptyState(
                "\U0001F3F7", "No topics yet.", "Create a topic to start organizing your journals.",
                "New Topic", self._on_new_topic,
            )
            self._grid_layout.addWidget(empty, 0, 0, 1, GRID_COLUMNS)
        else:
            for i, topic in enumerate(topics):
                count = self.context.topic_service.journal_count(topic.id)
                card = TopicCard(topic, count)
                card.opened.connect(self._open_topic_detail)
                card.rename_requested.connect(self._on_rename_topic)
                card.recolor_requested.connect(self._on_recolor_topic)
                card.delete_requested.connect(self._on_delete_topic)
                self._grid_layout.addWidget(card, i // GRID_COLUMNS, i % GRID_COLUMNS)

        if self._current_topic_id is not None and self._stack.currentIndex() == 1:
            self._populate_detail(self._current_topic_id)

    def _open_topic_detail(self, topic_id: int) -> None:
        self._current_topic_id = topic_id
        self._populate_detail(topic_id)
        self._stack.setCurrentIndex(1)

    def _populate_detail(self, topic_id: int) -> None:
        topics = {t.id: t for t in self.context.topic_service.list_topics()}
        topic = topics.get(topic_id)
        if topic is None:
            self._stack.setCurrentIndex(0)
            return
        journals = self.context.journal_service.list_journals(topic_id=topic_id)
        self._detail_title.setText(f"{topic.icon} {topic.name}")
        self._detail_subtitle.setText(f"{len(journals)} {'entry' if len(journals) == 1 else 'entries'}")
        self._detail_list.set_journals(
            journals,
            empty_title="No entries in this topic yet.",
            empty_subtitle="Journals you tag with this topic will show up here.",
        )

    def _on_favorite_toggled(self, journal_id: int) -> None:
        self.context.journal_service.toggle_favorite(journal_id)
        self.context.notify_data_changed()

    # ------------------------------------------------------------------ #
    # Topic CRUD
    # ------------------------------------------------------------------ #
    def _on_new_topic(self) -> None:
        dialog = TopicDialog(self)
        if dialog.exec():
            name, color, glyph = dialog.result_values()
            if name:
                try:
                    self.context.topic_service.create_topic(name, color, glyph)
                    self.context.toast("Topic created")
                    self.context.notify_data_changed()
                except Exception as exc:  # noqa: BLE001 - surfaced to the user, not swallowed silently
                    self.context.toast(str(exc))

    def _on_rename_topic(self, topic_id: int) -> None:
        topics = {t.id: t for t in self.context.topic_service.list_topics()}
        topic = topics.get(topic_id)
        if topic is None:
            return
        dialog = TopicDialog(self, name=topic.name, color=topic.color, icon=topic.icon)
        if dialog.exec():
            name, color, glyph = dialog.result_values()
            if name:
                self.context.topic_service.rename_topic(topic_id, name)
                self.context.topic_service.update_style(topic_id, color=color, icon=glyph)
                self.context.notify_data_changed()

    def _on_recolor_topic(self, topic_id: int) -> None:
        self._on_rename_topic(topic_id)

    def _on_delete_topic(self, topic_id: int) -> None:
        topics = {t.id: t for t in self.context.topic_service.list_topics()}
        topic = topics.get(topic_id)
        if topic is None:
            return
        confirmed = ConfirmDialog.confirm(
            self,
            f"Delete '{topic.name}'?",
            "Entries in this topic won't be deleted -- they'll just no longer have a topic.",
            confirm_label="Delete Topic",
        )
        if confirmed:
            self.context.topic_service.delete_topic(topic_id)
            self.context.toast("Topic deleted")
            if self._current_topic_id == topic_id:
                self._current_topic_id = None
                self._stack.setCurrentIndex(0)
            self.context.notify_data_changed()
