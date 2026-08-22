import json
from pathlib import Path

import pytest

from files.settings import Settings


@pytest.fixture
def user_data_dir(tmp_path) -> Path:
    return tmp_path


@pytest.fixture
def settings_file(user_data_dir) -> Path:
    return user_data_dir / Settings.SETTINGS_FILE_NAME


# __init__ / file creation

def test_Settings_init_creates_json_file_if_missing(user_data_dir, settings_file):
    assert not settings_file.exists()
    Settings(user_data_dir)
    assert settings_file.exists()

def test_Settings_init_loads_existing_content(user_data_dir, settings_file):
    settings_file.write_text(json.dumps({"theme": "dark"}))
    settings = Settings(user_data_dir)
    assert settings["theme"] == "dark"

def test_Settings_init_accepts_a_str_path(user_data_dir, settings_file):
    settings_file.write_text(json.dumps({"theme": "dark"}))
    settings = Settings(str(user_data_dir))
    assert settings["theme"] == "dark"

def test_Settings_init_falls_back_to_defaults_when_file_is_empty(user_data_dir):
    settings = Settings(user_data_dir)
    assert settings["todo_file_name"] == "todo.txt"


# save_settings

def test_Settings_save_settings_writes_content_to_disk(user_data_dir, settings_file):
    settings_file.write_text(json.dumps({}))
    settings = Settings(user_data_dir)
    settings["theme"] = "dark"
    settings.save_settings()
    with open(settings_file) as f:
        assert json.load(f) == {"theme": "dark"}

def test_Settings_save_settings_round_trips(user_data_dir):
    settings = Settings(user_data_dir)
    settings["todo_dir"] = "/somewhere/else"
    settings.save_settings()
    assert Settings(user_data_dir)["todo_dir"] == "/somewhere/else"


# dict-like usage

def test_Settings_supports_dict_like_access(user_data_dir, settings_file):
    settings_file.write_text(json.dumps({}))
    settings = Settings(user_data_dir)
    settings["theme"] = "dark"
    assert settings["theme"] == "dark"
    assert "theme" in settings
    assert list(settings.keys()) == ["theme"]
    assert len(settings) == 1
