try:
    from files import android_lib as android  # noqa: F401
except ModuleNotFoundError:
    # android isn't present on non-android systems, so skip it
    pass
from files.helpers import UnsupportedStorageVolumeError, ensure_file_exists
from files.settings import Settings

__all__ = [
    "Settings",
    "UnsupportedStorageVolumeError",
    "ensure_file_exists"
]
