"""Tests for the database bootstrap layer: init, seeding, backup, size."""
from __future__ import annotations

from app.models import Topic, User


def test_init_db_creates_tables_and_seeds_defaults(db):
    with db.session() as session:
        assert session.query(User).count() == 1
        topics = session.query(Topic).all()
        assert len(topics) == 8
        names = {t.name for t in topics}
        assert "Personal" in names
        assert "Travel" in names


def test_init_db_is_idempotent(db):
    db.init_db()
    db.init_db()
    with db.session() as session:
        assert session.query(User).count() == 1
        assert session.query(Topic).count() == 8


def test_backup_creates_valid_copy(db, tmp_path):
    dest = tmp_path / "backup.db"
    result = db.backup_to(dest)
    assert result.exists()
    assert result.stat().st_size > 0

    # The backup should be a fully independent, readable SQLite file.
    import sqlite3

    conn = sqlite3.connect(str(dest))
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM topics")
        assert cursor.fetchone()[0] == 8
    finally:
        conn.close()


def test_database_size_bytes_reflects_real_file(db):
    assert db.database_size_bytes() > 0


def test_transaction_rolls_back_on_error(db):
    with db.session() as session:
        session.add(Topic(name="Rollback Test", color="#000000", icon="X"))

    with db.session() as session:
        assert session.query(Topic).filter(Topic.name == "Rollback Test").count() == 1

    try:
        with db.session() as session:
            session.add(Topic(name="Will Fail", color="#000000", icon="X"))
            raise RuntimeError("boom")
    except RuntimeError:
        pass

    with db.session() as session:
        assert session.query(Topic).filter(Topic.name == "Will Fail").count() == 0
