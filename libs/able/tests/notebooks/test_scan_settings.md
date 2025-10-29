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
class BLE(BluetoothDispatcher):

    def on_scan_started(self, success):
        results.started = success
        
    def on_scan_completed(self):
        results.completed = 1
        
    def on_device(self, device, rssi, advertisement):
        results.devices.append(device)

def get_advertisemnt_count():
    return len([dev for dev in results.devices if dev.getName() == "KivyBLETest"])        

ble = BLE()
```

# Run SCAN_MODE_LOW_POWER

```python
%%there
results =  Results()
ble.start_scan(
    settings=ScanSettingsBuilder().setScanMode(ScanSettings.SCAN_MODE_LOW_POWER)
)
```

```python
sleep(20)
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
low_power_advertisement_count = get_advertisemnt_count()
print(low_power_advertisement_count > 0)
```

# Run SCAN_MODE_LOW_LATENCY

```python
%%there
results =  Results()

ble.start_scan(
    settings=ScanSettingsBuilder().setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
)
```

```python
sleep(20)
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
low_latency_advertisement_count = get_advertisemnt_count()
print(low_latency_advertisement_count > 0)
```

# Check that received advertisement count is greater with SCAN_MODE_LOW_LATENCY 

```python
%%there
print(low_latency_advertisement_count - low_power_advertisement_count > 2)
```
