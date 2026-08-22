from pathlib import Path

MANIFEST = Path("src/main/AndroidManifest.xml")  # relative to the dist dir p4a cd's into

RECEIVER = """
        <receiver android:name=".AlarmBootReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
                <action android:name="android.app.action.SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED" />
            </intent-filter>
        </receiver>
"""


def before_apk_assemble(toolchain):
    manifest = MANIFEST.read_text()
    if "AlarmBootReceiver" in manifest:
        print("[p4a_hook] receiver already present")
        return
    MANIFEST.write_text(manifest.replace("</application>", RECEIVER + "    </application>"))
    print("[p4a_hook] inserted AlarmBootReceiver into the manifest")
