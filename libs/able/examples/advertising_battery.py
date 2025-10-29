"""Advertise battery level, that degrades every second."""
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label

from able import BluetoothDispatcher
from able import advertising

# Standard fully-qualified UUID for the Battery Service
BATTERY_SERVICE_UUID = "0000180f-0000-1000-8000-00805f9b34fb"


class BatteryAdvertiser(advertising.Advertiser):

    def on_advertising_started(self, advertising_set, tx_power, status):
        if status == advertising.Status.SUCCESS:
            print("Advertising is started successfully")
        else:
            print(f"Advertising start error status: {status}")

    def on_advertising_stopped(self, advertising_set):
        print("Advertising stopped")


class BatteryLabel(Label):
    """Widget to control advertiser and show current battery level."""

    def __init__(self):
        self._level = 0
        super().__init__(text="Waiting for advertising to start...")
        self.advertiser = BatteryAdvertiser(
            ble=BluetoothDispatcher(),
            data=self.construct_data(level=100),
            interval=advertising.Interval.MIN
        )
        self.advertiser.bind(on_advertising_started=self.on_started)  # bind to start of advertising
        self.advertiser.start()

    def on_started(self, advertiser, advertising_set, tx_power, status):
        if status == advertising.Status.SUCCESS:
            # Advertising is started - update battery level every second
            self.clock = Clock.schedule_interval(self.update_level, 1)

    def update_level(self, dt):
        level = self._level = (self._level - 1) % 101
        self.text = str(level)

        if level > 0:
            # Set new advertising data
            self.advertiser.data = self.construct_data(level)
        else:
            self.clock.cancel()
            # Stop advertising
            self.advertiser.stop()

    def construct_data(self, level):
        return advertising.AdvertiseData(
            advertising.DeviceName(),
            advertising.TXPowerLevel(),
            advertising.ServiceData(BATTERY_SERVICE_UUID, [level])
        )


class BatteryApp(App):

    def build(self):
        return BatteryLabel()


if __name__ == "__main__":
    BatteryApp().run()
