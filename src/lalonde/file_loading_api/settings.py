import json
from collections import UserDict
from json.decoder import JSONDecodeError
from pathlib import Path

from kivymd.app import MDApp

from file_loading_api.file_loading_api import ensure_file_exists

DEFAULT_SETTINGS = {
    "theme_style": "Light",
    "material_style": "M3",
    "todo_file_name": "todo.txt",
    "user_data_dir": ""
}

class AppHasNoNameError(ValueError): pass

class Settings(UserDict):
    SETTINGS_FILE_NAME = "settings.json"
    def __init__(self, app: MDApp):
        """Uses `app` to extrapolate the system's filepath. Note that"""
        if not app.name:
            raise AppHasNoNameError("App needs a name in order to load settings. Please define and pass an app class that inherits Kivy(MD).app.(MD)App")
            # Because files live in `$system_appdata_folder/$app_name/`,  apps without a name don't get assigned a folder.

        self._file_path = ensure_file_exists(Path(app.user_data_dir), self.SETTINGS_FILE_NAME)
        with open(self._file_path, "r") as json_file:
            try:
                super().__init__(json.load(json_file))
            except JSONDecodeError: # if empty, initialize an empty dict
                super().__init__(DEFAULT_SETTINGS)

    def save_settings(self):
        with open(self._file_path, "w") as json_file:
            json.dump(dict(self), json_file)
