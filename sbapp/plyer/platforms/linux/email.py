'''
Module of Linux API for plyer.email.
'''

import subprocess
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote
from plyer.facades import Email
from plyer.utils import whereis_exe


class LinuxEmail(Email):
    '''
    Implementation of Linux email API.
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

        subprocess.Popen(["xdg-open", uri])


def instance():
    '''
    Instance for facade proxy.
    '''
    import sys
    if whereis_exe('xdg-open'):
        return LinuxEmail()
    sys.stderr.write("xdg-open not found.")
    return Email()
