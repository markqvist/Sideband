"""Turn the alert on Mi Band device
"""
from kivy.app import App
from kivy.uix.button import Button

from able import BluetoothDispatcher, GATT_SUCCESS
from error_message import install_exception_handler


class BLE(BluetoothDispatcher):
    device = alert_characteristic = None

    def start_alert(self, *args, **kwargs):
        if self.alert_characteristic:  # alert service is already discovered
            self.alert(self.alert_characteristic)
        elif self.device:  # device is already founded during the scan
            self.connect_gatt(self.device)  # reconnect
        else:
            self.stop_scan()  # stop previous scan
            self.start_scan()  # start a scan for devices

    def on_device(self, device, rssi, advertisement):
        # some device is found during the scan
        name = device.getName()
        if name and name.startswith('MI'):  # is a Mi Band device
            self.device = device
            self.stop_scan()

    def on_scan_completed(self):
        if self.device:
            self.connect_gatt(self.device)  # connect to device

    def on_connection_state_change(self, status, state):
        if status == GATT_SUCCESS and state:  # connection established
            self.discover_services()  # discover what services a device offer
        else:  # disconnection or error
            self.alert_characteristic = None
            self.close_gatt()  # close current connection

    def on_services(self, status, services):
        # 0x2a06 is a standard code for "Alert Level" characteristic
        # https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.alert_level.xml
        self.alert_characteristic = services.search('2a06')
        self.alert(self.alert_characteristic)

    def alert(self, characteristic):
        self.write_characteristic(characteristic, [2])  # 2 is for "High Alert"


class AlertApp(App):

    def build(self):
        self.ble = None
        return Button(text='Press to Alert Mi', on_press=self.start_alert)

    def start_alert(self, *args, **kwargs):
        if not self.ble:
            self.ble = BLE()
        self.ble.start_alert()


if __name__ == '__main__':
    install_exception_handler()
    AlertApp().run()
