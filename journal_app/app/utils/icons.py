"""Centralized glyphs used throughout the UI. The app intentionally uses
plain unicode glyphs instead of an icon font/asset pack, keeping the
whole app self-contained (no bundled binary assets to ship or license)."""
from __future__ import annotations

ICONS = {
    "new": "\u270E",           # pencil
    "search": "\U0001F50D",
    "favorite_on": "\u2605",
    "favorite_off": "\u2606",
    "calendar": "\U0001F4C5",
    "topic": "\U0001F3F7",
    "settings": "\u2699",
    "delete": "\U0001F5D1",
    "edit": "\u270F",
    "export": "\u2B06",
    "backup": "\U0001F4BE",
    "close": "\u2715",
    "back": "\u2190",
    "add": "\u2795",
    "check": "\u2713",
    "tag": "\U0001F3F7",
    "streak": "\U0001F525",
    "image": "\U0001F5BC",
    "sun": "\u2600",
    "moon": "\U0001F319",
    "book": "\U0001F4D6",
    "empty_book": "\U0001F4DD",
}


def icon(name: str) -> str:
    return ICONS.get(name, "")
