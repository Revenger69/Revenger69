"""Calendar screen: navigate months, see at a glance which days have an
entry (a small dot indicator), and open or create a journal for any
selected date."""
from __future__ import annotations

import datetime as dt

from PySide6.QtCore import QDate, QPointF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QCalendarWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.context import AppContext
from app.ui.widgets.journal_list_view import JournalListView
from app.utils.icons import icon


class _MarkedCalendar(QCalendarWidget):
    def __init__(self, accent_color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._marked: set[dt.date] = set()
        self._accent_color = accent_color
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setGridVisible(False)

    def set_marked_dates(self, dates: set[dt.date]) -> None:
        self._marked = dates
        self.updateCells()

    def set_accent_color(self, color: str) -> None:
        self._accent_color = color
        self.updateCells()

    def paintCell(self, painter: QPainter, rect, date: QDate) -> None:  # noqa: N802 - Qt override
        super().paintCell(painter, rect, date)
        py_date = date.toPython()
        if py_date in self._marked:
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor(self._accent_color))
            painter.setPen(Qt.PenStyle.NoPen)
            cx = rect.center().x()
            cy = rect.bottom() - 8
            painter.drawEllipse(QPointF(cx, cy), 3, 3)
            painter.restore()


class CalendarView(QWidget):
    def __init__(self, context: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.context = context

        outer = QVBoxLayout(self)
        outer.setContentsMargins(36, 28, 36, 28)
        outer.setSpacing(16)

        title = QLabel("Calendar")
        title.setObjectName("PageTitle")
        outer.addWidget(title)
        subtitle = QLabel("Browse your journal, day by day.")
        subtitle.setObjectName("PageSubtitle")
        outer.addWidget(subtitle)

        body = QHBoxLayout()
        body.setSpacing(24)

        self._calendar = _MarkedCalendar("#6E8AA6")
        self._calendar.setMinimumWidth(360)
        self._calendar.selectionChanged.connect(self._on_date_selected)
        body.addWidget(self._calendar, stretch=0)

        detail_panel = QVBoxLayout()
        detail_panel.setSpacing(10)

        detail_header = QHBoxLayout()
        self._detail_date_label = QLabel()
        self._detail_date_label.setObjectName("SectionHeader")
        detail_header.addWidget(self._detail_date_label)
        detail_header.addStretch(1)
        self._create_button = QPushButton(f"{icon('add')} Create journal for this date")
        self._create_button.setObjectName("PrimaryButton")
        self._create_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._create_button.clicked.connect(self._on_create_for_date)
        detail_header.addWidget(self._create_button)
        detail_panel.addLayout(detail_header)

        self._detail_list = JournalListView()
        self._detail_list.journal_opened.connect(lambda jid: self.context.open_editor(jid))
        self._detail_list.favorite_toggled.connect(self._on_favorite_toggled)
        detail_panel.addWidget(self._detail_list, stretch=1)

        body.addLayout(detail_panel, stretch=1)
        outer.addLayout(body, stretch=1)

    def _selected_date(self) -> dt.date:
        return self._calendar.selectedDate().toPython()

    def _on_date_selected(self) -> None:
        self._refresh_detail()

    def _on_create_for_date(self) -> None:
        self.context.open_editor(None, self._selected_date())

    def _on_favorite_toggled(self, journal_id: int) -> None:
        self.context.journal_service.toggle_favorite(journal_id)
        self.context.notify_data_changed()

    def _refresh_detail(self) -> None:
        selected = self._selected_date()
        today = dt.date.today()
        if selected == today:
            label = "Today"
        else:
            label = selected.strftime("%A, %B %-d, %Y")
        self._detail_date_label.setText(label.upper())

        journals = self.context.journal_service.get_journals_for_date(selected)
        self._detail_list.set_journals(
            journals,
            grouped=False,
            empty_title="No entry for this date.",
            empty_subtitle="Write about this day whenever you're ready.",
        )

    def refresh(self) -> None:
        marked = self.context.journal_service.get_all_journal_dates()
        self._calendar.set_marked_dates(marked)
        self._calendar.set_accent_color(
            "#8FADC9" if self.context.settings.theme == "dark" else "#6E8AA6"
        )
        self._refresh_detail()
