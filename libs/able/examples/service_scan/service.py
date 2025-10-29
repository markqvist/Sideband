"""Service to run BLE scan for 60 seconds,
and log each `on_device` event.
"""
import time

from able import BluetoothDispatcher
from kivy.logger import Logger


class BLE(BluetoothDispatcher):
    def on_device(self, device, rssi, advertisement):
        title = device.getName() or device.getAddress()
        Logger.info("BLE Device found: %s", title)

    def on_error(self, msg):
        Logger.error("BLE Error %s", msg)


def main():
    ble = BLE()
    ble.start_scan()
    time.sleep(60)
    ble.stop_scan()


if __name__ == "__main__":
    main()
