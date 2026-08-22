import json
from collections import UserDict
from json.decoder import JSONDecodeError
from pathlib import Path

from files.helpers import ensure_file_exists

DEFAULT_SETTINGS = {
    "theme_style": "Light",
    "material_style": "M3",
    "todo_file_name": "todo.txt",
    "todo_dir": "" # Has to be set by user
}

class Settings(UserDict):
    SETTINGS_FILE_NAME = "settings.json"
    def __init__(self, user_data_dir: Path):
        """Uses `app` to extrapolate the system's filepath.
        
        Args:
            `user_data_dir`: The folder where the settings file lives.
        """

        self._file_path = ensure_file_exists(Path(user_data_dir), self.SETTINGS_FILE_NAME)
        with open(self._file_path, "r") as json_file:
            try:
                super().__init__(json.load(json_file))
            except JSONDecodeError: # if empty, initialize an empty dict
                super().__init__(DEFAULT_SETTINGS)

    def save_settings(self):
        with open(self._file_path, "w") as json_file:
            json.dump(dict(self), json_file)
