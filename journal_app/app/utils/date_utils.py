"""Date grouping and formatting helpers used by the dashboard, journal
list, and calendar views."""
from __future__ import annotations

import datetime as dt


def relative_date_label(date: dt.date, today: dt.date | None = None) -> str:
    """Human-friendly label: 'Today', 'Yesterday', a weekday name if within
    the last week, otherwise 'Month Day' (+ year if not this year)."""
    today = today or dt.date.today()
    delta = (today - date).days
    if delta == 0:
        return "Today"
    if delta == 1:
        return "Yesterday"
    if 0 < delta < 7:
        return date.strftime("%A")
    if date.year == today.year:
        return date.strftime("%B %-d") if hasattr(date, "strftime") else str(date)
    return date.strftime("%B %-d, %Y")


def group_key(date: dt.date, today: dt.date | None = None) -> str:
    """Bucket a date into one of the sections the journal list groups by."""
    today = today or dt.date.today()
    delta = (today - date).days
    if delta == 0:
        return "Today"
    if delta == 1:
        return "Yesterday"
    if 0 < delta < 7:
        return "This Week"
    if date.year == today.year and date.month == today.month:
        return "This Month"
    if date.year == today.year:
        return date.strftime("%B")
    return date.strftime("%Y")


GROUP_ORDER = ["Today", "Yesterday", "This Week", "This Month"]


def sort_group_keys(keys: list[str], today: dt.date | None = None) -> list[str]:
    """Order section headers sensibly: the fixed recents first, then
    month/year buckets from most to least recent."""
    today = today or dt.date.today()
    fixed = [k for k in GROUP_ORDER if k in keys]
    remaining = [k for k in keys if k not in GROUP_ORDER]

    def sort_key(label: str):
        # Try "Month" (this year) first, then a bare "Year".
        for fmt in ("%B", "%Y"):
            try:
                parsed = dt.datetime.strptime(label, fmt)
                if fmt == "%B":
                    return (0, -parsed.month)
                return (1, -parsed.year)
            except ValueError:
                continue
        return (2, label)

    remaining.sort(key=sort_key)
    return fixed + remaining


def compute_streak(journal_dates: set[dt.date], today: dt.date | None = None) -> int:
    """Consecutive-day streak ending today or yesterday (writing today is
    not required to keep yesterday's streak alive until the day ends)."""
    today = today or dt.date.today()
    if not journal_dates:
        return 0
    anchor = today if today in journal_dates else today - dt.timedelta(days=1)
    if anchor not in journal_dates:
        return 0
    streak = 0
    cursor = anchor
    while cursor in journal_dates:
        streak += 1
        cursor -= dt.timedelta(days=1)
    return streak


def word_count(text: str) -> int:
    return len(text.split()) if text and text.strip() else 0
