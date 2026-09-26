"""Color design tokens for the light ("warm paper") and dark themes.

Keeping every color as a named token -- rather than sprinkling hex codes
through widget code -- is what makes it possible to build a *real* dark
theme (distinct palette, not an inverted light theme) and to keep both
themes visually consistent.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str

    # Surfaces
    bg_primary: str        # main window / page background
    bg_secondary: str      # sidebar, panels
    bg_elevated: str       # cards, editor surface
    bg_hover: str          # hover state for list rows / nav items
    bg_selected: str       # selected nav item / active tab

    # Text
    text_primary: str
    text_secondary: str
    text_tertiary: str
    text_on_accent: str

    # Structure
    border: str
    border_subtle: str
    shadow: str

    # Accents
    accent: str             # primary accent (buttons, links, active states)
    accent_hover: str
    accent_alt: str         # secondary accent (used sparingly)
    accent_warm: str        # warm accent (favorites/star)
    danger: str
    success: str


LIGHT_THEME = Theme(
    name="light",
    bg_primary="#FBF7F0",
    bg_secondary="#F3ECDF",
    bg_elevated="#FFFFFF",
    bg_hover="#EFE6D6",
    bg_selected="#E8DCC4",
    text_primary="#2E2A24",
    text_secondary="#6B6357",
    text_tertiary="#9C9486",
    text_on_accent="#FFFFFF",
    border="#E4DCC9",
    border_subtle="#EDE6D6",
    shadow="rgba(46, 42, 36, 0.12)",
    accent="#6E8AA6",
    accent_hover="#5D7893",
    accent_alt="#8A9A5B",
    accent_warm="#C97B63",
    danger="#B85C5C",
    success="#7A9B6E",
)

DARK_THEME = Theme(
    name="dark",
    bg_primary="#1D1B18",
    bg_secondary="#242220",
    bg_elevated="#2B2825",
    bg_hover="#332F2A",
    bg_selected="#3A362E",
    text_primary="#EDE7DA",
    text_secondary="#B6AE9E",
    text_tertiary="#847C6E",
    text_on_accent="#1D1B18",
    border="#3A362F",
    border_subtle="#302C27",
    shadow="rgba(0, 0, 0, 0.45)",
    accent="#8FADC9",
    accent_hover="#A2BCD5",
    accent_alt="#A3B27C",
    accent_warm="#DDA089",
    danger="#DD8F8F",
    success="#9CBB90",
)


class ThemeManager:
    """Resolves a theme name to a Theme instance. A single place to add
    more themes later (e.g. "sepia", "high contrast") without touching
    every widget that consumes colors."""

    _themes = {"light": LIGHT_THEME, "dark": DARK_THEME}

    @classmethod
    def get(cls, name: str) -> Theme:
        return cls._themes.get(name, LIGHT_THEME)

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._themes.keys())
