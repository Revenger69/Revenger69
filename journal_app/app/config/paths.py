"""Central definition of all filesystem locations the app touches.

Keeping paths in one place avoids hardcoded strings scattered across the
codebase and makes it trivial to relocate the data directory (e.g. for
tests, which use an isolated temp directory instead of the real one).
"""
from __future__ import annotations

import os
from pathlib import Path


class AppPaths:
    """Resolves and creates the directories the application needs.

    By default everything lives under a per-user data directory so the
    app is a good citizen on Windows/macOS/Linux alike, but a test suite
    (or a portable build) can override the root via JOURNAL_APP_DATA_DIR.
    """

    APP_NAME = "PremiumJournal"

    def __init__(self, root_override: str | Path | None = None) -> None:
        if root_override is not None:
            self.root = Path(root_override)
        elif os.environ.get("JOURNAL_APP_DATA_DIR"):
            self.root = Path(os.environ["JOURNAL_APP_DATA_DIR"])
        else:
            self.root = self._default_root()
        self.root.mkdir(parents=True, exist_ok=True)

    def _default_root(self) -> Path:
        if os.name == "nt":
            base = os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
            return Path(base) / self.APP_NAME
        if os.uname().sysname == "Darwin":
            return Path.home() / "Library" / "Application Support" / self.APP_NAME
        # Linux / other unix: XDG data dir, falling back to a local ./data
        xdg = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
        return Path(xdg) / self.APP_NAME

    @property
    def database_path(self) -> Path:
        return self.root / "journal.db"

    @property
    def settings_path(self) -> Path:
        return self.root / "settings.json"

    @property
    def backups_dir(self) -> Path:
        path = self.root / "backups"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def media_dir(self) -> Path:
        path = self.root / "media"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def exports_dir(self) -> Path:
        path = self.root / "exports"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def logs_path(self) -> Path:
        return self.root / "app.log"
