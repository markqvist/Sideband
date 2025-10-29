[app]
title = Multiple BLE devices
version = 1.0
package.name = multidevs
package.domain = test.able
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

requirements = python3,kivy,android,able_recipe

android.accept_sdk_license = True
android.permissions =
    BLUETOOTH,
    BLUETOOTH_ADMIN,
    BLUETOOTH_SCAN,
    BLUETOOTH_CONNECT,
    BLUETOOTH_ADVERTISE,
    ACCESS_FINE_LOCATION

# android.api = 31
# android.minapi = 31


[buildozer]
warn_on_root = 1
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
