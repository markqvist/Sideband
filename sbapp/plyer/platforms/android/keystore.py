from plyer.facades import Keystore
from plyer.platforms.android import activity


class AndroidKeystore(Keystore):

    def _set_key(self, servicename, key, value, **kwargs):
        mode = kwargs.get("mode", 0)
        settings = activity.getSharedPreferences(servicename, mode)
        editor = settings.edit()
        editor.putString(key, value)
        editor.commit()

    def _get_key(self, servicename, key, **kwargs):
        mode = kwargs.get("mode", 0)
        default = kwargs.get("default", "__None")
        settings = activity.getSharedPreferences(servicename, mode)
        ret = settings.getString(key, default)
        if ret == "__None":
            ret = None
        return ret


def instance():
    return AndroidKeystore()
