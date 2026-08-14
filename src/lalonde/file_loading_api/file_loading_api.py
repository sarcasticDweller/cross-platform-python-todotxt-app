from pathlib import Path


class UnsupportedStorageVolumeError(ValueError): pass

def ensure_file_exists(folder_path: Path, file_name: str) -> Path:
    """Given a folder_path and a file_name, create the file at the folder_path and return the file_path"""
    path = folder_path / file_name
    path.touch(exist_ok=True)
    return path

def launch_folder_picker(platform_name: str, on_folder_picked):
    """
    `on_folder_picked` expects a function that accepts a Path as an argument
    """
    match platform_name:
        case "android":
            from file_loading_api.android import launch_android_folder_picker
            # importing indiscriminately would cause the app to crash on any platform that isnt android
            launch_android_folder_picker(on_folder_picked)
        case _:
            raise NotImplementedError("The only supported platform is Android.")
