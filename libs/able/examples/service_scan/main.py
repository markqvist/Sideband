"""Start BLE devices scaning service."""
from able import (
    BluetoothDispatcher,
    require_bluetooth_enabled,
)
from jnius import autoclass
from kivy.app import App
from kivy.lang import Builder


kv = """
BoxLayout:
   Button:
      text: 'Start service'
      on_press: app.ble_dispatcher.start_service()
   Button:
      text: 'Stop service'
      on_press: app.ble_dispatcher.stop_service()
"""


class Dispatcher(BluetoothDispatcher):
    @property
    def service(self):
        return autoclass("test.able.scanservice.ServiceAble")

    @property
    def activity(self):
        return autoclass("org.kivy.android.PythonActivity").mActivity

    # Need to turn on the adapter and obtain permissions, before service is started
    @require_bluetooth_enabled
    def start_service(self):
        self.service.start(self.activity, "")
        App.get_running_app().stop()  # Can close the app, service will continue to run

    def stop_service(self):
        self.service.stop(self.activity)


class ServiceApp(App):
    def build(self):
        self.ble_dispatcher = Dispatcher()
        return Builder.load_string(kv)


if __name__ == "__main__":
    ServiceApp().run()
