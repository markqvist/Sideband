"""Scan for devices with name "KivyBLETest",
connect and periodically read connected devices RSSI.

Multiple `BluetoothDispatcher` objects are used:
    one for the scanning process and one for every connected device.
"""
from able import GATT_SUCCESS, BluetoothDispatcher
from able.filters import DeviceNameFilter
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.label import Label


class DeviceDispatcher(BluetoothDispatcher):
    """Dispatcher to control a single BLE device."""

    def __init__(self, device: "BluetoothDevice"):
        super().__init__()
        self._device = device
        self._address: str = device.getAddress()
        self._name: str = device.getName() or ""

    @property
    def title(self) -> str:
        return f"<{self._address}><{self._name}>"

    def on_connection_state_change(self, status: int, state: int):
        if status == GATT_SUCCESS and state:
            Logger.info(f"Device: {self.title} connected")
        else:
            Logger.info(f"Device: {self.title} disconnected. {status=}, {state=}")
            self.close_gatt()
            Clock.schedule_once(callback=lambda dt: self.reconnect(), timeout=15)

    def on_rssi_updated(self, rssi: int, status: int):
        Logger.info(f"Device: {self.title} RSSI: {rssi}")

    def periodically_update_rssi(self):
        """
        Clock callback to read
        the signal strength indicator for a connected device.
        """
        if self.gatt:  # if device is connected
            self.update_rssi()

    def reconnect(self):
        Logger.info(f"Device: {self.title} try to reconnect ...")
        self.connect_gatt(self._device)

    def start(self):
        """Start connection to device."""
        if not self.gatt:
            self.connect_gatt(self._device)
            Clock.schedule_interval(
                callback=lambda dt: self.periodically_update_rssi(), timeout=5
            )


class ScannerDispatcher(BluetoothDispatcher):
    """Dispatcher to control the scanning process."""

    def __init__(self):
        super().__init__()
        # Stores connected devices addresses
        self._devices: dict[str, DeviceDispatcher] = {}

    def on_scan_started(self, success: bool):
        if success:
            Logger.info("Scan: started")
        else:
            Logger.error("Scan: error on start")

    def on_scan_completed(self):
        Logger.info("Scan: completed")

    def on_device(self, device, rssi, advertisement):
        address = device.getAddress()
        if address not in self._devices:
            # Create dispatcher instance for a new device
            dispatcher = DeviceDispatcher(device)
            # Remember address,
            # to avoid multiple dispatchers creation for this device
            self._devices[address] = dispatcher
            Logger.info(f"Scan: device <{address}> added")
            dispatcher.start()


class MultiDevicesApp(App):
    def build(self):
        ScannerDispatcher().start_scan(filters=[DeviceNameFilter("KivyBLETest")])
        return Label(text=self.name)


if __name__ == "__main__":
    MultiDevicesApp().run()
