'''
Module of Windows API for plyer.notification.
'''

from threading import Thread as thread

from plyer.facades import Notification
from plyer.platforms.win.libs.balloontip import balloon_tip


class WindowsNotification(Notification):
    '''
    Implementation of Windows notification/balloon API.
    '''

    def _notify(self, **kwargs):
        thread(target=balloon_tip, kwargs=kwargs).start()


def instance():
    '''
    Instance for facade proxy.
    '''
    return WindowsNotification()
