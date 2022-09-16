'''
Keystore
=======
The :class:`Keystore` provides a mechanism for securing/storing
cryptographic keys (such as user credentials) in a container.
Typically needed to support authentication APIs such as OAuth2
.. note::
    Typically needed to support authentication APIs such as OAuth2

Supported Platforms
-------------------
Android, iOS, Windows, OS X, Linux
---------------
'''


class Keystore:
    '''
    Keystore facade
    '''

    def set_key(self, servicename, key, value, **kwargs):
        self._set_key(servicename, key, value, **kwargs)

    def _set_key(self, servicename, key, value, **kwargs):
        raise NotImplementedError()

    def get_key(self, servicename, key, **kwargs):
        return self._get_key(servicename, key)

    def _get_key(self, servicename, key, **kwargs):
        raise NotImplementedError()
