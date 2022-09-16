# coding=utf-8
"""
Flash
-----
"""
from plyer.facades import Flash
from pyobjus import autoclass

NSString = autoclass("NSString")
AVCaptureDevice = autoclass("AVCaptureDevice")
AVMediaTypeVideo = NSString.alloc().initWithUTF8String_("vide")
AVCaptureTorchModeOff = 0
AVCaptureTorchModeOn = 1


class IosFlash(Flash):
    _camera = None

    def _on(self):
        if self._camera is None:
            self._camera_open()
        if not self._camera:
            return
        self._camera.lockForConfiguration_(None)
        try:
            self._camera.setTorchMode(AVCaptureTorchModeOn)
        finally:
            self._camera.unlockForConfiguration()

    def _off(self):
        if not self._camera:
            return
        self._camera.lockForConfiguration_(None)
        try:
            self._camera.setTorchMode(AVCaptureTorchModeOff)
        finally:
            self._camera.unlockForConfiguration()

    def _release(self):
        pass

    def _camera_open(self):
        device = AVCaptureDevice.defaultDeviceWithMediaType_(AVMediaTypeVideo)
        if not device:
            return
        self._camera = device


def instance():
    return IosFlash()
