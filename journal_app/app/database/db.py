"""Database bootstrap: engine creation, session management, seeding, and
backup. Nothing in here talks SQL directly outside of the SQLAlchemy ORM,
which keeps the rest of the app database-agnostic in principle.
"""
from __future__ import annotations

import contextlib
import logging
import shutil
import sqlite3
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.config import AppPaths, DEFAULT_TOPICS
from app.models import Base, Topic, User

logger = logging.getLogger(__name__)


class Database:
    """Owns the SQLAlchemy engine + session factory for one data directory.

    A fresh `Database` instance is cheap and test-friendly: point it at a
    temp directory (via AppPaths(root_override=...)) and you get a fully
    isolated SQLite file with no cross-test contamination.
    """

    def __init__(self, paths: AppPaths | None = None) -> None:
        self.paths = paths or AppPaths()
        self.engine = create_engine(
            f"sqlite:///{self.paths.database_path}",
            connect_args={"check_same_thread": False},
            future=True,
        )
        # Enforce foreign keys + a sane journal mode for durability without
        # sacrificing write performance too much.
        event.listen(self.engine, "connect", self._on_connect)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False, future=True)

    @staticmethod
    def _on_connect(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA journal_mode = WAL")
        cursor.execute("PRAGMA synchronous = NORMAL")
        cursor.close()

    def init_db(self) -> None:
        """Create tables (if needed) and seed defaults. Safe to call every
        startup -- it is a no-op on an already-initialized database."""
        Base.metadata.create_all(self.engine)
        with self.session() as session:
            if session.query(User).count() == 0:
                session.add(User(name="You"))
            if session.query(Topic).count() == 0:
                for name, color, icon in DEFAULT_TOPICS:
                    session.add(Topic(name=name, color=color, icon=icon))
            session.commit()

    @contextlib.contextmanager
    def session(self) -> Iterator[Session]:
        """Transactional scope: commits on success, rolls back on error.

        Usage:
            with db.session() as session:
                session.add(obj)
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Database transaction failed; rolled back.")
            raise
        finally:
            session.close()

    def backup_to(self, destination: Path) -> Path:
        """Safely copy the live database using SQLite's own backup API so
        an in-progress write can never produce a corrupt backup file."""
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        source_conn = sqlite3.connect(str(self.paths.database_path))
        dest_conn = sqlite3.connect(str(destination))
        try:
            with dest_conn:
                source_conn.backup(dest_conn)
        finally:
            source_conn.close()
            dest_conn.close()
        return destination

    def database_size_bytes(self) -> int:
        try:
            return self.paths.database_path.stat().st_size
        except FileNotFoundError:
            return 0
