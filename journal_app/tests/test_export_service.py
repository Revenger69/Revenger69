"""Tests for ExportService: JSON/TXT/Markdown/PDF output."""
from __future__ import annotations

import json

from app.services.dto import JournalDTO, TopicDTO
import datetime as dt


def _sample_journals():
    topic = TopicDTO(id=1, name="Travel", color="#4F9D9D", icon="\u2708")
    return [
        JournalDTO(
            id=1, title="A Quiet Evening", content="Line one.\n\nLine two about mountains.",
            created_at=dt.datetime(2026, 9, 1, 20, 30), updated_at=dt.datetime(2026, 9, 1, 20, 30),
            journal_date=dt.date(2026, 9, 1), topic=topic, mood="calm", is_favorite=True,
            word_count=6, tags=["nepal", "memories"],
        )
    ]


def test_export_json_round_trips_core_fields(export_service, tmp_path):
    dest = tmp_path / "out.json"
    export_service.export(_sample_journals(), "json", dest)
    data = json.loads(dest.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["title"] == "A Quiet Evening"
    assert data[0]["topic"] == "Travel"
    assert data[0]["tags"] == ["nepal", "memories"]
    assert data[0]["is_favorite"] is True


def test_export_txt_contains_readable_content(export_service, tmp_path):
    dest = tmp_path / "out.txt"
    export_service.export(_sample_journals(), "txt", dest)
    text = dest.read_text(encoding="utf-8")
    assert "A Quiet Evening" in text
    assert "mountains" in text
    assert "Travel" in text


def test_export_markdown_uses_headers_and_tags(export_service, tmp_path):
    dest = tmp_path / "out.md"
    export_service.export(_sample_journals(), "markdown", dest)
    text = dest.read_text(encoding="utf-8")
    assert text.startswith("## ")
    assert "`#nepal`" in text
    assert "**Topic:** Travel" in text


def test_export_pdf_produces_nonempty_file(export_service, tmp_path):
    if not export_service.pdf_available():
        return  # reportlab not installed in this environment; skip gracefully
    dest = tmp_path / "out.pdf"
    export_service.export(_sample_journals(), "pdf", dest)
    assert dest.exists()
    assert dest.stat().st_size > 200
    assert dest.read_bytes()[:4] == b"%PDF"


def test_export_unsupported_format_raises(export_service, tmp_path):
    from app.services.export_service import UnsupportedFormatError
    import pytest

    with pytest.raises(UnsupportedFormatError):
        export_service.export(_sample_journals(), "docx", tmp_path / "out.docx")


def test_export_creates_parent_directories(export_service, tmp_path):
    dest = tmp_path / "nested" / "dir" / "out.json"
    export_service.export(_sample_journals(), "json", dest)
    assert dest.exists()
