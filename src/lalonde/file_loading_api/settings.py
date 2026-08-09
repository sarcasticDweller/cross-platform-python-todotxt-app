import json
from collections import UserDict
from json.decoder import JSONDecodeError
from pathlib import Path

from kivymd.app import MDApp

DEFAULT_SETTINGS = {
    "theme_style": "Light",
    "material_style": "M3",
    "todo_file": "tmp_todo.txt" # stopgap until the file picker is figured out
}

class Settings(UserDict):
    SETTINGS_FILE_NAME = "settings.json"
    def __init__(self, app: MDApp):
        """Uses `app` to extrapolate the system's filepath. Note that"""
        if not app.name:
            raise ValueError("App needs a name in order to load settings. Please define and pass an app class that inherits Kivy(MD).app.(MD)App")
            # Because files live in `$system_appdata_folder/$app_name/`,  apps without a name don't get assigned a folder.

        self._file_path = Path(app.user_data_dir) / self.SETTINGS_FILE_NAME # read app.user_data_dir docstring to find settings.json
        self._file_path.touch(exist_ok=True)
        with open(self._file_path, "r") as json_file:
            try:
                super().__init__(json.load(json_file))
            except JSONDecodeError: # if empty, initialize an empty dict
                super().__init__(DEFAULT_SETTINGS)

    def save_settings(self):
        with open(self._file_path, "w") as json_file:
            json.dump(dict(self), json_file)
