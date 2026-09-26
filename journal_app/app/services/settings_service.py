"""User preferences: theme, typography, default topic, and reminder time.

Stored as a small JSON file (not the database) so preferences can be read
before the DB is even opened, and so a corrupt/missing prefs file never
threatens journal data.
"""
from __future__ import annotations

import dataclasses
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

from app.config import AppPaths

logger = logging.getLogger(__name__)


@dataclass
class AppSettings:
    theme: str = "light"                 # "light" | "dark"
    ui_font_size: int = 10
    journal_font_size: int = 16
    line_spacing: float = 1.5             # multiplier
    default_topic_id: int | None = None
    reminder_enabled: bool = False
    reminder_time: str = "20:00"          # HH:MM, 24h
    last_opened_view: str = "dashboard"

    def clamp(self) -> "AppSettings":
        """Keep values within sane, UI-safe bounds after loading untrusted
        JSON from disk."""
        self.ui_font_size = max(8, min(18, self.ui_font_size))
        self.journal_font_size = max(12, min(28, self.journal_font_size))
        self.line_spacing = max(1.0, min(2.2, self.line_spacing))
        if self.theme not in ("light", "dark"):
            self.theme = "light"
        return self


class SettingsService:
    def __init__(self, paths: AppPaths | None = None) -> None:
        self.paths = paths or AppPaths()
        self._settings: AppSettings | None = None

    def load(self) -> AppSettings:
        if self._settings is not None:
            return self._settings
        path = self.paths.settings_path
        if not path.exists():
            self._settings = AppSettings()
            self.save(self._settings)
            return self._settings
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            known_fields = {f.name for f in dataclasses.fields(AppSettings)}
            filtered = {k: v for k, v in data.items() if k in known_fields}
            self._settings = AppSettings(**filtered).clamp()
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            logger.warning("Could not parse settings file (%s); using defaults.", exc)
            self._settings = AppSettings()
        return self._settings

    def save(self, settings: AppSettings) -> None:
        self._settings = settings.clamp()
        tmp_path = self.paths.settings_path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(asdict(self._settings), indent=2), encoding="utf-8")
        tmp_path.replace(self.paths.settings_path)  # atomic on POSIX + Windows

    def update(self, **kwargs) -> AppSettings:
        current = self.load()
        updated = dataclasses.replace(current, **kwargs)
        self.save(updated)
        return updated
