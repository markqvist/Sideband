'''
IOS Call
----------
'''

from plyer.facades import Call
from pyobjus import autoclass, objc_str

NSURL = autoclass('NSURL')
NSString = autoclass('NSString')
UIApplication = autoclass('UIApplication')


class IOSCall(Call):

    def _makecall(self, **kwargs):
        tel = kwargs.get('tel')
        url = "tel://" + tel
        nsurl = NSURL.alloc().initWithString_(objc_str(url))

        UIApplication.sharedApplication().openURL_(nsurl)

    def _dialcall(self, **kwargs):
        pass
        # Not possible, Access not provided by iPhone SDK


def instance():
    return IOSCall()
