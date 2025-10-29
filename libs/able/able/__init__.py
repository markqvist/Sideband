from enum import IntEnum

from able.structures import Advertisement, Services
from able.version import __version__  # noqa
from kivy.utils import platform

__all__ = (
    "Advertisement",
    "BluetoothDispatcher",
    "Services",
)

# constants
GATT_SUCCESS = 0  #: GATT operation completed successfully
STATE_CONNECTED = 2  #: The profile is in connected state
STATE_DISCONNECTED = 0  #: The profile is in disconnected state


class AdapterState(IntEnum):
    """Bluetooth adapter state constants.
    https://developer.android.com/reference/android/bluetooth/BluetoothAdapter#STATE_OFF
    """

    OFF = 10  #: Adapter is off
    TURNING_ON = 11  #: Adapter is turning on
    ON = 12  #: Adapter is on
    TURNING_OFF = 13  #: Adapter is turning off


class WriteType(IntEnum):
    """GATT characteristic write types constants."""

    DEFAULT = (
        2  #: Write characteristic, requesting acknowledgement by the remote device
    )
    NO_RESPONSE = (
        1  #: Write characteristic without requiring a response by the remote device
    )
    SIGNED = 4  #: Write characteristic including authentication signature


if platform == "android":
    from able.android.dispatcher import BluetoothDispatcher
else:

    # mock android and PyJNIus modules usage
    import sys
    from unittest.mock import Mock

    sys.modules["android"] = Mock()
    sys.modules["android.permissions"] = Mock()
    jnius = Mock()

    class mocked_autoclass(Mock):
        def __call__(self, *args, **kwargs):
            mock = Mock()
            mock.__repr__ = lambda s: f"jnius.autoclass('{args[0]}')"
            mock.SDK_INT = 255
            return mock

    jnius.autoclass = mocked_autoclass()
    sys.modules["jnius"] = jnius

    from able.dispatcher import BluetoothDispatcherBase

    class BluetoothDispatcher(BluetoothDispatcherBase):
        """Bluetooth Low Energy interface

        :param queue_timeout: BLE operations queue timeout
        :param enable_ble_code: request code to identify activity that alows
               user to turn on Bluetooth adapter
        :param runtime_permissions: overridden list of
               :py:mod:`permissions <able.permissions>`
               to be requested on runtime.
        """


from able.adapter import require_bluetooth_enabled
from able.permissions import Permission


def require_runtime_permissions(method):
    """Deprecated decorator, left for backwards compatibility."""
    return method
