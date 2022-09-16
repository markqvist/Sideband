'''
IOS Sms
----------
'''

from plyer.facades import Sms
from pyobjus import autoclass, objc_str
from pyobjus.dylib_manager import load_framework

NSURL = autoclass('NSURL')
NSString = autoclass('NSString')
UIApplication = autoclass('UIApplication')
load_framework('/System/Library/Frameworks/MessageUI.framework')


class IOSSms(Sms):

    def _send(self, **kwargs):
        '''
        This method provides sending messages to recipients.

        Expects 2 parameters in kwargs:
            - recipient: String type
            - message: String type

        Opens a message interface with recipient and message information.
        '''
        recipient = kwargs.get('recipient')
        message = kwargs.get('message')
        url = "sms:"
        if recipient:
            # Apple has not supported multiple recipients yet.
            url += str(recipient)
        if message:
            # Apple has to supported it yet.
            pass

        nsurl = NSURL.alloc().initWithString_(objc_str(url))
        UIApplication.sharedApplication().openURL_(nsurl)


def instance():
    return IOSSms()
