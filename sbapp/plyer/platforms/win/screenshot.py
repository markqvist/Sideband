'''
https://docs.microsoft.com/en-us/windows/desktop/api/wingdi/nf-wingdi-bitblt
https://www.bugs.python.org/issue33656
'''

from os import getpid
from os.path import join
from ctypes import windll, c_int, addressof

from win32gui import GetDesktopWindow, GetWindowDC
from win32api import GetSystemMetrics
from win32ui import CreateDCFromHandle, CreateBitmap
from win32con import (
    SM_CXVIRTUALSCREEN,
    SM_CYVIRTUALSCREEN,
    SM_XVIRTUALSCREEN,
    SM_YVIRTUALSCREEN,
    SRCCOPY
)

from plyer.facades import Screenshot
from plyer.platforms.win.storagepath import WinStoragePath


class WinScreenshot(Screenshot):
    def __init__(self, file_path=None):
        default_path = join(
            WinStoragePath().get_pictures_dir(), 'screenshot.bmp'
        )
        super().__init__(file_path or default_path)

    def _set_dpi_aware(self, value):
        try:
            windll.shcore.SetProcessDpiAwareness(value)
        except (AttributeError, OSError):
            print('Could not set DPI awareness.')

    def _dpi_aware(self):
        # make backup of DPI awareness value in case a user does not want
        # to use it, otherwise we'll cripple user's runtime
        try:
            process_handle = windll.kernel32.OpenProcess(
                0,      # no permissions
                False,  # bInheritHandle
                getpid()
            )
            aware = c_int()
            windll.shcore.GetProcessDpiAwareness(
                process_handle,
                addressof(aware)
            )
        finally:
            # always close the handle!
            windll.kernel32.CloseHandle(process_handle)
        return bool(aware)

    def _capture(self):
        # make sure the process is DPI aware, otherwise the image
        # is only a part of the full monitor content
        # (necessary only on Win 8.1+)
        old_awareness = self._dpi_aware()
        self._set_dpi_aware(True)

        # get width and height of current monitor
        width = GetSystemMetrics(SM_CXVIRTUALSCREEN)
        height = GetSystemMetrics(SM_CYVIRTUALSCREEN)

        # get 'desktop' window handle
        handle_desktop = GetDesktopWindow()

        # get window graphic context handle
        handle_context = GetWindowDC(handle_desktop)

        # create device context
        dev_ctx = CreateDCFromHandle(handle_context)

        # create destination for original device context
        dest_ctx = dev_ctx.CreateCompatibleDC()

        # create bitmap compatible with desktop window device
        bmp = CreateBitmap()
        bmp.CreateCompatibleBitmap(dev_ctx, width, height)

        # select bitmap into destination device
        dest_ctx.SelectObject(bmp)

        # populate selected bitmap in destination device
        dest_ctx.BitBlt(
            (0, 0),           # start point (x, y)
            (width, height),  # size of rectangle
            dev_ctx,          # source device
            (
                GetSystemMetrics(SM_XVIRTUALSCREEN),
                GetSystemMetrics(SM_YVIRTUALSCREEN)
            ),                # source rectangle, can be different monitor
            SRCCOPY           # copy directly without filters
        )

        # save bitmap to file
        bmp.SaveBitmapFile(dest_ctx, self.file_path)

        # return to the original state
        self._set_dpi_aware(old_awareness)


def instance():
    return WinScreenshot()
