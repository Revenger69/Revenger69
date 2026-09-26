"""A single place for 'current time' so we can avoid the deprecated
datetime.utcnow() while still storing naive UTC datetimes (which is what
the rest of the schema/comparisons assume)."""
from __future__ import annotations

import datetime as dt


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
