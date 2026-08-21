from pathlib import Path
from urllib.parse import unquote

import android
from android import activity
from jnius import autoclass

from file_loading_api.file_loading_api import UnsupportedStorageVolumeError

ANDROID_FOLDER_ROOT = "/storage/emulated/0"
REQUEST_CODE = 42  # arbitrary, just needs to be unique

def android_uri_to_path(uri: android.net.Uri) -> Path:
    volume, _, subpath = unquote(uri.toString()).split("/tree/")[1].partition(":")
    if volume != "primary":
        raise UnsupportedStorageVolumeError("Expected to be on the primary volume")

    return Path(ANDROID_FOLDER_ROOT) / subpath

def launch_android_folder_picker(on_folder_picked):
    """Mostly vibe-coded tool to get a folder and persistent read/write permission to said folder.
    `on_folder_picked` expects a function that accepts a Path as an argument
    """
    Intent = autoclass("android.content.Intent")
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    current_activity = PythonActivity.mActivity

    def on_activity_result(request_code, result_code, intent):
        if request_code != REQUEST_CODE:
            #return
            # actually, id like to see this break here
            raise ValueError(f"Expected request code {REQUEST_CODE}, got {request_code}")
        uri = intent.getData()
        take_flags = intent.getFlags() & (
            Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
        )
        current_activity.getContentResolver().takePersistableUriPermission(uri, take_flags)

        resolved_path = android_uri_to_path(uri) # if err: crash for now
        on_folder_picked(resolved_path)

    activity.bind(on_activity_result=on_activity_result) # allgedly problematic if ran repeatedely
    intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
    current_activity.startActivityForResult(intent, REQUEST_CODE)
