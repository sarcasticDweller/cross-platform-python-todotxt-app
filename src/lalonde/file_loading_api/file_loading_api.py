from pathlib import Path


def ensure_file_exists(folder_path: Path, file_name: str) -> Path:
    """Given a folder_path and a file_name, create the file at the folder_path and return the file_path"""
    path = folder_path / file_name
    path.touch(exist_ok=True)
    return path

class UnsupportedStorageVolumeError(TypeError): pass
