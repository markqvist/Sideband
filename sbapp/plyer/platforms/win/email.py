'''
Module of Windows API for plyer.email.
'''

import os
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote
from plyer.facades import Email


class WindowsEmail(Email):
    '''
    Implementation of Windows email API.
    '''

    def _send(self, **kwargs):
        recipient = kwargs.get('recipient')
        subject = kwargs.get('subject')
        text = kwargs.get('text')

        uri = "mailto:"
        if recipient:
            uri += str(recipient)
        if subject:
            uri += "?" if "?" not in uri else "&"
            uri += "subject="
            uri += quote(str(subject))
        if text:
            uri += "?" if "?" not in uri else "&"
            uri += "body="
            uri += quote(str(text))

        # WE + startfile are available only on Windows
        try:
            os.startfile(uri)
        except WindowsError:
            print("Warning: unable to find a program able to send emails.")


def instance():
    '''
    Instance for facade proxy.
    '''
    return WindowsEmail()
