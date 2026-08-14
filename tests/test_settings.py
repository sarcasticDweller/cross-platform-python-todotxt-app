import json
from pathlib import Path

import pytest
from kivymd.app import MDApp

from file_loading_api.settings import Settings


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(MDApp, "user_data_dir", str(tmp_path))
    return MDApp()


@pytest.fixture
def settings_file(app):
    return Path(app.user_data_dir) / Settings.SETTINGS_FILE_NAME


# __init__ / file creation

def test_Settings_init_creates_json_file_if_missing(app, settings_file):
    assert not settings_file.exists()
    Settings(app)
    assert settings_file.exists()

def test_Settings_init_loads_existing_content(app, settings_file):
    settings_file.write_text(json.dumps({"theme": "dark"}))
    settings = Settings(app)
    assert settings["theme"] == "dark"


# save_settings

def test_Settings_save_settings_writes_content_to_disk(app, settings_file):
    settings_file.write_text(json.dumps({}))
    settings = Settings(app)
    settings["theme"] = "dark"
    settings.save_settings()
    with open(settings_file) as f:
        assert json.load(f) == {"theme": "dark"}


# dict-like usage

def test_Settings_supports_dict_like_access(app, settings_file):
    settings_file.write_text(json.dumps({}))
    settings = Settings(app)
    settings["theme"] = "dark"
    assert settings["theme"] == "dark"
    assert "theme" in settings
    assert list(settings.keys()) == ["theme"]
    assert len(settings) == 1
