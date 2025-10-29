Changelog
=========

1.0.16
------

* Added `autoconnect` parameter to connection methods
  `#45 <https://github.com/b3b/able/issues/45>`_

1.0.15
------

* Changing the wheel name to avoid installing a package from cache
  `#40 <https://github.com/b3b/able/issues/40>`_

1.0.14
------

* Added event handler for bluetooth adapter state change
  `#39 <https://github.com/b3b/able/pull/39>`_ by `robgar2001 <https://github.com/robgar2001>`_
* Removal of deprecated `convert_path` from setup script

1.0.13
------

* Fixed build failure when pip isolated environment is used `#38 <https://github.com/b3b/able/issues/38>`_

1.0.12
------

* Fixed crash on API level 31 (Android 12) `#37 <https://github.com/b3b/able/issues/37>`_
* Added new optional `BluetoothDispatcher` parameter to specifiy required permissions: `runtime_permissions`.
  Runtime permissions that are required by by default:
  ACCESS_FINE_LOCATION, BLUETOOTH_SCAN, BLUETOOTH_CONNECT, BLUETOOTH_ADVERTISE
* Changed `able.require_bluetooth_enabled` behavior: first asks for runtime permissions
  and if permissions are granted then offers to enable the adapter
* `require_runtime_permissions` decorator deprecated

1.0.11
------

* Improved logging of reconnection management
  `#33 <https://github.com/b3b/able/pull/33>`_ by `robgar2001 <https://github.com/robgar2001>`_

1.0.10
------

* Fixed build failure after AAB support was added to python-for-android

1.0.9
-----

* Switched from deprecated scanning method `BluetoothAdapter.startLeScan` to `BluetoothLeScanner.startScan`
* Added support for BLE scanning settings: `able.scan_settings` module
* Added support for BLE scanning filters: `able.filters` module


1.0.8
-----

* Added support to use `able` in Android services
* Added decorators:

  - `able.require_bluetooth_enabled`: to call `BluetoothDispatcher` method when bluetooth adapter becomes ready
  - `able.require_runtime_permissions`:  to call `BluetoothDispatcher` method when location runtime permission is granted


1.0.7
-----

* Added `able.advertising`: module to perform BLE advertise operations
* Added property to get and set Bluetoth adapter name


1.0.6
-----

* Fixed `TypeError` exception on `BluetoothDispatcher.enable_notifications`


1.0.5
-----

* Added `BluetoothDispatcher.bonded_devices` property: list of paired BLE devices

1.0.4
-----

* Fixed sending string data with `write_characteristic` function

1.0.3
-----

* Changed package version generation:

  - Version is set during the build, from the git tag
  - Development (git master) version is always "0.0.0"
* Added ATT MTU changing method and callback
* Added MTU changing example
* Fixed:

  - set `BluetoothDispatcher.gatt` attribute in GATT connection handler,
    to avoid possible `on_connection_state_change()` call before  the `gatt` attribute is set
