"""A small, self-dismissing notification banner ("Saved", "Journal
deleted", "Backup created") that floats over the bottom of the window
without stealing focus or interrupting the user's writing."""
from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtWidgets import QGraphicsOpacityEffect, QHBoxLayout, QLabel, QWidget

from app.ui.effects import apply_card_shadow


class Toast(QWidget):
    """Attach one Toast per top-level window and call `show_message(...)`
    as many times as needed; it repositions and restarts its own timer."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Widget)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self._frame = QWidget(self)
        self._frame.setObjectName("Toast")
        layout = QHBoxLayout(self._frame)
        layout.setContentsMargins(16, 10, 16, 10)
        self._label = QLabel("", self._frame)
        self._label.setObjectName("ToastLabel")
        layout.addWidget(self._label)
        apply_card_shadow(self._frame, blur=30, y_offset=6, alpha=70)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._frame)

        self._opacity = QGraphicsOpacityEffect(self._frame)
        self._frame.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(0.0)

        self._fade_in = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade_in.setDuration(180)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._fade_out = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade_out.setDuration(280)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_out.finished.connect(self.hide)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._fade_out.start)

        self.hide()

    def show_message(self, text: str, duration_ms: int = 2200) -> None:
        self._label.setText(text)
        self.adjustSize()
        self._reposition()
        self.show()
        self.raise_()
        self._fade_out.stop()
        self._opacity.setOpacity(1.0)
        self._fade_in.start()
        self._hide_timer.start(duration_ms)

    def _reposition(self) -> None:
        if self.parentWidget() is None:
            return
        parent_rect = self.parentWidget().rect()
        self.resize(parent_rect.width(), self.sizeHint().height() + 24)
        self.move(0, parent_rect.height() - self.height())

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
