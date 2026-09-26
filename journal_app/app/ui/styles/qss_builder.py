"""Builds the application-wide Qt stylesheet (QSS) from a Theme's color
tokens. Widgets opt into specific rules via objectName (e.g. "Sidebar",
"PrimaryButton", "JournalCard") rather than subclassing styles per widget,
which keeps the visual language centralized and consistent.
"""
from __future__ import annotations

from app.ui.styles.fonts import FontResolver
from app.ui.styles.theme import Theme


def build_stylesheet(theme: Theme) -> str:
    ui_font = FontResolver.ui_family()
    t = theme
    return f"""
    /* ---------- Base ---------- */
    * {{
        font-family: "{ui_font}";
        outline: none;
    }}
    QMainWindow, QWidget#CentralArea {{
        background: {t.bg_primary};
    }}
    QWidget {{
        color: {t.text_primary};
    }}
    QLabel {{
        background: transparent;
    }}
    QToolTip {{
        background: {t.bg_elevated};
        color: {t.text_primary};
        border: 1px solid {t.border};
        border-radius: 6px;
        padding: 6px 8px;
    }}

    /* ---------- Sidebar & navigation ---------- */
    QWidget#Sidebar {{
        background: {t.bg_secondary};
        border-right: 1px solid {t.border};
    }}
    QLabel#AppTitle {{
        color: {t.text_primary};
        font-size: 16px;
        font-weight: 700;
        padding: 4px 2px;
    }}
    QLabel#AppSubtitle {{
        color: {t.text_tertiary};
        font-size: 11px;
    }}
    QPushButton#NavButton {{
        text-align: left;
        padding: 10px 12px;
        border: none;
        border-radius: 10px;
        background: transparent;
        color: {t.text_secondary};
        font-size: 13px;
        font-weight: 500;
    }}
    QPushButton#NavButton:hover {{
        background: {t.bg_hover};
        color: {t.text_primary};
    }}
    QPushButton#NavButton:checked {{
        background: {t.bg_selected};
        color: {t.text_primary};
        font-weight: 700;
    }}
    QPushButton#NewJournalButton {{
        background: {t.accent};
        color: {t.text_on_accent};
        border: none;
        border-radius: 12px;
        padding: 12px 14px;
        font-size: 13px;
        font-weight: 700;
        text-align: center;
    }}
    QPushButton#NewJournalButton:hover {{
        background: {t.accent_hover};
    }}
    QPushButton#NewJournalButton:pressed {{
        background: {t.accent_hover};
        padding-top: 13px;
    }}

    /* ---------- Buttons ---------- */
    QPushButton {{
        font-size: 13px;
    }}
    QPushButton#PrimaryButton {{
        background: {t.accent};
        color: {t.text_on_accent};
        border: none;
        border-radius: 9px;
        padding: 9px 18px;
        font-weight: 600;
    }}
    QPushButton#PrimaryButton:hover {{ background: {t.accent_hover}; }}
    QPushButton#PrimaryButton:disabled {{ background: {t.border}; color: {t.text_tertiary}; }}

    QPushButton#SecondaryButton {{
        background: transparent;
        color: {t.text_primary};
        border: 1px solid {t.border};
        border-radius: 9px;
        padding: 8px 16px;
        font-weight: 500;
    }}
    QPushButton#SecondaryButton:hover {{ background: {t.bg_hover}; }}

    QPushButton#DangerButton {{
        background: transparent;
        color: {t.danger};
        border: 1px solid {t.danger};
        border-radius: 9px;
        padding: 8px 16px;
        font-weight: 500;
    }}
    QPushButton#DangerButton:hover {{ background: {t.danger}; color: {t.text_on_accent}; }}

    QPushButton#IconButton {{
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 4px;
        font-size: 15px;
        color: {t.text_secondary};
    }}
    QPushButton#IconButton:hover {{ background: {t.bg_hover}; color: {t.text_primary}; }}
    QPushButton#IconButton:checked {{ color: {t.accent_warm}; }}

    /* ---------- Inputs ---------- */
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDateEdit {{
        background: {t.bg_elevated};
        color: {t.text_primary};
        border: 1px solid {t.border};
        border-radius: 9px;
        padding: 7px 10px;
        selection-background-color: {t.accent};
        selection-color: {t.text_on_accent};
    }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border: 1px solid {t.accent};
    }}
    QComboBox::drop-down {{ border: none; width: 22px; }}
    QComboBox QAbstractItemView {{
        background: {t.bg_elevated};
        color: {t.text_primary};
        border: 1px solid {t.border};
        selection-background-color: {t.bg_selected};
        outline: none;
    }}

    QLineEdit#SearchBar {{
        border-radius: 16px;
        padding: 8px 14px;
        background: {t.bg_secondary};
        border: 1px solid {t.border_subtle};
    }}

    QLineEdit#TitleInput {{
        border: none;
        background: transparent;
        font-size: 26px;
        font-weight: 700;
        padding: 4px 0;
    }}
    QLineEdit#TitleInput:focus {{ border: none; }}

    QTextEdit#ContentEditor {{
        border: none;
        background: transparent;
        padding: 6px 0;
    }}

    /* ---------- Cards ---------- */
    QFrame#Card {{
        background: {t.bg_elevated};
        border: 1px solid {t.border_subtle};
        border-radius: 14px;
    }}
    QFrame#Card:hover {{
        border: 1px solid {t.border};
    }}
    QLabel#CardDate {{
        color: {t.text_tertiary};
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    QLabel#CardTitle {{
        color: {t.text_primary};
        font-size: 15px;
        font-weight: 700;
    }}
    QLabel#CardPreview {{
        color: {t.text_secondary};
        font-size: 12px;
    }}

    QFrame#Badge {{
        border-radius: 9px;
        padding: 2px 4px;
    }}
    QLabel#BadgeLabel {{
        font-size: 11px;
        font-weight: 600;
    }}

    QFrame#TagChip {{
        background: {t.bg_secondary};
        border: 1px solid {t.border_subtle};
        border-radius: 10px;
    }}
    QLabel#TagChipLabel {{
        color: {t.text_secondary};
        font-size: 11px;
    }}

    /* ---------- Section / group headers ---------- */
    QLabel#SectionHeader {{
        color: {t.text_tertiary};
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        padding-top: 8px;
    }}
    QLabel#PageTitle {{
        color: {t.text_primary};
        font-size: 22px;
        font-weight: 700;
    }}
    QLabel#PageSubtitle {{
        color: {t.text_secondary};
        font-size: 13px;
    }}

    /* ---------- Status / meta labels ---------- */
    QLabel#StatusLabel {{
        color: {t.text_tertiary};
        font-size: 11px;
    }}
    QLabel#MutedLabel {{
        color: {t.text_tertiary};
        font-size: 12px;
    }}

    /* ---------- Toast ---------- */
    QFrame#Toast {{
        background: {t.text_primary};
        border-radius: 10px;
    }}
    QLabel#ToastLabel {{
        color: {t.bg_primary};
        font-size: 12px;
        font-weight: 600;
    }}

    /* ---------- Empty states ---------- */
    QLabel#EmptyStateIcon {{ font-size: 40px; }}
    QLabel#EmptyStateTitle {{
        color: {t.text_primary};
        font-size: 16px;
        font-weight: 700;
    }}
    QLabel#EmptyStateSubtitle {{
        color: {t.text_tertiary};
        font-size: 12px;
    }}

    /* ---------- Mood selector ---------- */
    QPushButton#MoodButton {{
        background: {t.bg_elevated};
        border: 1px solid {t.border_subtle};
        border-radius: 12px;
        font-size: 18px;
        padding: 6px;
    }}
    QPushButton#MoodButton:checked {{
        background: {t.bg_selected};
        border: 1px solid {t.accent};
    }}
    QPushButton#MoodButton:hover {{ border: 1px solid {t.border}; }}

    /* ---------- Scroll areas ---------- */
    QScrollArea {{ border: none; background: transparent; }}
    QScrollArea > QWidget > QWidget {{ background: transparent; }}
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {t.border};
        border-radius: 5px;
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {t.text_tertiary}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar:horizontal {{ height: 0px; }}

    /* ---------- Calendar ---------- */
    QCalendarWidget {{
        background: {t.bg_elevated};
        border: 1px solid {t.border_subtle};
        border-radius: 14px;
    }}
    QCalendarWidget QToolButton {{
        background: transparent;
        color: {t.text_primary};
        font-weight: 700;
        font-size: 13px;
        border-radius: 8px;
        padding: 4px 8px;
    }}
    QCalendarWidget QToolButton:hover {{ background: {t.bg_hover}; }}
    QCalendarWidget QMenu {{ background: {t.bg_elevated}; color: {t.text_primary}; }}
    QCalendarWidget QSpinBox {{
        background: {t.bg_elevated};
        color: {t.text_primary};
        border: 1px solid {t.border};
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background: {t.bg_secondary};
        border-top-left-radius: 14px;
        border-top-right-radius: 14px;
    }}
    QCalendarWidget QAbstractItemView:enabled {{
        background: {t.bg_elevated};
        color: {t.text_primary};
        selection-background-color: {t.accent};
        selection-color: {t.text_on_accent};
        outline: none;
    }}
    QCalendarWidget QAbstractItemView:disabled {{ color: {t.text_tertiary}; }}

    /* ---------- Sliders ---------- */
    QSlider::groove:horizontal {{
        height: 4px;
        background: {t.border};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {t.accent};
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }}
    QSlider::sub-page:horizontal {{
        background: {t.accent};
        border-radius: 2px;
    }}

    /* ---------- Checkboxes ---------- */
    QCheckBox {{ spacing: 8px; font-size: 13px; }}
    QCheckBox::indicator {{
        width: 16px; height: 16px;
        border-radius: 4px;
        border: 1px solid {t.border};
        background: {t.bg_elevated};
    }}
    QCheckBox::indicator:checked {{
        background: {t.accent};
        border: 1px solid {t.accent};
    }}

    /* ---------- Dialogs ---------- */
    QDialog {{ background: {t.bg_primary}; }}

    /* ---------- Splitter ---------- */
    QSplitter::handle {{ background: {t.border_subtle}; }}
    """
