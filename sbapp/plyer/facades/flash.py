# coding=utf-8
'''
Flash
=====

The :class:`Flash` provides access to public methods to use flash of your
device.

.. note::
    In android you need CAMERA, FLASHLIGHT permissions
    to access flash.

.. versionadded:: 1.2.5

This can be used to activate the flash of your camera on
Android and iOS.

Simple Examples
---------------

To turn on flash::

    >>> from plyer import flash
    >>> flash.on()

To turn off flash::

    >>> flash.off()

To release flash::

    >>> flash.release()

Supported Platforms
-------------------
Android, iOS

'''


class Flash:
    """
    Flash facade.
    """

    def on(self):
        """
        Activate the flash
        """
        self._on()

    def off(self):
        """
        Deactiavte the flash
        """
        self._off()

    def release(self):
        """
        Release any access to the Flash / Camera.
        Call this when you're done using the Flash.
        This will release the Camera, and stop any process.

        Next call to `_on` will reactivate it.
        """
        self._release()

    # private

    def _on(self):
        raise NotImplementedError()

    def _off(self):
        raise NotImplementedError()

    def _release(self):
        pass
