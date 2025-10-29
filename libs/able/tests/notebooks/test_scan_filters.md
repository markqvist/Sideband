---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.11.2
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Setup

```python
%run init.ipynb
```

```python
%%there
from able.filters import *

class BLE(BluetoothDispatcher):

    def on_scan_started(self, success):
        results.started = success
        
    def on_scan_completed(self):
        results.completed = 1
        
    def on_device(self, device, rssi, advertisement):
        results.devices.append(device)

ble = BLE()
```

```python
%%there
BluetoothDevice = autoclass("android.bluetooth.BluetoothDevice")
ScanResult = autoclass("android.bluetooth.le.ScanResult")
ScanRecord = autoclass("android.bluetooth.le.ScanRecord")
Parcel = autoclass("android/os/Parcel")
ParcelUuid = autoclass('android.os.ParcelUuid')

def filter_matches(f, scan_result):
    print(f, f.build().matches(scan_result))

def mock_device():
    """Return BluetoothDevice instance with address=AA:AA:AA:AA:AA:AA"""
    device_data = [17, 0, 0, 0, 65, 0, 65, 0, 58, 0, 65, 0, 65, 0, 58, 0, 65, 0, 65, 0, 58, 0, 65, 0, 65, 0, 58, 0, 65, 0, 65, 0, 58, 0, 65, 0, 65]
    p = Parcel.obtain()
    p.unmarshall(device_data, 0, len(device_data))
    p.setDataPosition(0)
    return BluetoothDevice.CREATOR.createFromParcel(p)


def mock_scan_result(record):
    return ScanResult(mock_device(), ScanRecord.parseFromBytes(record), -33, 1633954394000)

def mock_test_app_scan_result():
    return mock_scan_result(
        [2, 1, 6, 17, 6, 27, 197, 213, 165, 2, 0, 200, 184, 227, 17, 17, 193, 0, 13,
         254, 22, 12, 9, 75, 105, 118, 121, 66, 76, 69, 84, 101, 115, 116,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]
    )

def mock_beacon_scan_result():
    """0x4C,  # Apple Manufacturer ID
        bytes([
            0x2, # SubType: Custom Manufacturer Data
            0x15 # Subtype lenth
        ]) +
        uuid +  # UUID of beacon: UUID=8da683d6-e574-4a2e-bb9b-d83f2d05fc12
        bytes([
            0, 15,  # Major value
            0, 1,  # Minor value
            10  # RSSI, dBm at 1m
        ])
    """
    return mock_scan_result(bytes.fromhex('1AFF4C0002158DA683D6E5744A2EBB9BD83F2D05FC12000F00010A'))

def mock_battery_scan_result():
    """Battery ("0000180f-0000-1000-8000-00805f9b34fb" or "180f" in short form)
       service data: 34% (0x22)
    """
    return mock_scan_result(bytes.fromhex('04160F1822'))

beacon = mock_beacon_scan_result()
battery = mock_battery_scan_result()
testapp = mock_test_app_scan_result()
```

# Test device is found with scan filters set

```python
%%there
results =  Results()
ble.start_scan(filters=[
    DeviceNameFilter("KivyBLETest") & ServiceUUIDFilter("16fe0d00-c111-11e3-b8c8-0002a5d5c51b"),
])
```

```python
sleep(10)
```

```python
%%there
ble.stop_scan()
```

```python
sleep(2)
```

```python
%%there
print(set([dev.getName() for dev in results.devices]))
```

# Test device is not found: filtered out by name

```python
%%there
results =  Results()
ble.start_scan(filters=[DeviceNameFilter("No-such-device-8458e2e35158")])
```

```python
sleep(10)
```

```python
%%there
ble.stop_scan()
```

```python
sleep(2)
```

```python
%%there
print(results.devices)
```

# Test scan filter mathes

```python
%%there
filter_matches(EmptyFilter(), testapp)
filter_matches(EmptyFilter(), beacon)
filter_matches(EmptyFilter(), battery)
```

```python
%%there
filter_matches(DeviceAddressFilter("AA:AA:AA:AA:AA:AA"), testapp)
filter_matches(DeviceAddressFilter("AA:AA:AA:AA:AA:AB"), testapp)
try:
    filter_matches(DeviceAddressFilter("AA"), testapp)
except Exception as exc:
    print(exc)
```

```python
%%there
filter_matches(DeviceNameFilter("KivyBLETest"), testapp)
filter_matches(DeviceNameFilter("KivyBLETes"), testapp)
```

```python
%%there
filter_matches(ManufacturerDataFilter(0x4c, []), testapp)
filter_matches(ManufacturerDataFilter(0x4c, []), beacon)
filter_matches(ManufacturerDataFilter(0x4c, [0x2, 0x15, 0x8d, 0xa6, 0x83, 0xd6, 0xe5]), beacon)
filter_matches(ManufacturerDataFilter(0x4c, [0x2, 0x15, 0x8d, 0xa6, 0x83, 0xd6, 0xaa]), beacon)
filter_matches(
    ManufacturerDataFilter(0x4c,
                           [0x2, 0x15, 0x8d, 0xa6, 0x83, 0xd6, 0xaa],
                           [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00]),
    beacon
)
filter_matches(
    ManufacturerDataFilter(0x4c,
                           [0x2, 0x15, 0x8d, 0xa6, 0x83, 0xd6, 0xaa],
                           [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff]),
    beacon
)
filter_matches(ManufacturerDataFilter(0x4c, [0x2, 0, 0x8d, 0xa6, 0x83], [0xff, 0, 0xff, 0xff, 0xff]), beacon)
filter_matches(ManufacturerDataFilter(0x4c, b'\x02\x15'), beacon)
filter_matches(ManufacturerDataFilter(0x4c, b'\x02\x16'), beacon)
```

```python
%%there
filter_matches(ServiceDataFilter("0000180f-0000-1000-8000-00805f9b34fb", []), battery)
filter_matches(ServiceDataFilter("0000180f-0000-1000-8000-00805f9b34fc", []), battery)

filter_matches(ServiceDataFilter("0000180f-0000-1000-8000-00805f9b34fb", [0x22]), battery)
filter_matches(ServiceDataFilter("0000180f-0000-1000-8000-00805f9b34fb", [0x21]), battery)
filter_matches(ServiceDataFilter("0000180f-0000-1000-8000-00805f9b34fb", [0x21], mask=[0xf0]), battery)
filter_matches(ServiceDataFilter("0000180f-0000-1000-8000-00805f9b34fb", [0x21], mask=[0x0f]), battery)
```

```python
%%there
filter_matches(ServiceUUIDFilter("16fe0d00-c111-11e3-b8c8-0002a5d5c51B"), testapp)
filter_matches(ServiceUUIDFilter("16fe0d00-c111-11e3-b8c8-0002a5d5c51C"), testapp)
filter_matches(ServiceUUIDFilter(
    "16fe0d00-c111-11e3-b8c8-0002a5d5c51C",
    "ffffffff-ffff-ffff-ffff-ffffffffffff"
), testapp)
filter_matches(ServiceUUIDFilter(
    "16fe0d00-c111-11e3-b8c8-0002a5d5c51C",
    "ffffffff-ffff-ffff-ffff-fffffffffff0"
), testapp)
```
