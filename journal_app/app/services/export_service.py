"""Export journals to JSON, plain text, Markdown, or PDF, and back up the
raw SQLite file. Export is entirely local -- nothing here makes a network
call, in keeping with the app's local-first, privacy-first design.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from app.services.dto import JournalDTO

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    _REPORTLAB_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only when reportlab is absent
    _REPORTLAB_AVAILABLE = False


class UnsupportedFormatError(Exception):
    pass


class ExportService:
    SUPPORTED_FORMATS = ("json", "txt", "markdown", "pdf")

    def pdf_available(self) -> bool:
        return _REPORTLAB_AVAILABLE

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #
    def export(self, journals: list[JournalDTO], fmt: str, destination: Path) -> Path:
        fmt = fmt.lower()
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if fmt == "json":
            self._export_json(journals, destination)
        elif fmt == "txt":
            self._export_txt(journals, destination)
        elif fmt == "markdown":
            self._export_markdown(journals, destination)
        elif fmt == "pdf":
            self._export_pdf(journals, destination)
        else:
            raise UnsupportedFormatError(f"Unknown export format: {fmt}")
        return destination

    # ------------------------------------------------------------------ #
    # Format-specific writers
    # ------------------------------------------------------------------ #
    def _export_json(self, journals: list[JournalDTO], destination: Path) -> None:
        payload = [
            {
                "id": j.id,
                "title": j.title,
                "content": j.content,
                "date": j.journal_date.isoformat(),
                "created_at": j.created_at.isoformat(),
                "updated_at": j.updated_at.isoformat(),
                "topic": j.topic.name if j.topic else None,
                "mood": j.mood,
                "tags": j.tags,
                "is_favorite": j.is_favorite,
                "word_count": j.word_count,
            }
            for j in journals
        ]
        destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def _export_txt(self, journals: list[JournalDTO], destination: Path) -> None:
        blocks = []
        for j in journals:
            header = f"{j.journal_date.strftime('%B %d, %Y')} — {j.title or 'Untitled'}"
            meta_bits = []
            if j.topic:
                meta_bits.append(f"Topic: {j.topic.name}")
            if j.mood:
                meta_bits.append(f"Mood: {j.mood}")
            if j.tags:
                meta_bits.append("Tags: " + ", ".join(f"#{t}" for t in j.tags))
            meta = " | ".join(meta_bits)
            block = header + ("\n" + meta if meta else "") + "\n\n" + j.content.strip()
            blocks.append(block)
        destination.write_text(("\n\n" + "-" * 40 + "\n\n").join(blocks), encoding="utf-8")

    def _export_markdown(self, journals: list[JournalDTO], destination: Path) -> None:
        lines: list[str] = []
        for j in journals:
            lines.append(f"## {j.journal_date.strftime('%B %d, %Y')} — {j.title or 'Untitled'}")
            lines.append("")
            meta_bits = []
            if j.topic:
                meta_bits.append(f"**Topic:** {j.topic.name}")
            if j.mood:
                meta_bits.append(f"**Mood:** {j.mood}")
            if j.is_favorite:
                meta_bits.append("**\u2605 Favorite**")
            if meta_bits:
                lines.append(" &nbsp;\u00b7&nbsp; ".join(meta_bits))
                lines.append("")
            lines.append(j.content.strip())
            if j.tags:
                lines.append("")
                lines.append(" ".join(f"`#{t}`" for t in j.tags))
            lines.append("")
            lines.append("---")
            lines.append("")
        destination.write_text("\n".join(lines), encoding="utf-8")

    def _export_pdf(self, journals: list[JournalDTO], destination: Path) -> None:
        if not _REPORTLAB_AVAILABLE:
            raise RuntimeError(
                "PDF export requires the 'reportlab' package. Install it with "
                "'pip install reportlab' and try again."
            )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "JournalTitle", parent=styles["Heading2"], spaceAfter=4, textColor="#2E2A24"
        )
        meta_style = ParagraphStyle(
            "JournalMeta", parent=styles["Normal"], textColor="#8A8578", fontSize=9, spaceAfter=10
        )
        body_style = ParagraphStyle(
            "JournalBody", parent=styles["Normal"], fontSize=11, leading=16, spaceAfter=16
        )

        doc = SimpleDocTemplate(
            str(destination),
            pagesize=LETTER,
            leftMargin=0.9 * inch,
            rightMargin=0.9 * inch,
            topMargin=0.9 * inch,
            bottomMargin=0.9 * inch,
            title="Journal Export",
        )
        story = []
        for j in journals:
            story.append(Paragraph(_escape(j.title or "Untitled"), title_style))
            meta_bits = [j.journal_date.strftime("%B %d, %Y")]
            if j.topic:
                meta_bits.append(j.topic.name)
            if j.mood:
                meta_bits.append(j.mood)
            if j.tags:
                meta_bits.append(", ".join(f"#{t}" for t in j.tags))
            story.append(Paragraph(_escape(" \u00b7 ".join(meta_bits)), meta_style))
            for paragraph in j.content.split("\n\n"):
                if paragraph.strip():
                    story.append(Paragraph(_escape(paragraph).replace("\n", "<br/>"), body_style))
            story.append(Spacer(1, 18))
        doc.build(story)


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
