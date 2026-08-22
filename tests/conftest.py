"""Shared pytest fixtures that isolate storage from the developer workspace."""

from __future__ import annotations

import pytest

from config.settings import get_settings


@pytest.fixture
def isolated_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    get_settings.cache_clear()
    settings = get_settings()
    yield settings
    get_settings.cache_clear()
