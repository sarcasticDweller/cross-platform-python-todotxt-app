"""Android notification backend for alarms.

Android-only by design: `jnius` doesn't exist off-device, so *importing* this
module on desktop raises ModuleNotFoundError. That's intentional -- the platform
check belongs at the call site, not as a guard clause in every function here.

Requires minapi >= 26. NotificationChannel and the two-argument
Notification.Builder constructor were both added in API 26; on 24/25 they don't
exist and these calls throw.
"""

from jnius import autoclass, cast

# Bumping the suffix is the ONLY way to change a channel's importance, sound, or
# vibration on a device where it already exists -- Android freezes those at
# creation and silently ignores later changes.
CHANNEL_ID = "lalonde_alarms_v1"
CHANNEL_NAME = "Task alarms"

NOTIFICATION_ID = 1001 # must not be 1; causes a collision with p4a's ServiceAlarm.getServiceID()


def _get_context():
    """The Context for whichever process we're in.

    The app and the alarm service are separate OS processes with separate
    entrypoints, and each exposes its own Context: `mActivity` is null in the
    service, `mService` is null in the app.
    """
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    if PythonActivity.mActivity is not None:
        return PythonActivity.mActivity

    PythonService = autoclass("org.kivy.android.PythonService")
    return PythonService.mService


def _get_notification_manager(context):
    Context = autoclass("android.content.Context")
    return cast(
        "android.app.NotificationManager",
        context.getSystemService(Context.NOTIFICATION_SERVICE)
    )


def create_notification_channel():
    """Registers the alarm channel. Safe to call repeatedly.

    Android treats re-creating an existing channel as a no-op, so this can run on
    every app start (and every service start) without checking first.

    A notification posted to an unregistered channel is silently dropped, so this
    has to happen before any `post_notification()` call in the same process.
    """
    NotificationChannel = autoclass("android.app.NotificationChannel")
    NotificationManager = autoclass("android.app.NotificationManager")

    context = _get_context()

    # IMPORTANCE_HIGH gets a heads-up popup so a reminder isn't easy to miss, but
    # the channel deliberately keeps the default notification sound on the
    # notification stream -- NOT USAGE_ALARM. Silent on vibrate and subject to Do
    # Not Disturb is the intended behavior: punctuality is the goal, not volume.
    channel = NotificationChannel(
        CHANNEL_ID,
        CHANNEL_NAME,
        NotificationManager.IMPORTANCE_HIGH
    )
    channel.setDescription("Reminders for tasks with an alarm: attribute")
    channel.enableVibration(True)

    _get_notification_manager(context).createNotificationChannel(channel)


def post_notification(title: str, text: str, notification_id: int = NOTIFICATION_ID):
    """Posts an alarm notification.

    Note this fails *silently* if POST_NOTIFICATIONS hasn't been granted (API 33+):
    no exception, nothing in logcat, just no notification. That's the first thing
    to check whenever this appears to run but nothing shows up.
    """
    NotificationBuilder = autoclass("android.app.Notification$Builder")

    context = _get_context()

    builder = NotificationBuilder(context, CHANNEL_ID)
    builder.setContentTitle(title)
    builder.setContentText(text)
    # A notification with no small icon is discarded. Reuse the app's own icon
    # rather than shipping a second drawable.
    builder.setSmallIcon(context.getApplicationInfo().icon)
    builder.setAutoCancel(True)  # dismiss when tapped

    # TODO: setContentIntent so tapping opens the app on the relevant task.
    # Needs a PendingIntent, which is phase D's territory.

    _get_notification_manager(context).notify(notification_id, builder.build())
