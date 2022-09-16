from plyer.facades import Keystore
from pyobjus import autoclass, objc_str

NSUserDefaults = autoclass('NSUserDefaults')


class IosKeystore(Keystore):

    def _set_key(self, servicename, key, value, **kwargs):
        NSUserDefaults.standardUserDefaults().setObject_forKey_(
            objc_str(value), objc_str(key))

    def _get_key(self, servicename, key, **kwargs):
        ret = NSUserDefaults.standardUserDefaults().stringForKey_(
            objc_str(key))
        if ret is not None:
            return ret.UTF8String()
        else:
            return ret


def instance():
    return IosKeystore()
