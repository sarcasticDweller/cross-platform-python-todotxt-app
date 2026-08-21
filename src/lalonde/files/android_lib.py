from pathlib import Path
from urllib.parse import unquote

from android import activity
from jnius import autoclass

from files import UnsupportedStorageVolumeError

ANDROID_FOLDER_ROOT = "/storage/emulated/0"
REQUEST_CODE = 42  # arbitrary, just needs to be unique


# Warning: Pure vibes below this point


def has_storage_permission() -> bool:
    """Whether this app currently holds the MANAGE_EXTERNAL_STORAGE ("All files access") permission."""
    Environment = autoclass("android.os.Environment")
    return Environment.isExternalStorageManager()


def request_storage_permission():
    """Sends the user to the system settings screen to grant "All files access".

    Unlike a normal runtime permission request, there's no result callback for this --
    the caller is expected to re-check `has_storage_permission()` on `on_resume`.
    """
    Intent = autoclass("android.content.Intent")
    Settings = autoclass("android.provider.Settings")
    Uri = autoclass("android.net.Uri")
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    current_activity = PythonActivity.mActivity

    intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
    intent.setData(Uri.parse(f"package:{current_activity.getPackageName()}"))
    current_activity.startActivity(intent)


def _uri_to_path(uri) -> Path:
    volume, _, subpath = unquote(uri.toString()).split("/tree/")[1].partition(":")
    if volume != "primary":
        raise UnsupportedStorageVolumeError("Expected to be on the primary volume")
    return Path(ANDROID_FOLDER_ROOT) / subpath


def launch_folder_picker(on_folder_picked):
    """Uses the native document-tree picker purely for its UI -- actual file
    access comes from MANAGE_EXTERNAL_STORAGE, not from this intent's URI grant.
    """
    Intent = autoclass("android.content.Intent")
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    current_activity = PythonActivity.mActivity

    def on_activity_result(request_code, result_code, intent):
        if request_code != REQUEST_CODE:
            raise ValueError(f"Expected request code {REQUEST_CODE}, got {request_code}")
        on_folder_picked(_uri_to_path(intent.getData()))

    activity.bind(on_activity_result=on_activity_result)
    intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
    current_activity.startActivityForResult(intent, REQUEST_CODE)
