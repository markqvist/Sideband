"""Request MTU change, and write 100 bytes to a characteristic."""
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.widget import Widget

from able import BluetoothDispatcher, GATT_SUCCESS


class BLESender(BluetoothDispatcher):

    def __init__(self):
        super().__init__()
        self.characteristic_to_write = None
        Clock.schedule_once(self.connect, 0)

    def connect(self, _):
        self.connect_by_device_address("FF:FF:FF:FF:FF:FF")

    def on_connection_state_change(self, status, state):
        if status == GATT_SUCCESS and state:
            self.discover_services()

    def on_services(self, status, services):
        if status == GATT_SUCCESS:
            self.characteristic_to_write = services.search("0d03")
            # Need to request 100 + 3 extra bytes for ATT packet header
            self.request_mtu(103)

    def on_mtu_changed(self, mtu, status):
        if status == GATT_SUCCESS and mtu == 103:
            Logger.info("MTU changed: now it is possible to send 100 bytes at once")
            self.write_characteristic(self.characteristic_to_write, range(100))
        else:
            Logger.error("MTU not changed: mtu=%d, status=%d", mtu, status)

    def on_characteristic_write(self, characteristic, status):
        if status == GATT_SUCCESS:
            Logger.info("Characteristic write succeed")
        else:
            Logger.error("Write status: %d", status)


class MTUApp(App):

    def build(self):
        BLESender()
        return Widget()


if __name__ == '__main__':
    MTUApp().run()
