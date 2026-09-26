"""A small shared helper for clearing dynamically-populated layouts.

Calling deleteLater() alone is not enough: the widget stays a visible
child of its parent (at its last-painted geometry) until Qt processes
the deferred deletion on a later event-loop iteration, which can cause
a brief "ghost" of stale content. Detaching it immediately via
setParent(None) avoids that.
"""
from __future__ import annotations

from PySide6.QtWidgets import QLayout


def clear_layout(layout: QLayout, keep_last: int = 0) -> None:
    """Remove and dispose of every item in `layout`, except the last
    `keep_last` items (used e.g. to keep a trailing 'add' button)."""
    while layout.count() > keep_last:
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())
