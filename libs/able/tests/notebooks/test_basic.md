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
        
ble = BLE()
```

# Run BLE devices scan

```python
%%there
results =  Results()
print(f"Started: {results.started} Completed: {results.completed}")
ble.start_scan()
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

# Check that scan started and completed

```python
%%there
print(f"Started: {results.started} Completed: {results.completed}")
```

# Check that testing device was discovered

```python
%%there
print(
    "KivyBLETest" in [dev.getName() for dev in results.devices]
)
```
