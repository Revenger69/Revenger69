"""Tests for SettingsService: persistence, defaults, clamping, corruption
recovery."""
from __future__ import annotations

from app.services.settings_service import AppSettings, SettingsService


def test_load_creates_defaults_when_missing(settings_service):
    settings = settings_service.load()
    assert settings.theme == "light"
    assert settings.journal_font_size == 16
    assert settings_service.paths.settings_path.exists()


def test_update_persists_changes(paths):
    service = SettingsService(paths)
    service.update(theme="dark", journal_font_size=20)

    reloaded = SettingsService(paths)
    settings = reloaded.load()
    assert settings.theme == "dark"
    assert settings.journal_font_size == 20


def test_clamp_keeps_values_in_safe_bounds():
    settings = AppSettings(journal_font_size=999, line_spacing=50.0, ui_font_size=1, theme="neon")
    clamped = settings.clamp()
    assert clamped.journal_font_size == 28
    assert clamped.line_spacing == 2.2
    assert clamped.ui_font_size == 8
    assert clamped.theme == "light"


def test_load_recovers_from_corrupt_settings_file(paths):
    paths.settings_path.write_text("{not valid json", encoding="utf-8")
    service = SettingsService(paths)
    settings = service.load()
    assert settings.theme == "light"  # falls back to defaults, doesn't crash


def test_load_ignores_unknown_fields(paths):
    import json

    paths.settings_path.write_text(
        json.dumps({"theme": "dark", "some_future_field": "ignored"}), encoding="utf-8"
    )
    service = SettingsService(paths)
    settings = service.load()
    assert settings.theme == "dark"
