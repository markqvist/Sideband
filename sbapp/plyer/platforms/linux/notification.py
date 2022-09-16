'''
Module of Linux API for plyer.notification.
'''

import warnings
import subprocess
from plyer.facades import Notification
from plyer.utils import whereis_exe
import os


class NotifyDesktopPortals(Notification):
    '''
    Implementation of xdg-desktop-portals API.
    '''

    def _notify(self, **kwargs):
        title = kwargs.get("title", "title")
        body = kwargs.get("message", "body")

        subprocess.run([
            "gdbus", "call", "--session", "--dest",
            "org.freedesktop.portal.Desktop",
            "--object-path", "/org/freedesktop/portal/desktop", "--method",
            "org.freedesktop.portal.Notification.AddNotification", "",
            "{'title': <'" + title + "'>, 'body': <'" + body + "'>}"
        ], stdout=subprocess.DEVNULL)


class NotifySendNotification(Notification):
    '''
    Implementation of Linux notification API
    using notify-send binary.
    '''
    def _notify(self, **kwargs):
        icon = kwargs.get('icon', '')
        title = kwargs.get('title', 'title')
        hint = kwargs.get('hint', 'string::')
        message = kwargs.get('message', 'body')
        category = kwargs.get('category', '')
        app_name = kwargs.get('app_name', '')
        urgency = kwargs.get('urgency', 'normal')
        expire_time = kwargs.get('expire_time', '0')

        notify_send_args = (title,
                            message,
                            "-i", icon,
                            "-h", hint,
                            "-u", urgency,
                            "-c", category,
                            "-a", app_name,
                            "-t", expire_time)

        subprocess.call(["notify-send", *notify_send_args])


class NotifyDbus(Notification):
    '''
    Implementation of Linux notification API
    using dbus library and dbus-python wrapper.
    '''

    def _notify(self, **kwargs):
        summary = kwargs.get('title', "title")
        body = kwargs.get('message', "body")
        app_name = kwargs.get('app_name', '')
        app_icon = kwargs.get('app_icon', '')
        timeout = kwargs.get('timeout', 10)
        actions = kwargs.get('actions', [])
        hints = kwargs.get('hints', {})
        replaces_id = kwargs.get('replaces_id', 0)

        _bus_name = 'org.freedesktop.Notifications'
        _object_path = '/org/freedesktop/Notifications'
        _interface_name = _bus_name

        import dbus
        session_bus = dbus.SessionBus()
        obj = session_bus.get_object(_bus_name, _object_path)
        interface = dbus.Interface(obj, _interface_name)
        interface.Notify(
            app_name, replaces_id, app_icon,
            summary, body, actions,
            hints, timeout * 1000
        )


def instance():
    '''
    Instance for facade proxy.
    '''
    if os.path.isdir("/app"):
        # Flatpak
        return NotifyDesktopPortals()
    try:
        import dbus  # noqa: F401
        return NotifyDbus()
    except ImportError:
        msg = ("The Python dbus package is not installed.\n"
               "Try installing it with your distribution's package manager, "
               "it is usually called python-dbus or python3-dbus, but you "
               "might have to try dbus-python instead, e.g. when using pip.")
        warnings.warn(msg)

    if whereis_exe('notify-send'):
        return NotifySendNotification()
    warnings.warn("notify-send not found.")
    return Notification()
