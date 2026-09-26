"""Tests for date grouping/formatting/streak helpers."""
from __future__ import annotations

import datetime as dt

from app.utils.date_utils import (
    compute_streak,
    group_key,
    relative_date_label,
    sort_group_keys,
    word_count,
)


def test_relative_date_label_today_yesterday():
    today = dt.date(2026, 9, 16)
    assert relative_date_label(today, today) == "Today"
    assert relative_date_label(today - dt.timedelta(days=1), today) == "Yesterday"


def test_relative_date_label_within_week_uses_weekday():
    today = dt.date(2026, 9, 16)  # Wednesday
    three_days_ago = today - dt.timedelta(days=3)
    label = relative_date_label(three_days_ago, today)
    assert label == three_days_ago.strftime("%A")


def test_relative_date_label_older_uses_month_day():
    today = dt.date(2026, 9, 16)
    old = dt.date(2026, 1, 5)
    assert relative_date_label(old, today) == "January 5"


def test_group_key_buckets():
    today = dt.date(2026, 9, 16)
    assert group_key(today, today) == "Today"
    assert group_key(today - dt.timedelta(days=1), today) == "Yesterday"
    assert group_key(today - dt.timedelta(days=3), today) == "This Week"
    assert group_key(today - dt.timedelta(days=10), today) == "This Month"
    assert group_key(dt.date(2026, 1, 1), today) == "January"
    assert group_key(dt.date(2024, 1, 1), today) == "2024"


def test_sort_group_keys_orders_recents_first_then_months_then_years():
    keys = ["2024", "This Month", "January", "Today", "March", "Yesterday", "This Week"]
    ordered = sort_group_keys(keys, dt.date(2026, 9, 16))
    assert ordered[:4] == ["Today", "Yesterday", "This Week", "This Month"]
    assert ordered.index("March") < ordered.index("January")
    assert ordered[-1] == "2024"


def test_compute_streak_consecutive_days():
    today = dt.date(2026, 9, 16)
    dates = {today, today - dt.timedelta(days=1), today - dt.timedelta(days=2)}
    assert compute_streak(dates, today) == 3


def test_compute_streak_allows_yesterday_as_anchor():
    today = dt.date(2026, 9, 16)
    dates = {today - dt.timedelta(days=1), today - dt.timedelta(days=2)}
    assert compute_streak(dates, today) == 2


def test_compute_streak_zero_when_gap_before_today():
    today = dt.date(2026, 9, 16)
    dates = {today - dt.timedelta(days=3)}
    assert compute_streak(dates, today) == 0


def test_compute_streak_empty_set():
    assert compute_streak(set()) == 0


def test_word_count():
    assert word_count("") == 0
    assert word_count("   ") == 0
    assert word_count("one two three") == 3
    assert word_count("  extra   spaces   here ") == 3
