"""App-wide constants: default topics, moods, font fallback chains."""
from __future__ import annotations

# (name, color hex, icon glyph)
DEFAULT_TOPICS: list[tuple[str, str, str]] = [
    ("Personal", "#8A9A5B", "\U0001F331"),      # seedling
    ("Work", "#6E8AA6", "\U0001F4BC"),           # briefcase
    ("Family", "#C97B63", "\U0001F3E1"),         # house
    ("Travel", "#4F9D9D", "\u2708"),             # airplane
    ("Ideas", "#B08968", "\U0001F4A1"),          # bulb
    ("Goals", "#9C6ADE", "\U0001F3AF"),          # target
    ("Memories", "#D68C8C", "\U0001F4F7"),       # camera
    ("Gratitude", "#C9A227", "\U0001F64F"),      # folded hands
]

# (key, label, glyph)
MOODS: list[tuple[str, str, str]] = [
    ("happy", "Happy", "\U0001F60A"),
    ("calm", "Calm", "\U0001F60C"),
    ("excited", "Excited", "\U0001F929"),
    ("grateful", "Grateful", "\U0001F64F"),
    ("tired", "Tired", "\U0001F634"),
    ("anxious", "Anxious", "\U0001F630"),
    ("sad", "Sad", "\U0001F622"),
    ("angry", "Angry", "\U0001F620"),
]

MOOD_GLYPHS: dict[str, str] = {key: glyph for key, _label, glyph in MOODS}
MOOD_LABELS: dict[str, str] = {key: label for key, label, _glyph in MOODS}

# Fallback chains: QFontDatabase is queried for the first family that
# actually exists on the running system, so the app looks good everywhere
# without bundling font files.
UI_FONT_CANDIDATES: list[str] = [
    "Inter", "Segoe UI", "SF Pro Text", "Helvetica Neue", "Ubuntu", "Noto Sans", "Arial",
]

SERIF_FONT_CANDIDATES: list[str] = [
    "Iowan Old Style", "Georgia", "Merriweather", "Noto Serif", "PT Serif",
    "Times New Roman", "Liberation Serif", "DejaVu Serif",
]

NAV_ITEMS: list[tuple[str, str, str]] = [
    # (key, label, glyph)
    ("dashboard", "Home", "\U0001F3E0"),
    ("journal", "Journal", "\U0001F4D6"),
    ("calendar", "Calendar", "\U0001F4C5"),
    ("topics", "Topics", "\U0001F3F7"),
    ("favorites", "Favorites", "\u2B50"),
    ("search", "Search", "\U0001F50D"),
    ("settings", "Settings", "\u2699"),
]

APP_TITLE = "Paper — A Private Journal"
