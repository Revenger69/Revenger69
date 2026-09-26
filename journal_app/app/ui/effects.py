"""Small, reusable visual-effect helpers (drop shadows) shared across
cards and elevated surfaces. QSS has no box-shadow support, so a subtle
QGraphicsDropShadowEffect is what gives cards their "premium" lift.
"""
from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget


def apply_card_shadow(widget: QWidget, *, blur: int = 24, y_offset: int = 4, alpha: int = 40) -> None:
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, y_offset)
    effect.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(effect)
