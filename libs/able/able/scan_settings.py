"""BLE scanning settings.
"""
from jnius import autoclass
from kivy.utils import platform


if platform != 'android':
    class ScanSettings:
        """PyJNIus wrapper for Java class `android.bluetooth.le.ScanSettings`.
        https://developer.android.com/reference/android/bluetooth/le/ScanSettings
        """

    class ScanSettingsBuilder:
        """PyJNIus wrapper for Java class `android.bluetooth.le.ScanSettings.Builder`.
        https://developer.android.com/reference/android/bluetooth/le/ScanSettings.Builder
        """

else:
    ScanSettings = autoclass('android.bluetooth.le.ScanSettings')
    ScanSettingsBuilder = autoclass('android.bluetooth.le.ScanSettings$Builder')
