"""Entry point: `python main.py` launches the Premium Journal desktop app.

Sets up logging (to a local file, never logging journal content itself),
installs a friendly top-level exception handler so a bug never shows the
user a raw Python traceback, then boots the Qt application.
"""
from __future__ import annotations

import logging
import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from app.config import APP_TITLE, AppPaths


def _configure_logging(paths: AppPaths) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(paths.logs_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    # Keep SQL statement logging off by default -- journal content can
    # appear in bound parameters, and this must never land in a log file.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def _install_exception_hook() -> None:
    logger = logging.getLogger("uncaught")

    def handle(exc_type, exc_value, exc_tb) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        logger.error("Unhandled exception:\n%s", "".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
        app = QApplication.instance()
        if app is not None:
            QMessageBox.critical(
                None,
                APP_TITLE,
                "Something went wrong, but your journal data is safe.\n\n"
                "Please try again. If the problem continues, check the log file "
                "in your app data folder for details.",
            )

    sys.excepthook = handle


def main() -> int:
    paths = AppPaths()
    _configure_logging(paths)
    _install_exception_hook()

    app = QApplication(sys.argv)
    app.setApplicationName(AppPaths.APP_NAME)
    app.setOrganizationName(AppPaths.APP_NAME)
    app.setApplicationDisplayName(APP_TITLE)

    # Imported here (after QApplication exists) since font resolution and
    # some Qt widgets require a running QApplication instance.
    from app.ui.context import AppContext
    from app.ui.main_window import MainWindow
    from app.ui.styles import ThemeManager, build_stylesheet

    context = AppContext(paths)
    app.setStyleSheet(build_stylesheet(ThemeManager.get(context.settings.theme)))

    window = MainWindow(context)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
