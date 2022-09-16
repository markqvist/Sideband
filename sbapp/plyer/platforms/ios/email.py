'''
Module of iOS API for plyer.email.
'''

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from plyer.facades import Email
from pyobjus import autoclass, objc_str
from pyobjus.dylib_manager import load_framework

load_framework('/System/Library/Frameworks/UIKit.framework')

NSURL = autoclass('NSURL')
NSString = autoclass('NSString')
UIApplication = autoclass('UIApplication')


class IOSEmail(Email):
    '''
    Implementation of iOS battery API.
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

        nsurl = NSURL.alloc().initWithString_(objc_str(uri))

        UIApplication.sharedApplication().openURL_(nsurl)


def instance():
    '''
    Instance for facade proxy.
    '''
    return IOSEmail()
