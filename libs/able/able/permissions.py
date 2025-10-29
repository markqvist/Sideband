"""Before executing, all :class:`BluetoothDispatcher <able.BluetoothDispatcher>` methods that requires Bluetooth adapter
(`start_scan`, `connect_by_device_address`, `enable_notifications`, `adapter` property ...),
are asking the user to:

#. grant runtime permissions,
#. turn on Bluetooth adapter.

The list of requested runtime permissions varies depending on the level of the target Android API level:

* target API level <=30: ACCESS_FINE_LOCATION - to obtain BLE scan results
* target API level >= 31:

  * BLUETOOTH_CONNECT - to enable adapter and to connect to devices
  * BLUETOOTH_SCAN - to start the scan
  * ACCESS_FINE_LOCATION - to detect beacons during the scan
  * BLUETOOTH_ADVERTISE - to be able to advertise to nearby Bluetooth devices

Requested permissions list can be changed with the `BluetoothDispatcher.runtime_permissions` parameter.
"""
from jnius import autoclass

SDK_INT = int(autoclass("android.os.Build$VERSION").SDK_INT)


class Permission:
    """
    String constants values for BLE-related permissions.
    https://developer.android.com/reference/android/Manifest.permission
    """

    ACCESS_BACKGROUND_LOCATION = "android.permission.ACCESS_BACKGROUND_LOCATION"
    ACCESS_FINE_LOCATION = "android.permission.ACCESS_FINE_LOCATION"
    BLUETOOTH_ADVERTISE = "android.permission.BLUETOOTH_ADVERTISE"
    BLUETOOTH_CONNECT = "android.permission.BLUETOOTH_CONNECT"
    BLUETOOTH_SCAN = "android.permission.BLUETOOTH_SCAN"


if SDK_INT >= 31:
    # API level 31 (Android 12) introduces new permissions
    DEFAULT_RUNTIME_PERMISSIONS = [
        Permission.BLUETOOTH_ADVERTISE,
        Permission.BLUETOOTH_CONNECT,
        Permission.BLUETOOTH_SCAN,
        # ACCESS_FINE_LOCATION is not mandatory for scan,
        # but required to discover beacons
        Permission.ACCESS_FINE_LOCATION,
    ]
else:
    # For API levels 29-30,
    # ACCESS_FINE_LOCATION permission is needed to obtain BLE scan results
    DEFAULT_RUNTIME_PERMISSIONS = [
        Permission.ACCESS_FINE_LOCATION,
    ]
