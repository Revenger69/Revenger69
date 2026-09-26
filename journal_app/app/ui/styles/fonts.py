"""Resolves the app's two font roles -- clean UI sans and readable serif
for long-form writing -- to whatever matching family actually exists on
the running system, via QFontDatabase. This avoids bundling font files
while still getting a considered typographic feel on every platform.
"""
from __future__ import annotations

from PySide6.QtGui import QFont, QFontDatabase

from app.config import SERIF_FONT_CANDIDATES, UI_FONT_CANDIDATES


class FontResolver:
    _ui_family: str | None = None
    _serif_family: str | None = None

    @classmethod
    def _first_available(cls, candidates: list[str]) -> str:
        available = set(QFontDatabase.families())
        for candidate in candidates:
            if candidate in available:
                return candidate
        return candidates[-1]  # last resort fallback name; Qt substitutes a real font

    @classmethod
    def ui_family(cls) -> str:
        if cls._ui_family is None:
            cls._ui_family = cls._first_available(UI_FONT_CANDIDATES)
        return cls._ui_family

    @classmethod
    def serif_family(cls) -> str:
        if cls._serif_family is None:
            cls._serif_family = cls._first_available(SERIF_FONT_CANDIDATES)
        return cls._serif_family

    @classmethod
    def ui_font(cls, size: int = 10, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
        font = QFont(cls.ui_family(), size)
        font.setWeight(weight)
        return font

    @classmethod
    def serif_font(cls, size: int = 16, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
        font = QFont(cls.serif_family(), size)
        font.setWeight(weight)
        return font
