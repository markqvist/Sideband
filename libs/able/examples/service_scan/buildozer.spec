[app]
title = BLE scan dev service
version = 1.1
package.name = scanservice
package.domain = test.able
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

android.permissions =
    FOREGROUND_SERVICE,
    BLUETOOTH,
    BLUETOOTH_ADMIN,
    BLUETOOTH_SCAN,
    BLUETOOTH_CONNECT,
    BLUETOOTH_ADVERTISE,
    ACCESS_FINE_LOCATION

requirements = kivy==2.1.0,python3,able_recipe
services = Able:service.py:foreground

android.accept_sdk_license = True

# android.api = 31
# android.minapi = 31

[buildozer]
warn_on_root = 1
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
