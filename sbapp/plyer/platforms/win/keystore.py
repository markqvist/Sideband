try:
    import keyring
except Exception:
    raise NotImplementedError()

from plyer.facades import Keystore


class WinKeystore(Keystore):

    def _set_key(self, servicename, key, value, **kwargs):
        keyring.set_password(servicename, key, value)

    def _get_key(self, servicename, key, **kwargs):
        return keyring.get_password(servicename, key)


def instance():
    return WinKeystore()
